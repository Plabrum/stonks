"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuCheckboxItem,
} from "@/components/ui/dropdown-menu";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Label } from "@/components/ui/label";
import {
  Search,
  Filter,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Plus,
  ExternalLink,
} from "lucide-react";
import { cn, formatCurrency } from "@/lib/utils";
import { $api } from "@/lib/hooks";
import Link from "next/link";
import { components } from "@/lib/api-client";

type CompanySearchSchema = components["schemas"]["CompanySearchSchema"];
type SortCriterion = components["schemas"]["SortCriterion"];
type NumericRange = components["schemas"]["NumericRange"];
import { useDebounce } from "@/lib/use-debounce";

interface RangeFilterProps {
  field: string;
  label: string;
  value: { min?: number; max?: number } | undefined;
  onApply: (field: string, min: number | null, max: number | null) => void;
  onClear: (field: string) => void;
  formatValue?: (value: number) => string;
}

function RangeFilter({
  field,
  label,
  value,
  onApply,
  onClear,
  formatValue,
}: RangeFilterProps) {
  const [min, setMin] = useState<string>(value?.min?.toString() || "");
  const [max, setMax] = useState<string>(value?.max?.toString() || "");
  const [isOpen, setIsOpen] = useState(false);

  const handleApply = () => {
    const minVal = min === "" ? null : Number.parseFloat(min);
    const maxVal = max === "" ? null : Number.parseFloat(max);
    onApply(field, minVal, maxVal);
    setIsOpen(false);
  };

  const handleClear = () => {
    setMin("");
    setMax("");
    onClear(field);
    setIsOpen(false);
  };

  const hasActiveFilter = value && (value.min != null || value.max != null);

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className={cn(
            "h-8 w-8 p-0",
            hasActiveFilter && "bg-primary text-primary-foreground",
          )}
        >
          <Plus className="h-4 w-4" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80">
        <div className="space-y-4">
          <div>
            <h4 className="font-medium">{label} Range</h4>
            <p className="text-sm text-muted-foreground">
              Set minimum and maximum values
            </p>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <Label htmlFor={`${field}-min`}>Minimum</Label>
              <Input
                id={`${field}-min`}
                type="number"
                placeholder="Min"
                value={min}
                onChange={(e) => setMin(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor={`${field}-max`}>Maximum</Label>
              <Input
                id={`${field}-max`}
                type="number"
                placeholder="Max"
                value={max}
                onChange={(e) => setMax(e.target.value)}
              />
            </div>
          </div>
          {hasActiveFilter && (
            <div className="text-sm text-muted-foreground">
              Current:{" "}
              {value?.min != null
                ? formatValue?.(value.min) || value.min
                : "No min"}{" "}
              -{" "}
              {value?.max != null
                ? formatValue?.(value.max) || value.max
                : "No max"}
            </div>
          )}
          <div className="flex gap-2">
            <Button onClick={handleApply} size="sm" className="flex-1">
              Apply
            </Button>
            <Button
              onClick={handleClear}
              variant="outline"
              size="sm"
              className="flex-1 bg-transparent"
            >
              Clear
            </Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}

export default function CompanyDatabase() {
  const [searchSchema, setSearchSchema] = useState<CompanySearchSchema>({
    pagination: { offset: 0, limit: 50 },
  });
  const debouncedSearchSchema = useDebounce(searchSchema, 300);

  const { data: companiesData, isLoading } = $api.useQuery(
    "post",
    "/company/search",
    {
      body: debouncedSearchSchema,
      params: { query: { session: undefined } },
    },
  );

  const industries = useMemo(
    () => [...new Set(companiesData?.map((c) => c.industry) || [])],
    [companiesData],
  );
  const subIndustries = useMemo(
    () => [...new Set(companiesData?.map((c) => c.sub_industry) || [])],
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
          // Change to desc
          newSorting =
            prev.sorting?.map((s) =>
              s.field === field ? { ...s, direction: "desc" } : s,
            ) || [];
        } else {
          // Remove sort
          newSorting = prev.sorting?.filter((s) => s.field !== field) || [];
        }
      } else {
        // Add new sort
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

  const handleSubIndustryFilter = (subIndustry: string, checked: boolean) => {
    setSearchSchema((prev) => {
      const currentSubIndustries = prev.filters?.subIndustries || [];
      const newSubIndustries = checked
        ? [...currentSubIndustries, subIndustry]
        : currentSubIndustries.filter((s) => s !== subIndustry);
      return {
        ...prev,
        filters: {
          ...prev.filters,
          subIndustries: newSubIndustries.length ? newSubIndustries : undefined,
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
      const newRanges = { ...prev.filters?.numericRanges };
      if (Object.keys(newRanges).length === 0) {
        return {
          ...prev,
          filters: { ...prev.filters, numericRanges: undefined },
        };
      }
      return {
        ...prev,
        filters: { ...prev.filters, numericRanges: newRanges },
      };
    });
  };

  const getSortIcon = (field: string) => {
    const sort = searchSchema.sorting?.find((s) => s.field === field);
    if (!sort) return <ArrowUpDown className="h-4 w-4" />;
    if (sort.direction === "asc") return <ArrowUp className="h-4 w-4" />;
    return <ArrowDown className="h-4 w-4" />;
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
            <CardTitle>Companies (0)</CardTitle>
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
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead
                    className="cursor-pointer"
                    onClick={() => handleSort("name")}
                  >
                    <div className="flex items-center gap-2">
                      Company Name {getSortIcon("name")}
                    </div>
                  </TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Website</TableHead>
                  <TableHead
                    className="cursor-pointer"
                    onClick={() => handleSort("industry")}
                  >
                    <div className="flex items-center gap-2">
                      Industry {getSortIcon("industry")}
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="outline"
                            size="sm"
                            className={cn(
                              "h-8 w-8 p-0",
                              (searchSchema.filters?.industries?.length || 0) >
                                0 && "bg-primary text-primary-foreground",
                            )}
                          >
                            <Filter className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                          {industries.map((industry) => (
                            <DropdownMenuCheckboxItem
                              key={industry}
                              checked={searchSchema.filters?.industries?.includes(
                                industry,
                              )}
                              onCheckedChange={(checked) =>
                                handleIndustryFilter(industry, !!checked)
                              }
                            >
                              {industry}
                            </DropdownMenuCheckboxItem>
                          ))}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </TableHead>
                  <TableHead
                    className="cursor-pointer"
                    onClick={() => handleSort("sub_industry")}
                  >
                    <div className="flex items-center gap-2">
                      Sub-Industry {getSortIcon("sub_industry")}
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="outline"
                            size="sm"
                            className={cn(
                              "h-8 w-8 p-0",
                              (searchSchema.filters?.subIndustries?.length ||
                                0) > 0 && "bg-primary text-primary-foreground",
                            )}
                          >
                            <Filter className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                          {subIndustries.map((subIndustry) => (
                            <DropdownMenuCheckboxItem
                              key={subIndustry}
                              checked={searchSchema.filters?.subIndustries?.includes(
                                subIndustry,
                              )}
                              onCheckedChange={(checked) =>
                                handleSubIndustryFilter(subIndustry, !!checked)
                              }
                            >
                              {subIndustry}
                            </DropdownMenuCheckboxItem>
                          ))}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </TableHead>
                  <TableHead
                    className="cursor-pointer"
                    onClick={() => handleSort("stats.share_price")}
                  >
                    <div className="flex items-center gap-2">
                      Share Price {getSortIcon("stats.share_price")}
                      <RangeFilter
                        field="stats.share_price"
                        label="Share Price"
                        value={
                          searchSchema.filters?.numericRanges?.[
                            "stats.share_price"
                          ]
                        }
                        onApply={handleRangeFilter}
                        onClear={clearRangeFilter}
                        formatValue={(val) => `${val}`}
                      />
                    </div>
                  </TableHead>
                  <TableHead
                    className="cursor-pointer"
                    onClick={() => handleSort("stats.equity_value")}
                  >
                    <div className="flex items-center gap-2">
                      Market Cap {getSortIcon("stats.equity_value")}
                      <RangeFilter
                        field="stats.equity_value"
                        label="Market Cap"
                        value={
                          searchSchema.filters?.numericRanges?.[
                            "stats.equity_value"
                          ]
                        }
                        onApply={handleRangeFilter}
                        onClear={clearRangeFilter}
                        formatValue={formatCurrency}
                      />
                    </div>
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading && (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center">
                      Loading...
                    </TableCell>
                  </TableRow>
                )}
                {!isLoading &&
                  companiesData.map((company) => (
                    <TableRow key={company.id}>
                      <TableCell className="font-medium">
                        <Link
                          href={`/company/${company.ticker}`}
                          className="text-blue-600 hover:underline"
                        >
                          {company.name}
                        </Link>
                      </TableCell>
                      <TableCell className="max-w-xs">
                        <div className="text-sm text-muted-foreground line-clamp-2">
                          {company.description}
                        </div>
                      </TableCell>
                      <TableCell>
                        <a
                          href={company.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-blue-600 hover:text-blue-800 text-sm"
                        >
                          {company.website?.replace("https://", "")}
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </TableCell>
                      <TableCell>{company.industry}</TableCell>
                      <TableCell>{company.sub_industry}</TableCell>
                      <TableCell>
                        {formatCurrency(company.stats.share_price)}
                      </TableCell>
                      <TableCell>
                        {formatCurrency(company.stats.equity_value)}
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
