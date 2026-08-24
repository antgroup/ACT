package org.actprotocol.quickstart.alipay;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

final class ConfigTest {
    @Test
    void acceptsCurrentOfficialAmountBoundaries() {
        assertEquals("0.01", config("0.01", "cny").amount);
        assertEquals("50.00", config("50.00", "CNY").amount);
        assertEquals("CNY", config("1", "cny").currency);
    }

    @Test
    void rejectsUnsupportedAmountsAndCurrencies() {
        assertThrows(IllegalArgumentException.class, () -> config("0.001", "CNY"));
        assertThrows(IllegalArgumentException.class, () -> config("50.01", "CNY"));
        assertThrows(IllegalArgumentException.class, () -> config("1e-2", "CNY"));
        assertThrows(IllegalArgumentException.class, () -> config("0.01", "USD"));
    }

    private static Config config(String amount, String currency) {
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
                amount,
                currency,
                8080,
                10);
    }
}
