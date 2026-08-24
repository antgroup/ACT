package org.actprotocol.quickstart.alipay;

import com.alipay.api.request.AlipayAipayAgentPaymentVerifyRequest;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

final class OfficialAlipayGatewayTest {
    @Test
    void verifyRequestPreservesEveryOfficialProofField() throws Exception {
        Models.PaymentProof proof = new Models.PaymentProof();
        proof.protocol = new Models.ProofProtocol();
        proof.method = new Models.ProofMethod();
        proof.protocol.tradeNo = "trade-001";
        proof.protocol.paymentProof = "opaque-proof";
        proof.method.clientSession = "buyer-session";

        ObjectMapper json = new ObjectMapper();
        AlipayAipayAgentPaymentVerifyRequest request =
                OfficialAlipayGateway.createVerifyRequest(proof, json);
        JsonNode content = json.readTree(request.getBizContent());

        assertEquals(3, content.size());
        assertEquals("trade-001", content.path("trade_no").asText());
        assertEquals("opaque-proof", content.path("payment_proof").asText());
        assertEquals("buyer-session", content.path("client_session").asText());
    }
}
