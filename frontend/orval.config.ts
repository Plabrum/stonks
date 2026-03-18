import { defineConfig } from "orval";

const OPENAPI_URL =
  process.env.OPENAPI_URL ?? "http://localhost:8000/schema/openapi.json";

export default defineConfig({
  stonks: {
    input: {
      target: OPENAPI_URL,
    },
    output: {
      mode: "tags-split",
      target: "src/openapi",
      client: "react-query",
      override: {
        query: {
          useSuspenseQuery: true,
        },
        mutator: {
          path: "src/openapi/custom-instance.ts",
          name: "customInstance",
        },
      },
    },
  },
});
