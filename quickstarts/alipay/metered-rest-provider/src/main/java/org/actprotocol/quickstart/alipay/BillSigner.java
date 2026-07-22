package org.actprotocol.quickstart.alipay;

import com.alipay.api.internal.util.AlipaySignature;

interface BillSigner {
    String sign(String content) throws Exception;

    final class Rsa2 implements BillSigner {
        private final String privateKey;

        Rsa2(String privateKey) {
            this.privateKey = privateKey;
        }

        @Override
        public String sign(String content) throws Exception {
            return AlipaySignature.rsaSign(content, privateKey, "UTF-8", "RSA2");
        }
    }
}
