import fs from "node:fs";
import commonjs from "@rollup/plugin-commonjs";
import json from "@rollup/plugin-json";
import { nodeResolve } from "@rollup/plugin-node-resolve";
import replace from "@rollup/plugin-replace";
import typescript from "@rollup/plugin-typescript";
import externalGlobals from "rollup-plugin-external-globals";
import importAssets from "rollup-plugin-import-assets";

const manifest = JSON.parse(fs.readFileSync("plugin.json", "utf8"));

export default {
  input: "./src/index.tsx",
  plugins: [
    typescript(),
    json(),
    commonjs(),
    nodeResolve({ browser: true }),
    externalGlobals({
      react: "SP_REACT",
      "react/jsx-runtime": "SP_JSX",
      "react-dom": "SP_REACTDOM",
      "@decky/ui": "DFL",
      "@decky/manifest": JSON.stringify(manifest),
    }),
    replace({ preventAssignment: false, "process.env.NODE_ENV": JSON.stringify("production") }),
    importAssets({ publicPath: `http://127.0.0.1:1337/plugins/${manifest.name}/` }),
    {
      name: "codex-css-bundle",
      load(id) {
        if (id.endsWith("/src/style.css")) return `export default ${JSON.stringify(fs.readFileSync(id, "utf8"))};`;
        return null;
      },
    },
  ],
  context: "window",
  external: ["react", "react-dom", "@decky/ui"],
  treeshake: {
    pureExternalImports: { pure: ["@decky/ui", "@decky/api"] },
    preset: "smallest",
  },
  output: { dir: "dist", format: "esm", sourcemap: false, exports: "default" },
};
