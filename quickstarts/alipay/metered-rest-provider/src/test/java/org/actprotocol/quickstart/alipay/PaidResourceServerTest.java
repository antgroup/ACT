package org.actprotocol.quickstart.alipay;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

final class PaidResourceServerTest {
    private PaidResourceServer server;

    @AfterEach
    void stopServer() {
        if (server != null) server.close();
    }

    @Test
    void requiresThenVerifiesPaymentAndConfirmsFulfillment() throws Exception {
        MutableGateway gateway = new MutableGateway();
        server = new PaidResourceServer(testConfig(), gateway, content -> "test-signature");
        server.start();

        HttpURLConnection unpaid = request(null);
        assertEquals(402, unpaid.getResponseCode());
        String paymentNeeded = unpaid.getHeaderField("Payment-Needed");
        assertNotNull(paymentNeeded);
        Models.PaymentNeeded bill = new A402Codec().decodePaymentNeeded(paymentNeeded);

        gateway.result = new Models.VerificationResult(
                true,
                bill.protocol.amount,
                bill.protocol.outTradeNo,
                "2026072200000001",
                bill.protocol.resourceId);
        String proof = proof("2026072200000001");
        HttpURLConnection paid = request(proof);

        assertEquals(200, paid.getResponseCode());
        assertTrue(read(paid.getInputStream()).contains("released after Alipay payment verification"));
        assertTrue(gateway.confirmed.await(2, TimeUnit.SECONDS));
        assertEquals("2026072200000001", gateway.confirmedTradeNo);
    }

    @Test
    void rejectsVerifiedFactsThatDoNotMatchOriginalBill() throws Exception {
        MutableGateway gateway = new MutableGateway();
        server = new PaidResourceServer(testConfig(), gateway, content -> "test-signature");
        server.start();

        HttpURLConnection unpaid = request(null);
        assertEquals(402, unpaid.getResponseCode());
        Models.PaymentNeeded bill = new A402Codec().decodePaymentNeeded(
                unpaid.getHeaderField("Payment-Needed"));
        gateway.result = new Models.VerificationResult(
                true,
                "999.00",
                bill.protocol.outTradeNo,
                "2026072200000002",
                bill.protocol.resourceId);

        assertEquals(402, request(proof("2026072200000002")).getResponseCode());
    }

    private HttpURLConnection request(String proof) throws Exception {
        URL url = new URL("http://127.0.0.1:" + server.port() + "/paid-resource");
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
        if (proof != null) connection.setRequestProperty("Payment-Proof", proof);
        return connection;
    }

    private static String proof(String tradeNo) throws Exception {
        Models.PaymentProof proof = new Models.PaymentProof();
        proof.protocol = new Models.ProofProtocol();
        proof.method = new Models.ProofMethod();
        proof.protocol.paymentProof = "opaque-official-proof";
        proof.protocol.tradeNo = tradeNo;
        proof.method.clientSession = "test-client-session";
        return new A402Codec().encodePaymentProofForTest(proof);
    }

    private static Config testConfig() {
        return new Config(
                "https://example.invalid",
                "app-test",
                "private-key",
                "public-key",
                "",
                "2088test",
                "Test merchant",
                "service-1",
                "ACT resource",
                "resource-1",
                "0.01",
                "CNY",
                0,
                10);
    }

    private static String read(InputStream input) throws Exception {
        byte[] buffer = new byte[4096];
        int count = input.read(buffer);
        return new String(buffer, 0, count, StandardCharsets.UTF_8);
    }

    private static final class MutableGateway implements AlipayGateway {
        volatile Models.VerificationResult result;
        volatile String confirmedTradeNo;
        final CountDownLatch confirmed = new CountDownLatch(1);

        @Override
        public Models.VerificationResult verify(Models.PaymentProof proof) {
            return result;
        }

        @Override
        public void confirmFulfillment(String tradeNo) {
            confirmedTradeNo = tradeNo;
            confirmed.countDown();
        }
    }
}
