package org.actprotocol.quickstart.alipay;

interface AlipayGateway {
    Models.VerificationResult verify(Models.PaymentProof proof) throws Exception;

    void confirmFulfillment(String tradeNo) throws Exception;
}
