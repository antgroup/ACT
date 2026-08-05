package org.actprotocol.quickstart.alipay;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Map;

final class Config {
    final String gatewayUrl;
    final String appId;
    final String privateKey;
    final String alipayPublicKey;
    final String appAuthToken;
    final String sellerId;
    final String sellerName;
    final String serviceId;
    final String goodsName;
    final String resourceId;
    final String amount;
    final String currency;
    final int port;
    final int billValidityMinutes;

    Config(
            String gatewayUrl,
            String appId,
            String privateKey,
            String alipayPublicKey,
            String appAuthToken,
            String sellerId,
            String sellerName,
            String serviceId,
            String goodsName,
            String resourceId,
            String amount,
            String currency,
            int port,
            int billValidityMinutes) {
        this.gatewayUrl = gatewayUrl;
        this.appId = appId;
        this.privateKey = privateKey;
        this.alipayPublicKey = alipayPublicKey;
        this.appAuthToken = appAuthToken;
        this.sellerId = sellerId;
        this.sellerName = sellerName;
        this.serviceId = serviceId;
        this.goodsName = goodsName;
        this.resourceId = resourceId;
        this.amount = amount;
        this.currency = currency;
        this.port = port;
        this.billValidityMinutes = billValidityMinutes;
    }

    static Config fromEnvironment() throws IOException {
        Map<String, String> env = System.getenv();
        return new Config(
                required(env, "ALIPAY_GATEWAY_URL"),
                required(env, "ALIPAY_APP_ID"),
                secret(env, "ALIPAY_PRIVATE_KEY", "ALIPAY_PRIVATE_KEY_FILE"),
                secret(
                        env,
                        "ALIPAY_ALIPAY_PUBLIC_KEY",
                        "ALIPAY_ALIPAY_PUBLIC_KEY_FILE",
                        "ALIPAY_PUBLIC_KEY",
                        "ALIPAY_PUBLIC_KEY_FILE"),
                env.getOrDefault("ALIPAY_APP_AUTH_TOKEN", ""),
                required(env, "ALIPAY_SELLER_ID"),
                required(env, "ALIPAY_SELLER_NAME"),
                required(env, "ALIPAY_SERVICE_ID"),
                required(env, "ALIPAY_GOODS_NAME"),
                required(env, "ALIPAY_RESOURCE_ID"),
                required(env, "ALIPAY_AMOUNT"),
                env.getOrDefault("ALIPAY_CURRENCY", "CNY"),
                integer(env, "ALIPAY_PORT", 8080),
                integer(env, "ALIPAY_BILL_VALIDITY_MINUTES", 10));
    }

    private static String required(Map<String, String> env, String name) {
        String value = env.get(name);
        if (value == null || value.trim().isEmpty()) {
            throw new IllegalArgumentException("Missing required environment variable: " + name);
        }
        return value.trim();
    }

    private static String secret(Map<String, String> env, String directName, String fileName)
            throws IOException {
        String direct = env.get(directName);
        if (direct != null && !direct.trim().isEmpty()) {
            return normalizeKey(direct);
        }
        String path = env.get(fileName);
        if (path == null || path.trim().isEmpty()) {
            throw new IllegalArgumentException(
                    "Set " + directName + " or " + fileName + ". Key files are recommended.");
        }
        byte[] bytes = Files.readAllBytes(Paths.get(path));
        return normalizeKey(new String(bytes, StandardCharsets.UTF_8));
    }

    private static String secret(
            Map<String, String> env,
            String directName,
            String fileName,
            String legacyDirectName,
            String legacyFileName) throws IOException {
        if (nonBlank(env.get(directName)) || nonBlank(env.get(fileName))) {
            return secret(env, directName, fileName);
        }
        if (nonBlank(env.get(legacyDirectName)) || nonBlank(env.get(legacyFileName))) {
            System.err.println(
                    "Deprecated Alipay public-key configuration: use "
                            + directName + " or " + fileName);
            return secret(env, legacyDirectName, legacyFileName);
        }
        throw new IllegalArgumentException(
                "Set " + directName + " or " + fileName
                        + ". The value must be the Alipay public key, not the app public key.");
    }

    private static boolean nonBlank(String value) {
        return value != null && !value.trim().isEmpty();
    }

    private static String normalizeKey(String value) {
        return value
                .replace("-----BEGIN PRIVATE KEY-----", "")
                .replace("-----END PRIVATE KEY-----", "")
                .replace("-----BEGIN PUBLIC KEY-----", "")
                .replace("-----END PUBLIC KEY-----", "")
                .replaceAll("\\s", "");
    }

    private static int integer(Map<String, String> env, String name, int defaultValue) {
        String value = env.get(name);
        if (value == null || value.trim().isEmpty()) return defaultValue;
        int parsed = Integer.parseInt(value);
        if (parsed <= 0) throw new IllegalArgumentException(name + " must be positive");
        return parsed;
    }
}
