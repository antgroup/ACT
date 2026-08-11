package org.actprotocol.quickstart.alipay;

import com.alipay.api.AlipayClient;
import com.alipay.api.AlipayConfig;
import com.alipay.api.AlipayRequest;
import com.alipay.api.AlipayResponse;
import com.alipay.api.DefaultAlipayClient;
import com.alipay.api.domain.AlipayAipayAgentFulfillmentConfirmModel;
import com.alipay.api.request.AlipayAipayAgentFulfillmentConfirmRequest;
import com.alipay.api.request.AlipayAipayAgentPaymentVerifyRequest;
import com.alipay.api.response.AlipayAipayAgentFulfillmentConfirmResponse;
import com.alipay.api.response.AlipayAipayAgentPaymentVerifyResponse;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.LinkedHashMap;
import java.util.Map;

final class OfficialAlipayGateway implements AlipayGateway {
    private final AlipayClient client;
    private final String appAuthToken;
    private final ObjectMapper json = new ObjectMapper();

    OfficialAlipayGateway(Config config) throws Exception {
        AlipayConfig sdkConfig = new AlipayConfig();
        sdkConfig.setServerUrl(config.gatewayUrl);
        sdkConfig.setAppId(config.appId);
        sdkConfig.setPrivateKey(config.privateKey);
        sdkConfig.setFormat("json");
        sdkConfig.setAlipayPublicKey(config.alipayPublicKey);
        sdkConfig.setCharset("UTF-8");
        sdkConfig.setSignType("RSA2");
        this.client = new DefaultAlipayClient(sdkConfig);
        this.appAuthToken = config.appAuthToken;
    }

    @Override
    public Models.VerificationResult verify(Models.PaymentProof proof) throws Exception {
        AlipayAipayAgentPaymentVerifyRequest request = new AlipayAipayAgentPaymentVerifyRequest();
        Map<String, String> content = new LinkedHashMap<>();
        content.put("trade_no", proof.protocol.tradeNo);
        content.put("payment_proof", proof.protocol.paymentProof);
        content.put("client_session", proof.method.clientSession);
        // The public API requires client_session. Some generated SDK models lag that field,
        // so use the SDK request's documented biz_content escape hatch without changing it.
        request.setBizContent(json.writeValueAsString(content));
        AlipayAipayAgentPaymentVerifyResponse response = execute(request);
        if (!response.isSuccess()) {
            throw new IllegalStateException(
                    "Alipay payment.verify failed: " + response.getCode() + " " + response.getSubMsg());
        }
        return new Models.VerificationResult(
                Boolean.TRUE.equals(response.getActive()),
                response.getAmount(),
                response.getOutTradeNo(),
                response.getTradeNo(),
                response.getResourceId());
    }

    @Override
    public void confirmFulfillment(String tradeNo) throws Exception {
        AlipayAipayAgentFulfillmentConfirmModel model =
                new AlipayAipayAgentFulfillmentConfirmModel();
        model.setTradeNo(tradeNo);
        AlipayAipayAgentFulfillmentConfirmRequest request =
                new AlipayAipayAgentFulfillmentConfirmRequest();
        request.setBizModel(model);
        AlipayAipayAgentFulfillmentConfirmResponse response = execute(request);
        if (!response.isSuccess()) {
            throw new IllegalStateException(
                    "Alipay fulfillment.confirm failed: "
                            + response.getCode() + " " + response.getSubMsg());
        }
    }

    private <T extends AlipayResponse> T execute(AlipayRequest<T> request) throws Exception {
        if (appAuthToken == null || appAuthToken.isEmpty()) return client.execute(request);
        return client.execute(request, null, appAuthToken);
    }
}
