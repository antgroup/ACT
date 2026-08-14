package org.actprotocol.quickstart.alipay;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.Collections;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

final class PaidResourceServer implements AutoCloseable {
    private final Config config;
    private final AlipayGateway gateway;
    private final BillSigner signer;
    private final DemoEventSink demoEvents;
    private final A402Codec codec = new A402Codec();
    private final ObjectMapper json = new ObjectMapper();
    private final Map<String, Models.BillRecord> bills = new ConcurrentHashMap<>();
    private final Map<String, String> fulfilledOccupancies = new ConcurrentHashMap<>();
    private final Map<String, String> deliveredRequests = new ConcurrentHashMap<>();
    private final Object deliveryLock = new Object();
    private final ExecutorService fulfillmentExecutor = Executors.newSingleThreadExecutor();
    private final ExecutorService serverExecutor = Executors.newCachedThreadPool();
    private HttpServer server;

    PaidResourceServer(Config config, AlipayGateway gateway, BillSigner signer) {
        this(config, gateway, signer, DemoEventSink.noop());
    }

    PaidResourceServer(
            Config config,
            AlipayGateway gateway,
            BillSigner signer,
            DemoEventSink demoEvents) {
        this.config = config;
        this.gateway = gateway;
        this.signer = signer;
        this.demoEvents = demoEvents;
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
        String requestFingerprint = requestFingerprint(exchange);
        String requestRef = digestRef("request|" + requestFingerprint);
        if (proofHeader == null || proofHeader.trim().isEmpty()) {
            demoEvents.emit("RESOURCE_REQUESTED", mapOf(
                    "resource_id", config.resourceId,
                    "goods_name", config.goodsName,
                    "http_method", exchange.getRequestMethod(),
                    "request_ref", requestRef));
            paymentRequired(exchange, "Payment Needed", true, null, requestFingerprint, requestRef);
            return;
        }

        try {
            demoEvents.emit("RESOURCE_REQUEST_RETRIED", mapOf(
                    "resource_id", config.resourceId,
                    "http_method", exchange.getRequestMethod(),
                    "request_ref", requestRef,
                    "request_fingerprint", requestFingerprint,
                    "result_summary", "original resource request retried with proof reference"));
            Models.PaymentProof proof = codec.decodePaymentProof(proofHeader);
            Models.VerificationResult verified = gateway.verify(proof);
            Models.BillRecord bill = verified.outTradeNo == null ? null : bills.get(verified.outTradeNo);
            String rejection = rejectionReason(proof, verified, bill, requestFingerprint);
            if (rejection != null) {
                demoEvents.emit("PROOF_REJECTED", mapOf(
                        "resource_id", config.resourceId,
                        "recovery_action", "DO_NOT_DELIVER · REISSUE_OR_RECONCILE",
                        "result_summary", rejection));
                paymentRequired(exchange, rejection, false, bill, requestFingerprint, requestRef);
                return;
            }

            String occupancyKey = String.join("|", config.actMethodId, verified.tradeNo,
                    verified.outTradeNo, verified.resourceId);
            String deliveryKey = String.join("|", config.actMethodId, verified.tradeNo,
                    requestFingerprint);
            boolean firstDelivery;
            synchronized (deliveryLock) {
                String priorFingerprint = fulfilledOccupancies.get(occupancyKey);
                if (priorFingerprint != null && !priorFingerprint.equals(requestFingerprint)) {
                    sendJson(exchange, 409, mapOf("error", "payment_replay_for_different_request"));
                    return;
                }
                firstDelivery = !deliveredRequests.containsKey(deliveryKey);
                fulfilledOccupancies.putIfAbsent(occupancyKey, requestFingerprint);
                deliveredRequests.putIfAbsent(deliveryKey, verified.resourceId);
            }

            String transactionRef = digestRef("trade|" + verified.tradeNo);
            String deliveryRef = digestRef("delivery|" + deliveryKey);
            demoEvents.emit("PAYMENT_VERIFIED", mapOf(
                    "amount", verified.amount,
                    "currency", config.currency,
                    "resource_id", verified.resourceId,
                    "order_ref", bill.orderRef,
                    "request_fingerprint", bill.requestFingerprint,
                    "transaction_ref", transactionRef,
                    "validation_mapping", "ACT 2.1 evidence <- Alipay payment.verify result",
                    "result_summary", "active and merchant bill checks passed"));
            sendJson(exchange, 200, mapOf(
                    "resource_id", config.resourceId,
                    "content", "This resource was released after Alipay payment verification.",
                    "trade_no", verified.tradeNo,
                    "idempotent_replay", !firstDelivery));
            demoEvents.emit("RESOURCE_DELIVERED", mapOf(
                    "resource_id", verified.resourceId,
                    "order_ref", bill.orderRef,
                    "request_fingerprint", bill.requestFingerprint,
                    "transaction_ref", transactionRef,
                    "delivery_ref", deliveryRef,
                    "idempotent_replay", !firstDelivery,
                    "payment_action", firstDelivery ? "ORIGINAL_PAYMENT" : "NO_NEW_PAYMENT",
                    "delivery_action", firstDelivery ? "COMMIT_DELIVERY" : "RETURN_PRIOR_RESULT",
                    "fulfillment_action", firstDelivery ? "SCHEDULE_CONFIRMATION" : "NOT_REPEATED",
                    "result_summary", firstDelivery
                            ? "paid resource delivered"
                            : "idempotent resource response"));

            if (firstDelivery) confirmFulfillmentAsync(
                    verified.tradeNo, transactionRef, deliveryRef, bill.orderRef);
        } catch (IllegalArgumentException exception) {
            demoEvents.emit("PROOF_REJECTED", mapOf(
                    "resource_id", config.resourceId,
                    "recovery_action", "DO_NOT_DELIVER · REQUEST_VALID_PROOF",
                    "result_summary", "invalid proof encoding or shape"));
            paymentRequired(exchange, "Invalid Payment-Proof", false, null, requestFingerprint, requestRef);
        } catch (Exception exception) {
            System.err.println("payment verification unavailable: " + safeMessage(exception));
            demoEvents.emit("VERIFICATION_UNAVAILABLE", mapOf(
                    "resource_id", config.resourceId,
                    "recovery_action", "RETRY_SAME_VERIFICATION · DO_NOT_DELIVER",
                    "result_summary", "official verification temporarily unavailable"));
            exchange.getResponseHeaders().set("Retry-After", "3");
            sendJson(exchange, 503, mapOf("error", "payment_verification_unavailable"));
        }
    }

    private String rejectionReason(
            Models.PaymentProof proof,
            Models.VerificationResult verified,
            Models.BillRecord bill,
            String requestFingerprint) {
        if (!verified.active) return "Payment proof is inactive";
        if (bill == null) return "Unknown merchant order";
        if (OffsetDateTime.now().isAfter(bill.expiresAt)) return "Payment requirement expired";
        if (!equal(verified.tradeNo, proof.protocol.tradeNo)) return "Trade number mismatch";
        if (!equal(verified.amount, bill.value.protocol.amount)) return "Amount mismatch";
        if (!equal(verified.resourceId, bill.value.protocol.resourceId)) return "Resource mismatch";
        if (!equal(verified.outTradeNo, bill.value.protocol.outTradeNo)) return "Order mismatch";
        if (!equal(bill.requestFingerprint, requestFingerprint)) return "Original request fingerprint mismatch";
        return null;
    }

    private void paymentRequired(
            HttpExchange exchange,
            String message,
            boolean emitInitialRequirement,
            Models.BillRecord existingBill,
            String requestFingerprint,
            String requestRef) throws IOException {
        try {
            Models.BillRecord record = existingBill == null
                    ? newBill(requestFingerprint, requestRef)
                    : existingBill;
            Models.PaymentNeeded bill = record.value;
            String encoded = codec.encodePaymentNeeded(record.value);
            exchange.getResponseHeaders().set("Payment-Needed", encoded);
            sendJson(exchange, 402, mapOf(
                    "error", "Payment Needed",
                    "message", message,
                    "resourceId", config.resourceId));
            if (emitInitialRequirement) {
                demoEvents.emit("PAYMENT_REQUIRED", mapOf(
                        "amount", bill.protocol.amount,
                        "currency", bill.protocol.currency,
                        "resource_id", bill.protocol.resourceId,
                        "request_ref", record.requestRef,
                        "request_fingerprint", record.requestFingerprint,
                        "order_ref", record.orderRef,
                        "profile_mapping", "ALIPAY_PRODUCT_PAYLOAD_TO_ACT_2_1_EVIDENCE",
                        "goods_name", bill.method.goodsName,
                        "seller_name", bill.method.sellerName));
            }
        } catch (Exception exception) {
            System.err.println("cannot create payment requirement: " + safeMessage(exception));
            sendJson(exchange, 500, mapOf("error", "payment_requirement_unavailable"));
        }
    }

    private Models.BillRecord newBill(String requestFingerprint, String requestRef) throws Exception {
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
        String orderRef = digestRef("order|" + bill.protocol.outTradeNo);
        Models.BillRecord record = new Models.BillRecord(
                bill, expiresAt, requestFingerprint, requestRef, orderRef);
        bills.put(bill.protocol.outTradeNo, record);
        return record;
    }

    private void confirmFulfillmentAsync(
            String tradeNo,
            String transactionRef,
            String deliveryRef,
            String orderRef) {
        fulfillmentExecutor.submit(() -> {
            try {
                gateway.confirmFulfillment(tradeNo);
                System.out.println("fulfillment confirmed for trade " + redact(tradeNo));
                demoEvents.emit("FULFILLMENT_CONFIRMED", mapOf(
                        "resource_id", config.resourceId,
                        "order_ref", orderRef,
                        "transaction_ref", transactionRef,
                        "delivery_ref", deliveryRef,
                        "fulfillment_ref", digestRef("fulfillment|" + tradeNo),
                        "product_fulfillment_status", "CONFIRMED",
                        "result_summary", "seller fulfillment confirmed"));
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

    private static String requestFingerprint(HttpExchange exchange) {
        try {
            String host = exchange.getRequestHeaders().getFirst("Host");
            if (host == null || host.trim().isEmpty()) host = "127.0.0.1";
            URI source = URI.create("http://" + host + exchange.getRequestURI().toString());
            String scheme = source.getScheme().toLowerCase(Locale.ROOT);
            String normalizedHost = source.getHost().toLowerCase(Locale.ROOT);
            int port = source.getPort();
            if (("http".equals(scheme) && port == 80) || ("https".equals(scheme) && port == 443)) port = -1;
            String path = source.getRawPath();
            if (path == null || path.isEmpty()) path = "/";
            URI normalized = new URI(
                    scheme, source.getUserInfo(), normalizedHost, port, path, source.getRawQuery(), null);
            String bodyHash = sha256Base64Url(new byte[0]);
            String material = exchange.getRequestMethod().toUpperCase(Locale.ROOT) + "\n"
                    + normalized.toASCIIString() + "\n\n" + bodyHash;
            return "sha-256:" + sha256Base64Url(material.getBytes(StandardCharsets.UTF_8));
        } catch (Exception exception) {
            throw new IllegalArgumentException("Cannot canonicalize the paid-resource request", exception);
        }
    }

    private static String digestRef(String value) {
        return "sha-256:" + sha256Base64Url(value.getBytes(StandardCharsets.UTF_8));
    }

    private static String sha256Base64Url(byte[] value) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(value);
            return Base64.getUrlEncoder().withoutPadding().encodeToString(digest);
        } catch (Exception exception) {
            throw new IllegalStateException("SHA-256 is unavailable", exception);
        }
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
        demoEvents.close();
    }
}
