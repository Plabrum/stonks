// generated with @7nohe/openapi-react-query-codegen@1.6.2 

import { type QueryClient } from "@tanstack/react-query";
import { CompanyService, DefaultService } from "../requests/services.gen";
import * as Common from "./common";
export const ensureUseDefaultServiceGetHealthData = (queryClient: QueryClient, { includeInSchema }: {
  includeInSchema?: boolean;
} = {}) => queryClient.ensureQueryData({ queryKey: Common.UseDefaultServiceGetHealthKeyFn({ includeInSchema }), queryFn: () => DefaultService.getHealth({ includeInSchema }) });
export const ensureUseCompanyServiceGetCompanyByTickerData = (queryClient: QueryClient, { ticker }: {
  ticker: string;
}) => queryClient.ensureQueryData({ queryKey: Common.UseCompanyServiceGetCompanyByTickerKeyFn({ ticker }), queryFn: () => CompanyService.getCompanyByTicker({ ticker }) });
