package org.actprotocol.quickstart.alipay;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

final class A402CodecTest {
    @Test
    void encodesPaymentNeededAsBase64UrlJson() throws Exception {
        Models.PaymentNeeded bill = bill();
        A402Codec codec = new A402Codec();
        String encoded = codec.encodePaymentNeeded(bill);
        Models.PaymentNeeded decoded = codec.decodePaymentNeeded(encoded);

        assertEquals("ORDER_1", decoded.protocol.outTradeNo);
        assertEquals("ACT resource", decoded.method.goodsName);
    }

    @Test
    void signingContentUsesOfficialSortedFieldSet() {
        assertEquals(
                "amount=0.01&currency=CNY&goods_name=ACT resource&out_trade_no=ORDER_1"
                        + "&pay_before=2026-07-22T12:00:00+08:00&resource_id=resource-1"
                        + "&seller_id=2088test&service_id=service-1",
                A402Codec.signingContent(bill()));
    }

    private static Models.PaymentNeeded bill() {
        Models.PaymentNeeded bill = new Models.PaymentNeeded();
        bill.protocol = new Models.BillProtocol();
        bill.method = new Models.BillMethod();
        bill.protocol.outTradeNo = "ORDER_1";
        bill.protocol.amount = "0.01";
        bill.protocol.currency = "CNY";
        bill.protocol.resourceId = "resource-1";
        bill.protocol.payBefore = "2026-07-22T12:00:00+08:00";
        bill.method.goodsName = "ACT resource";
        bill.method.sellerId = "2088test";
        bill.method.serviceId = "service-1";
        return bill;
    }
}
