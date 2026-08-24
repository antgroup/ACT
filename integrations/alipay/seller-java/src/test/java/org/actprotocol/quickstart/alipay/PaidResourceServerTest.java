package org.actprotocol.quickstart.alipay;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

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
        String response = read(paid.getInputStream());
        assertTrue(response.contains("released after Alipay payment verification"));
        assertTrue(response.contains("transaction_ref"));
        assertTrue(!response.contains("2026072200000001"));
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

        HttpURLConnection rejected = request(proof("2026072200000002"));
        assertEquals(409, rejected.getResponseCode());
        assertEquals(null, rejected.getHeaderField("Payment-Needed"));
    }

    @Test
    void repeatedProofReturnsPriorResourceWithoutDuplicateFulfillment() throws Exception {
        // A402-TEST-007: repeated proof cannot duplicate non-idempotent fulfillment.
        MutableGateway gateway = new MutableGateway();
        server = new PaidResourceServer(testConfig(), gateway, content -> "test-signature");
        server.start();

        HttpURLConnection unpaid = request(null);
        assertEquals(402, unpaid.getResponseCode());
        Models.PaymentNeeded bill = new A402Codec().decodePaymentNeeded(
                unpaid.getHeaderField("Payment-Needed"));
        gateway.result = new Models.VerificationResult(
                true,
                bill.protocol.amount,
                bill.protocol.outTradeNo,
                "2026072200000003",
                bill.protocol.resourceId);
        String proof = proof("2026072200000003");

        assertEquals(200, request(proof).getResponseCode());
        assertTrue(gateway.confirmed.await(2, TimeUnit.SECONDS));
        HttpURLConnection replay = request(proof);
        assertEquals(200, replay.getResponseCode());
        assertTrue(read(replay.getInputStream()).contains("\"idempotent_replay\":true"));
        assertEquals(1, gateway.confirmCalls.get());
    }

    @Test
    void proofCannotBeReusedForAChangedOriginalRequest() throws Exception {
        MutableGateway gateway = new MutableGateway();
        server = new PaidResourceServer(testConfig(), gateway, content -> "test-signature");
        server.start();

        HttpURLConnection unpaid = request(null);
        assertEquals(402, unpaid.getResponseCode());
        Models.PaymentNeeded bill = new A402Codec().decodePaymentNeeded(
                unpaid.getHeaderField("Payment-Needed"));
        gateway.result = new Models.VerificationResult(
                true,
                bill.protocol.amount,
                bill.protocol.outTradeNo,
                "2026072200000004",
                bill.protocol.resourceId);

        assertEquals(409, request("/paid-resource?variant=other", proof("2026072200000004")).getResponseCode());
        assertEquals(0, gateway.confirmCalls.get());
    }

    @Test
    void repeatedUnpaidRequestReusesTheActiveRequirement() throws Exception {
        MutableGateway gateway = new MutableGateway();
        server = new PaidResourceServer(testConfig(), gateway, content -> "test-signature");
        server.start();

        HttpURLConnection first = request(null);
        assertEquals(402, first.getResponseCode());
        String firstRequirement = first.getHeaderField("Payment-Needed");
        HttpURLConnection second = request(null);
        assertEquals(402, second.getResponseCode());
        assertEquals(firstRequirement, second.getHeaderField("Payment-Needed"));
    }

    @Test
    void validMatchingProofStillDeliversAfterThePaymentDeadline() throws Exception {
        MutableGateway gateway = new MutableGateway();
        server = new PaidResourceServer(testConfig(0), gateway, content -> "test-signature");
        server.start();

        HttpURLConnection unpaid = request(null);
        assertEquals(402, unpaid.getResponseCode());
        Models.PaymentNeeded bill = new A402Codec().decodePaymentNeeded(
                unpaid.getHeaderField("Payment-Needed"));
        gateway.result = new Models.VerificationResult(
                true,
                bill.protocol.amount,
                bill.protocol.outTradeNo,
                "2026072200000005",
                bill.protocol.resourceId);

        HttpURLConnection paid = request(proof("2026072200000005"));
        assertEquals(200, paid.getResponseCode());
        assertTrue(gateway.confirmed.await(2, TimeUnit.SECONDS));
    }

    @Test
    void inactiveProofGetsAFreshRequirementWithoutReusingTheExpiredBill() throws Exception {
        MutableGateway gateway = new MutableGateway();
        server = new PaidResourceServer(testConfig(0), gateway, content -> "test-signature");
        server.start();

        HttpURLConnection unpaid = request(null);
        assertEquals(402, unpaid.getResponseCode());
        String originalRequirement = unpaid.getHeaderField("Payment-Needed");
        Models.PaymentNeeded bill = new A402Codec().decodePaymentNeeded(originalRequirement);
        gateway.result = new Models.VerificationResult(
                false,
                bill.protocol.amount,
                bill.protocol.outTradeNo,
                "2026072200000006",
                bill.protocol.resourceId);

        HttpURLConnection rejected = request(proof("2026072200000006"));
        assertEquals(402, rejected.getResponseCode());
        assertNotNull(rejected.getHeaderField("Payment-Needed"));
        assertTrue(!originalRequirement.equals(rejected.getHeaderField("Payment-Needed")));
        assertEquals(0, gateway.confirmCalls.get());
    }

    private HttpURLConnection request(String proof) throws Exception {
        return request("/paid-resource", proof);
    }

    private HttpURLConnection request(String path, String proof) throws Exception {
        URL url = new URL("http://127.0.0.1:" + server.port() + path);
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
        return testConfig(10);
    }

    private static Config testConfig(int billValidityMinutes) {
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
                billValidityMinutes);
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
        final AtomicInteger confirmCalls = new AtomicInteger();

        @Override
        public Models.VerificationResult verify(Models.PaymentProof proof) {
            return result;
        }

        @Override
        public void confirmFulfillment(String tradeNo) {
            confirmCalls.incrementAndGet();
            confirmedTradeNo = tradeNo;
            confirmed.countDown();
        }
    }
}
