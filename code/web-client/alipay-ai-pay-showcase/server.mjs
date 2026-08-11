import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createDemoServer } from "./bridge-server.mjs";

const root = join(dirname(fileURLToPath(import.meta.url)), "public");
const port = Number(process.env.PORT || 4173);
const demo = createDemoServer({ root, port });

await demo.start();
process.stdout.write(`ACT showcase: http://127.0.0.1:${demo.port()}\n`);
process.stdout.write(`Live event bridge: http://127.0.0.1:${demo.port()}/events\n`);

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, async () => {
    await demo.close();
    process.exit(0);
  });
}
