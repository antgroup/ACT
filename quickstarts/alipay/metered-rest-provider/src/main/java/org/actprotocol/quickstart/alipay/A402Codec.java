package org.actprotocol.quickstart.alipay;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

final class A402Codec {
    private static final int MAX_HEADER_LENGTH = 32 * 1024;
    private final ObjectMapper json = new ObjectMapper();

    String encodePaymentNeeded(Models.PaymentNeeded value) throws Exception {
        byte[] bytes = json.writeValueAsBytes(value);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }

    Models.PaymentNeeded decodePaymentNeeded(String value) throws Exception {
        requireHeader(value);
        byte[] bytes = Base64.getUrlDecoder().decode(value);
        return json.readValue(bytes, Models.PaymentNeeded.class);
    }

    Models.PaymentProof decodePaymentProof(String value) throws Exception {
        requireHeader(value);
        byte[] bytes = Base64.getDecoder().decode(value);
        Models.PaymentProof proof = json.readValue(bytes, Models.PaymentProof.class);
        if (proof.protocol == null
                || blank(proof.protocol.paymentProof)
                || blank(proof.protocol.tradeNo)
                || proof.method == null
                || blank(proof.method.clientSession)) {
            throw new IllegalArgumentException("Payment-Proof is missing required fields");
        }
        return proof;
    }

    String encodePaymentProofForTest(Models.PaymentProof value) throws Exception {
        return Base64.getEncoder().encodeToString(json.writeValueAsBytes(value));
    }

    static String signingContent(Models.PaymentNeeded bill) {
        Map<String, String> fields = new TreeMap<>();
        fields.put("amount", bill.protocol.amount);
        fields.put("currency", bill.protocol.currency);
        fields.put("goods_name", bill.method.goodsName);
        fields.put("out_trade_no", bill.protocol.outTradeNo);
        fields.put("pay_before", bill.protocol.payBefore);
        fields.put("resource_id", bill.protocol.resourceId);
        fields.put("seller_id", bill.method.sellerId);
        fields.put("service_id", bill.method.serviceId);
        return fields.entrySet().stream()
                .map(entry -> entry.getKey() + "=" + entry.getValue())
                .collect(Collectors.joining("&"));
    }

    static String utf8(String value) {
        return new String(value.getBytes(StandardCharsets.UTF_8), StandardCharsets.UTF_8);
    }

    private static void requireHeader(String value) {
        if (blank(value)) throw new IllegalArgumentException("payment header is empty");
        if (value.length() > MAX_HEADER_LENGTH) {
            throw new IllegalArgumentException("payment header is too large");
        }
    }

    private static boolean blank(String value) {
        return value == null || value.trim().isEmpty();
    }
}
