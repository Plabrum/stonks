// generated with @7nohe/openapi-react-query-codegen@1.6.2

import {
  UseMutationOptions,
  UseQueryOptions,
  useMutation,
  useQuery,
} from "@tanstack/react-query";
import { CompanyService, DefaultService } from "../requests/services.gen";
import { CompanySearchSchema } from "../requests/types.gen";
import * as Common from "./common";
export const useDefaultServiceGetHealth = <
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
  useQuery<TData, TError>({
    queryKey: Common.UseDefaultServiceGetHealthKeyFn(
      { includeInSchema },
      queryKey,
    ),
    queryFn: () => DefaultService.getHealth({ includeInSchema }) as TData,
    ...options,
  });
export const useCompanyServiceGetCompanyByTicker = <
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
  useQuery<TData, TError>({
    queryKey: Common.UseCompanyServiceGetCompanyByTickerKeyFn(
      { ticker },
      queryKey,
    ),
    queryFn: () => CompanyService.getCompanyByTicker({ ticker }) as TData,
    ...options,
  });
export const useCompanyServicePostCompanySearch = <
  TData = Common.CompanyServicePostCompanySearchMutationResult,
  TError = unknown,
  TContext = unknown,
>(
  options?: Omit<
    UseMutationOptions<
      TData,
      TError,
      {
        requestBody: CompanySearchSchema;
      },
      TContext
    >,
    "mutationFn"
  >,
) =>
  useMutation<
    TData,
    TError,
    {
      requestBody: CompanySearchSchema;
    },
    TContext
  >({
    mutationFn: ({ requestBody }) =>
      CompanyService.postCompanySearch({
        requestBody,
      }) as unknown as Promise<TData>,
    ...options,
  });
