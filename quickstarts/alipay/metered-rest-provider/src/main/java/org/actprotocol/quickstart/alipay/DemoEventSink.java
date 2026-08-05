package org.actprotocol.quickstart.alipay;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

interface DemoEventSink extends AutoCloseable {
    void emit(String state, Map<String, Object> details);

    @Override
    void close();

    static DemoEventSink fromEnvironment() {
        String bridgeUrl = System.getenv("ACT_DEMO_BRIDGE_URL");
        if (bridgeUrl == null || bridgeUrl.trim().isEmpty()) return noop();
        String validationId = System.getenv("ACT_DEMO_VALIDATION_ID");
        if (validationId == null || validationId.trim().isEmpty()) {
            throw new IllegalArgumentException(
                    "ACT_DEMO_VALIDATION_ID is required when ACT_DEMO_BRIDGE_URL is set");
        }
        return new HttpDemoEventSink(bridgeUrl.trim(), validationId.trim());
    }

    static DemoEventSink noop() {
        return new DemoEventSink() {
            @Override
            public void emit(String state, Map<String, Object> details) {}

            @Override
            public void close() {}
        };
    }

    final class HttpDemoEventSink implements DemoEventSink {
        private final String bridgeUrl;
        private final String validationId;
        private final ObjectMapper json = new ObjectMapper();
        private final ExecutorService executor = Executors.newSingleThreadExecutor();

        HttpDemoEventSink(String bridgeUrl, String validationId) {
            this.bridgeUrl = bridgeUrl;
            this.validationId = validationId;
        }

        @Override
        public void emit(String state, Map<String, Object> details) {
            Map<String, Object> event = new LinkedHashMap<>();
            event.put("state", state);
            event.put("source", "metered-rest-provider");
            event.put("evidence_ref", validationId + "#" + state.toLowerCase());
            event.put("correlation_ref", validationId + "#correlation");
            event.putAll(details);
            executor.submit(() -> post(event));
        }

        private void post(Map<String, Object> event) {
            HttpURLConnection connection = null;
            try {
                byte[] body = json.writeValueAsBytes(event);
                connection = (HttpURLConnection) new URL(bridgeUrl).openConnection();
                connection.setRequestMethod("POST");
                connection.setConnectTimeout(500);
                connection.setReadTimeout(1000);
                connection.setDoOutput(true);
                connection.setRequestProperty("Content-Type", "application/json");
                connection.setFixedLengthStreamingMode(body.length);
                try (OutputStream output = connection.getOutputStream()) {
                    output.write(body);
                }
                int status = connection.getResponseCode();
                if (status < 200 || status >= 300) {
                    System.err.println("ACT demo event rejected: " + stateOf(event) + " HTTP " + status);
                }
            } catch (Exception exception) {
                System.err.println(
                        "ACT demo event unavailable: " + stateOf(event) + " "
                                + exception.getClass().getSimpleName());
            } finally {
                if (connection != null) connection.disconnect();
            }
        }

        private static String stateOf(Map<String, Object> event) {
            Object state = event.get("state");
            return state == null ? "unknown" : String.valueOf(state);
        }

        @Override
        public void close() {
            executor.shutdown();
            try {
                if (!executor.awaitTermination(2, TimeUnit.SECONDS)) executor.shutdownNow();
            } catch (InterruptedException exception) {
                executor.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
    }
}
