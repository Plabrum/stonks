"use client";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { TrendingUp, DollarSign, Building2, FileText } from "lucide-react";
import { formatCurrency, formatDate } from "@/lib/utils";
import { $api } from "@/lib/hooks";
import { Suspense, use } from "react";

function CompanyDetail({ ticker }: { ticker: string }) {
  const { data: companyData, isLoading } = $api.useQuery(
    "get",
    "/company/{ticker}",
    { params: { path: { ticker } } },
  );

  if (isLoading) {
    return <div>Loading company data...</div>;
  }

  console.log("Company Data:", companyData);

  if (!companyData) {
    return <div>Company not found</div>;
  }

  const { name, industry, stats, latest_filing, predictions, comparables } =
    companyData;

  return (
    <div className="p-8">
      {/* Company Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <Building2 className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-4xl font-bold text-foreground">
              {name} <span className="text-muted-foreground">({ticker})</span>
            </h1>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="secondary">{industry}</Badge>
              <span className="text-sm text-muted-foreground">
                Last updated: {formatDate(companyData.updated_at)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Top 5 Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Current Share Price
            </CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${stats?.share_price}</div>
            <p className="text-xs text-muted-foreground">Per share</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Current Market Cap
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(stats?.equity_value || 0)}
            </div>
            <p className="text-xs text-muted-foreground">Total equity value</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              5Y Projected Price
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              ${predictions?.projected_5y_share_price}
            </div>
            <p className="text-xs text-muted-foreground">Target price</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              5Y Projected Market Cap
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {formatCurrency(
                (predictions?.projected_5y_share_price || 0) *
                  (stats?.shares_outstanding || 0),
              )}
            </div>
            <p className="text-xs text-muted-foreground">Projected value</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Fund Investment Change
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div
              className={`text-2xl font-bold ${
                (stats?.median_fund_investment_percentage_change || 0) >= 0
                  ? "text-green-600"
                  : "text-red-600"
              }`}
            >
              {(stats?.median_fund_investment_percentage_change || 0) >= 0
                ? "+"
                : ""}
              {(stats?.median_fund_investment_percentage_change || 0).toFixed(
                1,
              )}
              %
            </div>
            <p className="text-xs text-muted-foreground">Median change</p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Financial Metrics</CardTitle>
            <CardDescription>
              Key financial performance indicators
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">LTM EBITDA (% margin)</span>
              <span className="font-semibold">
                {formatCurrency(stats?.ltm_ebitda || 0)} (
                {(
                  ((stats?.ltm_ebitda || 0) / (stats?.ltm_revenue || 1)) *
                  100
                ).toFixed(1)}
                % margin)
              </span>
            </div>
            <Separator />
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">
                LTM Revenue (% growth)
              </span>
              <span className="font-semibold">
                {formatCurrency(stats?.ltm_revenue || 0)} (
                {(stats?.ltm_revenue_growth || 0) >= 0 ? "+" : ""}
                {(stats?.ltm_revenue_growth || 0).toFixed(1)}% growth)
              </span>
            </div>
            <Separator />
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">LTM Net Income</span>
              <span className="font-semibold">
                {formatCurrency(stats?.ltm_net_income || 0)}
              </span>
            </div>
            <Separator />
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Net Debt</span>
              <span className="font-semibold">
                {(stats?.debt || 0) - (stats?.cash || 0) < 0 ? "-" : ""}
                {formatCurrency(
                  Math.abs((stats?.debt || 0) - (stats?.cash || 0)),
                )}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Valuation Multiples</CardTitle>
            <CardDescription>Key valuation ratios</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">EV/LTM Revenue</span>
              <span className="font-semibold">
                {(stats?.multiple_ev_to_revenue || 0).toFixed(2)}x
              </span>
            </div>
            <Separator />
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">EV/LTM EBITDA</span>
              <span className="font-semibold">
                {(stats?.multiple_ev_to_ebitda || 0).toFixed(2)}x
              </span>
            </div>
            <Separator />
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">P/E Ratio</span>
              <span className="font-semibold">
                {(stats?.price_to_earnings || 0).toFixed(2)}x
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Comparables</CardTitle>
            <CardDescription>
              Median comparable company multiples
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Median EV/LTM Revenue</span>
              <span className="font-semibold text-muted-foreground">
                {(comparables?.median_ev_to_revenue || 0).toFixed(2)}x
              </span>
            </div>
            <Separator />
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Median EV/LTM EBITDA</span>
              <span className="font-semibold text-muted-foreground">
                {(comparables?.median_ev_to_ebitda || 0).toFixed(2)}x
              </span>
            </div>
            <Separator />
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Median P/E Ratio</span>
              <span className="font-semibold text-muted-foreground">
                {(comparables?.median_pe_ratio || 0).toFixed(2)}x
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Latest Filing */}
      {latest_filing && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Latest Filing
            </CardTitle>
            <CardDescription>
              Most recent SEC filing information
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Filing Type
                </p>
                <p className="text-lg font-semibold">{latest_filing.type}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Filing Date
                </p>
                <p className="text-lg font-semibold">
                  {formatDate(latest_filing.filing_date)}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Period End
                </p>
                <p className="text-lg font-semibold">
                  {formatDate(latest_filing.period_end)}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">CIK</p>
                <p className="text-lg font-semibold">{latest_filing.cik}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default function CompanyPage({
  params,
}: {
  params: Promise<{ ticker: string }>;
}) {
  const { ticker } = use(params);

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <CompanyDetail ticker={ticker} />
    </Suspense>
  );
}
