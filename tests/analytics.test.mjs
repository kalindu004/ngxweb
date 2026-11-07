import { readFileSync } from "node:fs";
import vm from "node:vm";

const root = new URL("../", import.meta.url);
const configSource = readFileSync(new URL("js/analytics-config.js", root), "utf8");
const analyticsSource = readFileSync(new URL("js/analytics.js", root), "utf8");

function run(extraConfig) {
  const created = [];
  const sandbox = {
    window: {},
    document: {
      createElement() {
        return { async: false, src: "" };
      },
      head: {
        appendChild(el) {
          created.push(el.src);
        },
      },
    },
  };
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(configSource + "\n" + analyticsSource, sandbox);
  if (extraConfig) {
    Object.assign(sandbox.window.NGX_ANALYTICS, extraConfig);
    vm.runInContext(analyticsSource, sandbox);
  }
  return { created, config: sandbox.window.NGX_ANALYTICS };
}

const off = run();
if (off.config.provider !== "" || off.config.measurementId !== "") {
  throw new Error("shipped analytics config must stay empty");
}
if (off.created.length !== 0) {
  throw new Error("empty config must not inject a script: " + off.created.join(","));
}

const bad = run({ provider: "ga4", measurementId: "UA-00000-1" });
if (bad.created.length !== 0) {
  throw new Error("non-GA4 ids must not load");
}

const on = run({ provider: "ga4", measurementId: "G-" + "UNITTEST1" });
if (on.created.length !== 1 || !on.created[0].includes("id=G-" + "UNITTEST1")) {
  throw new Error("a real-shaped id should be the only case that loads gtag");
}

if (configSource.includes("G-") || configSource.includes("GTM-") || configSource.includes("UA-")) {
  throw new Error("analytics-config.js must not contain a measurement id");
}

console.log("analytics gate: off, rejected UA id, accepted shaped id in memory only");
