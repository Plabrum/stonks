// generated with @7nohe/openapi-react-query-codegen@1.6.2 

import { type QueryClient } from "@tanstack/react-query";
import { CompanyService, DefaultService } from "../requests/services.gen";
import * as Common from "./common";
export const prefetchUseDefaultServiceGetHealth = (queryClient: QueryClient, { includeInSchema }: {
  includeInSchema?: boolean;
} = {}) => queryClient.prefetchQuery({ queryKey: Common.UseDefaultServiceGetHealthKeyFn({ includeInSchema }), queryFn: () => DefaultService.getHealth({ includeInSchema }) });
export const prefetchUseCompanyServiceGetCompanyByTicker = (queryClient: QueryClient, { ticker }: {
  ticker: string;
}) => queryClient.prefetchQuery({ queryKey: Common.UseCompanyServiceGetCompanyByTickerKeyFn({ ticker }), queryFn: () => CompanyService.getCompanyByTicker({ ticker }) });
