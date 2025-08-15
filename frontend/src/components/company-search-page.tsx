"use client";
import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";

import { useDebounce } from "@/lib/use-debounce";
import { SortCriterion, type CompanySearchSchema } from "@/openapi/requests";
import { CompanyTable } from "@/components/company-table";

import { useCompanyServicePostCompanySearch } from "@/openapi/queries";
import { useSuspenseQuery } from "@tanstack/react-query";

export function useSearchCompaniesQuery(input: CompanySearchSchema) {
  const { mutateAsync } = useCompanyServicePostCompanySearch();

  return useSuspenseQuery({
    queryKey: ["searchCompanies", input],
    queryFn: () => mutateAsync({ requestBody: input }),
  });
}

export default function CompanySearchPage() {
  const [searchSchema, setSearchSchema] = useState<CompanySearchSchema>({
    pagination: { offset: 0, limit: 50 },
  });
  const debouncedSearchSchema = useDebounce(searchSchema, 300);

  const { data: companiesData } = useSearchCompaniesQuery(
    debouncedSearchSchema,
  );

  const industries: string[] = useMemo(
    () => [
      ...new Set(
        companiesData
          ?.map((c) => c.industry)
          .filter((i): i is string => Boolean(i)),
      ),
    ],
    [companiesData],
  );

  const handleSearchTermChange = (term: string) => {
    setSearchSchema((prev) => ({ ...prev, search: term || undefined }));
  };

  const handleSort = (field: string) => {
    setSearchSchema((prev) => {
      const existingSort = prev.sorting?.find((s) => s.field === field);
      let newSorting: SortCriterion[];

      if (existingSort) {
        if (existingSort.direction === "asc") {
          newSorting =
            prev.sorting?.map((s) =>
              s.field === field ? { ...s, direction: "desc" } : s,
            ) || [];
        } else {
          newSorting = prev.sorting?.filter((s) => s.field !== field) || [];
        }
      } else {
        newSorting = [...(prev.sorting || []), { field, direction: "asc" }];
      }

      return { ...prev, sorting: newSorting.length ? newSorting : undefined };
    });
  };

  const handleIndustryFilter = (industry: string, checked: boolean) => {
    setSearchSchema((prev) => {
      const currentIndustries = prev.filters?.industries || [];
      const newIndustries = checked
        ? [...currentIndustries, industry]
        : currentIndustries.filter((i) => i !== industry);
      return {
        ...prev,
        filters: {
          ...prev.filters,
          industries: newIndustries.length ? newIndustries : undefined,
        },
      };
    });
  };

  const handleRangeFilter = (
    field: string,
    min: number | null,
    max: number | null,
  ) => {
    setSearchSchema((prev) => {
      const newNumericRanges = {
        ...(prev.filters?.numericRanges || {}),
        [field]: { min: min ?? undefined, max: max ?? undefined },
      };
      return {
        ...prev,
        filters: {
          ...prev.filters,
          numericRanges: newNumericRanges,
        },
      };
    });
  };

  const clearRangeFilter = (field: string) => {
    setSearchSchema((prev) => {
      const ranges = { ...prev.filters?.numericRanges };
      delete ranges[field];

      return {
        ...prev,
        filters: {
          ...prev.filters,
          numericRanges: Object.keys(ranges).length ? ranges : undefined,
        },
      };
    });
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">Company Database</h1>
        <p className="text-muted-foreground">
          Comprehensive database of company financial metrics and projections
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Companies ({companiesData.length})</CardTitle>
          </div>
          <div className="flex items-center gap-4 mt-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search companies..."
                value={searchSchema.search || ""}
                onChange={(e) => handleSearchTermChange(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <CompanyTable
            companiesData={companiesData}
            searchSchema={searchSchema}
            industries={industries}
            onSort={handleSort}
            onIndustryFilter={handleIndustryFilter}
            onRangeFilter={handleRangeFilter}
            clearRangeFilter={clearRangeFilter}
          />
        </CardContent>
      </Card>
    </div>
  );
}
