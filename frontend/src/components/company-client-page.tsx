"use client";

import { CompanyDetail } from "@/components/company-detail";
import { useGetByTickerSuspense } from "@/openapi/company/company";

export function CompanyClientPage({ ticker }: { ticker: string }) {
  const { data: companyData } = useGetByTickerSuspense(ticker);

  if (!companyData) {
    return <div>Company not found</div>;
  }

  return <CompanyDetail companyData={companyData} />;
}
