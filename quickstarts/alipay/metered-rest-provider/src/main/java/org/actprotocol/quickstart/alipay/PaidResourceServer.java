package org.actprotocol.quickstart.alipay;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

final class PaidResourceServer implements AutoCloseable {
    private final Config config;
    private final AlipayGateway gateway;
    private final BillSigner signer;
    private final A402Codec codec = new A402Codec();
    private final ObjectMapper json = new ObjectMapper();
    private final Map<String, Models.BillRecord> bills = new ConcurrentHashMap<>();
    private final Map<String, String> fulfilledTrades = new ConcurrentHashMap<>();
    private final ExecutorService fulfillmentExecutor = Executors.newSingleThreadExecutor();
    private final ExecutorService serverExecutor = Executors.newCachedThreadPool();
    private HttpServer server;

    PaidResourceServer(Config config, AlipayGateway gateway, BillSigner signer) {
        this.config = config;
        this.gateway = gateway;
        this.signer = signer;
    }

    void start() throws IOException {
        server = HttpServer.create(new InetSocketAddress(config.port), 0);
        server.createContext("/health", this::health);
        server.createContext("/paid-resource", this::paidResource);
        server.setExecutor(serverExecutor);
        server.start();
    }

    int port() {
        if (server == null) throw new IllegalStateException("server is not started");
        return server.getAddress().getPort();
    }

    private void health(HttpExchange exchange) throws IOException {
        if (!"GET".equals(exchange.getRequestMethod())) {
            sendJson(exchange, 405, mapOf("error", "method_not_allowed"));
            return;
        }
        sendJson(exchange, 200, mapOf("status", "ok", "mode", "alipay-sandbox-or-openapi"));
    }

    private void paidResource(HttpExchange exchange) throws IOException {
        if (!"GET".equals(exchange.getRequestMethod())) {
            sendJson(exchange, 405, mapOf("error", "method_not_allowed"));
            return;
        }

        String proofHeader = exchange.getRequestHeaders().getFirst("Payment-Proof");
        if (proofHeader == null || proofHeader.trim().isEmpty()) {
            paymentRequired(exchange, "Payment Needed");
            return;
        }

        try {
            Models.PaymentProof proof = codec.decodePaymentProof(proofHeader);
            Models.VerificationResult verified = gateway.verify(proof);
            Models.BillRecord bill = verified.outTradeNo == null ? null : bills.get(verified.outTradeNo);
            String rejection = rejectionReason(proof, verified, bill);
            if (rejection != null) {
                paymentRequired(exchange, rejection);
                return;
            }

            String priorResource = fulfilledTrades.putIfAbsent(verified.tradeNo, verified.resourceId);
            if (priorResource != null && !priorResource.equals(verified.resourceId)) {
                sendJson(exchange, 409, mapOf("error", "payment_replay_for_different_resource"));
                return;
            }

            boolean firstDelivery = priorResource == null;
            sendJson(exchange, 200, mapOf(
                    "resource_id", config.resourceId,
                    "content", "This resource was released after Alipay payment verification.",
                    "trade_no", verified.tradeNo,
                    "idempotent_replay", !firstDelivery));

            if (firstDelivery) confirmFulfillmentAsync(verified.tradeNo);
        } catch (IllegalArgumentException exception) {
            paymentRequired(exchange, "Invalid Payment-Proof");
        } catch (Exception exception) {
            System.err.println("payment verification unavailable: " + safeMessage(exception));
            exchange.getResponseHeaders().set("Retry-After", "3");
            sendJson(exchange, 503, mapOf("error", "payment_verification_unavailable"));
        }
    }

    private String rejectionReason(
            Models.PaymentProof proof,
            Models.VerificationResult verified,
            Models.BillRecord bill) {
        if (!verified.active) return "Payment proof is inactive";
        if (bill == null) return "Unknown merchant order";
        if (OffsetDateTime.now().isAfter(bill.expiresAt)) return "Payment requirement expired";
        if (!equal(verified.tradeNo, proof.protocol.tradeNo)) return "Trade number mismatch";
        if (!equal(verified.amount, bill.value.protocol.amount)) return "Amount mismatch";
        if (!equal(verified.resourceId, bill.value.protocol.resourceId)) return "Resource mismatch";
        if (!equal(verified.outTradeNo, bill.value.protocol.outTradeNo)) return "Order mismatch";
        return null;
    }

    private void paymentRequired(HttpExchange exchange, String message) throws IOException {
        try {
            Models.PaymentNeeded bill = newBill();
            String encoded = codec.encodePaymentNeeded(bill);
            exchange.getResponseHeaders().set("Payment-Needed", encoded);
            sendJson(exchange, 402, mapOf(
                    "error", "Payment Needed",
                    "message", message,
                    "resourceId", config.resourceId));
        } catch (Exception exception) {
            System.err.println("cannot create payment requirement: " + safeMessage(exception));
            sendJson(exchange, 500, mapOf("error", "payment_requirement_unavailable"));
        }
    }

    private Models.PaymentNeeded newBill() throws Exception {
        OffsetDateTime expiresAt = OffsetDateTime.now(ZoneOffset.ofHours(8))
                .plusMinutes(config.billValidityMinutes);
        Models.PaymentNeeded bill = new Models.PaymentNeeded();
        bill.protocol = new Models.BillProtocol();
        bill.method = new Models.BillMethod();

        bill.protocol.outTradeNo = "ACT_" + UUID.randomUUID().toString().replace("-", "");
        bill.protocol.amount = config.amount;
        bill.protocol.currency = config.currency;
        bill.protocol.resourceId = config.resourceId;
        bill.protocol.payBefore = expiresAt.format(DateTimeFormatter.ISO_OFFSET_DATE_TIME);
        bill.protocol.sellerSignType = "RSA2";
        bill.protocol.sellerUniqueId = config.sellerId;

        bill.method.sellerName = config.sellerName;
        bill.method.sellerId = config.sellerId;
        bill.method.sellerAppId = config.appId;
        bill.method.goodsName = config.goodsName;
        bill.method.sellerUniqueIdKey = "seller_id";
        bill.method.serviceId = config.serviceId;

        bill.protocol.sellerSignature = signer.sign(A402Codec.signingContent(bill));
        bills.put(bill.protocol.outTradeNo, new Models.BillRecord(bill, expiresAt));
        return bill;
    }

    private void confirmFulfillmentAsync(String tradeNo) {
        fulfillmentExecutor.submit(() -> {
            try {
                gateway.confirmFulfillment(tradeNo);
                System.out.println("fulfillment confirmed for trade " + redact(tradeNo));
            } catch (Exception exception) {
                // A production implementation must persist this job and retry with backoff.
                System.err.println(
                        "fulfillment confirmation failed for trade " + redact(tradeNo)
                                + ": " + safeMessage(exception));
            }
        });
    }

    private void sendJson(HttpExchange exchange, int status, Map<String, Object> body)
            throws IOException {
        byte[] bytes = json.writeValueAsBytes(body);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.getResponseHeaders().set("Cache-Control", "no-store");
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream output = exchange.getResponseBody()) {
            output.write(bytes);
        }
    }

    private static Map<String, Object> mapOf(Object... pairs) {
        Map<String, Object> map = new LinkedHashMap<>();
        for (int index = 0; index < pairs.length; index += 2) {
            map.put(String.valueOf(pairs[index]), pairs[index + 1]);
        }
        return Collections.unmodifiableMap(map);
    }

    private static boolean equal(String left, String right) {
        return left != null && left.equals(right);
    }

    private static String redact(String value) {
        if (value == null || value.length() < 8) return "***";
        return value.substring(0, 4) + "…" + value.substring(value.length() - 4);
    }

    private static String safeMessage(Exception exception) {
        String message = exception.getMessage();
        return message == null ? exception.getClass().getSimpleName() : message;
    }

    @Override
    public void close() {
        if (server != null) server.stop(0);
        serverExecutor.shutdownNow();
        fulfillmentExecutor.shutdownNow();
    }
}
