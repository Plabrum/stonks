import createClient from "openapi-fetch";
import type { paths } from "./api-client";

const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

if (!baseUrl) {
  throw new Error("Missing NEXT_PUBLIC_API_BASE_URL");
}

export const fetchClient = createClient<paths>({ baseUrl });
