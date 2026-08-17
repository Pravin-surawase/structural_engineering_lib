import fs from "node:fs";
import http from "node:http";
import https from "node:https";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(fileURLToPath(import.meta.url));
const host = "127.0.0.1";
const port = 3000;
const keyPath = process.env.E1_OFFICE_KEY_PATH;
const certPath = process.env.E1_OFFICE_CERT_PATH;

if (!keyPath || !certPath) {
  throw new Error("Set E1_OFFICE_KEY_PATH and E1_OFFICE_CERT_PATH to trusted localhost development certificate files.");
}

const staticFiles = new Map([
  ["/", ["taskpane.html", "text/html; charset=utf-8"]],
  ["/taskpane.html", ["taskpane.html", "text/html; charset=utf-8"]],
  ["/taskpane.css", ["taskpane.css", "text/css; charset=utf-8"]],
  ["/taskpane.mjs", ["taskpane.mjs", "text/javascript; charset=utf-8"]],
  ["/taskpane-core.mjs", ["taskpane-core.mjs", "text/javascript; charset=utf-8"]],
]);

function proxyApi(request, response) {
  const upstream = http.request(
    {
      hostname: "127.0.0.1",
      port: 8000,
      method: request.method,
      path: request.url,
      headers: { ...request.headers, host: "127.0.0.1:8000" },
    },
    (upstreamResponse) => {
      response.writeHead(upstreamResponse.statusCode ?? 502, upstreamResponse.headers);
      upstreamResponse.pipe(response);
    },
  );
  upstream.on("error", (error) => {
    response.writeHead(502, { "Content-Type": "application/json" });
    response.end(JSON.stringify({ success: false, data: null, error: { message: error.message } }));
  });
  request.pipe(upstream);
}

const server = https.createServer(
  { key: fs.readFileSync(keyPath), cert: fs.readFileSync(certPath) },
  (request, response) => {
    const pathname = new URL(request.url, `https://${host}:${port}`).pathname;
    if (pathname.startsWith("/api/")) {
      proxyApi(request, response);
      return;
    }
    const entry = staticFiles.get(pathname);
    if (!entry) {
      response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
      response.end("Not found");
      return;
    }
    const [relativePath, contentType] = entry;
    response.writeHead(200, {
      "Content-Type": contentType,
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    });
    fs.createReadStream(path.join(root, relativePath)).pipe(response);
  },
);

server.listen(port, host, () => {
  console.log(`Excel Workbench task pane: https://localhost:${port}/taskpane.html`);
  console.log("API proxy target: http://127.0.0.1:8000/api/");
});
