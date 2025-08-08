// generated with @7nohe/openapi-react-query-codegen@1.6.2

import { UseQueryOptions, useSuspenseQuery } from "@tanstack/react-query";
import { CompanyService, DefaultService } from "../requests/services.gen";
import * as Common from "./common";
export const useDefaultServiceGetHealthSuspense = <
  TData = Common.DefaultServiceGetHealthDefaultResponse,
  TError = unknown,
  TQueryKey extends Array<unknown> = unknown[],
>(
  {
    includeInSchema,
  }: {
    includeInSchema?: boolean;
  } = {},
  queryKey?: TQueryKey,
  options?: Omit<UseQueryOptions<TData, TError>, "queryKey" | "queryFn">,
) =>
  useSuspenseQuery<TData, TError>({
    queryKey: Common.UseDefaultServiceGetHealthKeyFn(
      { includeInSchema },
      queryKey,
    ),
    queryFn: () => DefaultService.getHealth({ includeInSchema }) as TData,
    ...options,
  });
export const useCompanyServiceGetCompanyByTickerSuspense = <
  TData = Common.CompanyServiceGetCompanyByTickerDefaultResponse,
  TError = unknown,
  TQueryKey extends Array<unknown> = unknown[],
>(
  {
    ticker,
  }: {
    ticker: string;
  },
  queryKey?: TQueryKey,
  options?: Omit<UseQueryOptions<TData, TError>, "queryKey" | "queryFn">,
) =>
  useSuspenseQuery<TData, TError>({
    queryKey: Common.UseCompanyServiceGetCompanyByTickerKeyFn(
      { ticker },
      queryKey,
    ),
    queryFn: () => CompanyService.getCompanyByTicker({ ticker }) as TData,
    ...options,
  });
