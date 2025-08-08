import { CompanyClientPage } from "@/components/company-client-page";
import { Suspense } from "react";

export default async function CompanyPage({
  params,
}: {
  params: Promise<{ ticker: string }>;
}) {
  const { ticker } = await params;

  return (
    <Suspense fallback={<div>Loading company data...</div>}>
      <CompanyClientPage ticker={ticker} />
    </Suspense>
  );
}

