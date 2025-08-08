"use client";

import { CompanyDetail } from "@/components/company-detail";
import { useCompanyServiceGetCompanyByTickerSuspense } from "@/openapi/queries/suspense";

export function CompanyClientPage({ ticker }: { ticker: string }) {
  const { data: companyData } = useCompanyServiceGetCompanyByTickerSuspense({
    ticker,
  });

  if (!companyData) {
    return <div>Company not found</div>;
  }

  return <CompanyDetail companyData={companyData} />;
}
