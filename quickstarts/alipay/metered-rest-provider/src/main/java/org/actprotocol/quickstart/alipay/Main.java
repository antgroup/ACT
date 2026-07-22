package org.actprotocol.quickstart.alipay;

public final class Main {
    private Main() {}

    public static void main(String[] args) throws Exception {
        Config config = Config.fromEnvironment();
        OfficialAlipayGateway gateway = new OfficialAlipayGateway(config);
        PaidResourceServer server =
                new PaidResourceServer(config, gateway, new BillSigner.Rsa2(config.privateKey));
        Runtime.getRuntime().addShutdownHook(new Thread(server::close));
        server.start();
        System.out.println("ACT Alipay paid resource listening on http://localhost:"
                + server.port() + "/paid-resource");
        System.out.println("Only official Alipay verification can release the resource.");
    }
}
