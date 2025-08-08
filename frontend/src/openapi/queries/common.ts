// generated with @7nohe/openapi-react-query-codegen@1.6.2 

import { UseQueryResult } from "@tanstack/react-query";
import { CompanyService, DefaultService } from "../requests/services.gen";
export type DefaultServiceGetHealthDefaultResponse = Awaited<ReturnType<typeof DefaultService.getHealth>>;
export type DefaultServiceGetHealthQueryResult<TData = DefaultServiceGetHealthDefaultResponse, TError = unknown> = UseQueryResult<TData, TError>;
export const useDefaultServiceGetHealthKey = "DefaultServiceGetHealth";
export const UseDefaultServiceGetHealthKeyFn = ({ includeInSchema }: {
  includeInSchema?: boolean;
} = {}, queryKey?: Array<unknown>) => [useDefaultServiceGetHealthKey, ...(queryKey ?? [{ includeInSchema }])];
export type CompanyServiceGetCompanyByTickerDefaultResponse = Awaited<ReturnType<typeof CompanyService.getCompanyByTicker>>;
export type CompanyServiceGetCompanyByTickerQueryResult<TData = CompanyServiceGetCompanyByTickerDefaultResponse, TError = unknown> = UseQueryResult<TData, TError>;
export const useCompanyServiceGetCompanyByTickerKey = "CompanyServiceGetCompanyByTicker";
export const UseCompanyServiceGetCompanyByTickerKeyFn = ({ ticker }: {
  ticker: string;
}, queryKey?: Array<unknown>) => [useCompanyServiceGetCompanyByTickerKey, ...(queryKey ?? [{ ticker }])];
export type CompanyServicePostCompanySearchMutationResult = Awaited<ReturnType<typeof CompanyService.postCompanySearch>>;
