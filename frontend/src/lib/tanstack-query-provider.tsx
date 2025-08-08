"use client";

import React, { ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { OpenAPI } from "@/openapi/requests";

const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL!;

OpenAPI.BASE = baseUrl;
// You can share this queryClient across your app
export const queryClient = new QueryClient();

export const TanstackQueryProvider = ({
  children,
}: {
  children: ReactNode;
}) => {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
};
