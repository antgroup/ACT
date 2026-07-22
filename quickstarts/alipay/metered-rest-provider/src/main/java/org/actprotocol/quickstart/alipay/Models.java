package org.actprotocol.quickstart.alipay;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.OffsetDateTime;

final class Models {
    private Models() {}

    static final class PaymentNeeded {
        public BillProtocol protocol;
        public BillMethod method;
    }

    static final class BillProtocol {
        @JsonProperty("out_trade_no") public String outTradeNo;
        public String amount;
        public String currency;
        @JsonProperty("resource_id") public String resourceId;
        @JsonProperty("pay_before") public String payBefore;
        @JsonProperty("seller_signature") public String sellerSignature;
        @JsonProperty("seller_sign_type") public String sellerSignType;
        @JsonProperty("seller_unique_id") public String sellerUniqueId;
    }

    static final class BillMethod {
        @JsonProperty("seller_name") public String sellerName;
        @JsonProperty("seller_id") public String sellerId;
        @JsonProperty("seller_app_id") public String sellerAppId;
        @JsonProperty("goods_name") public String goodsName;
        @JsonProperty("seller_unique_id_key") public String sellerUniqueIdKey;
        @JsonProperty("service_id") public String serviceId;
    }

    static final class PaymentProof {
        public ProofProtocol protocol;
        public ProofMethod method;
    }

    static final class ProofProtocol {
        @JsonProperty("payment_proof") public String paymentProof;
        @JsonProperty("trade_no") public String tradeNo;
    }

    static final class ProofMethod {
        @JsonProperty("client_session") public String clientSession;
    }

    static final class VerificationResult {
        final boolean active;
        final String amount;
        final String outTradeNo;
        final String tradeNo;
        final String resourceId;

        VerificationResult(
                boolean active,
                String amount,
                String outTradeNo,
                String tradeNo,
                String resourceId) {
            this.active = active;
            this.amount = amount;
            this.outTradeNo = outTradeNo;
            this.tradeNo = tradeNo;
            this.resourceId = resourceId;
        }
    }

    static final class BillRecord {
        final PaymentNeeded value;
        final OffsetDateTime expiresAt;

        BillRecord(PaymentNeeded value, OffsetDateTime expiresAt) {
            this.value = value;
            this.expiresAt = expiresAt;
        }
    }
}
