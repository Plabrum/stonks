"use client";

import { useState } from "react";
import Link from "next/link";
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
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Filter, ArrowUpDown, ArrowUp, ArrowDown, Plus } from "lucide-react";
import { cn, formatCurrency } from "@/lib/utils";
import {
  CompanySearchResultSchema,
  type CompanySearchSchema,
} from "@/openapi/requests";

interface RangeFilterProps {
  field: string;
  label: string;
  value: { min?: number | null; max?: number | null } | undefined;
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
  const [min, setMin] = useState<string>(
    value?.min != null ? value.min.toString() : "",
  );
  const [max, setMax] = useState<string>(
    value?.max != null ? value.max.toString() : "",
  );
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

interface CompanyTableProps {
  companiesData: CompanySearchResultSchema[];
  isLoading: boolean;
  searchSchema: CompanySearchSchema;
  industries: string[];
  onSort: (field: string) => void;
  onIndustryFilter: (industry: string, checked: boolean) => void;
  onRangeFilter: (
    field: string,
    min: number | null,
    max: number | null,
  ) => void;
  clearRangeFilter: (field: string) => void;
}

export function CompanyTable({
  companiesData,
  searchSchema,
  industries,
  onSort,
  onIndustryFilter,
  onRangeFilter,
  clearRangeFilter,
}: CompanyTableProps) {
  const getSortIcon = (field: string) => {
    const sort = searchSchema.sorting?.find((s) => s.field === field);
    if (!sort) return <ArrowUpDown className="h-4 w-4" />;
    return sort.direction === "asc" ? (
      <ArrowUp className="h-4 w-4" />
    ) : (
      <ArrowDown className="h-4 w-4" />
    );
  };

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead
              onClick={() => onSort("name")}
              className="cursor-pointer"
            >
              <div className="flex items-center gap-2">
                Company Name {getSortIcon("name")}
              </div>
            </TableHead>
            <TableHead
              onClick={() => onSort("industry")}
              className="cursor-pointer"
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
                        (searchSchema.filters?.industries?.length || 0) > 0 &&
                          "bg-primary text-primary-foreground",
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
                          onIndustryFilter(industry, !!checked)
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
              onClick={() => onSort("equity_value")}
              className="cursor-pointer"
            >
              <div className="flex items-center gap-2">
                Market Cap {getSortIcon("equity_value")}
                <RangeFilter
                  field="equity_value"
                  label="Market Cap"
                  value={
                    searchSchema.filters?.numericRanges?.["equity_value"]
                  }
                  onApply={onRangeFilter}
                  onClear={clearRangeFilter}
                  formatValue={formatCurrency}
                />
              </div>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {companiesData.map((company) => (
            <TableRow key={company.id}>
              <TableCell className="font-medium">
                <Link
                  href={`/company/${company.ticker}`}
                  className="text-blue-600 hover:underline"
                >
                  {company.name}
                </Link>
              </TableCell>
              <TableCell>{company.industry}</TableCell>
              <TableCell>
                {formatCurrency(company.equity_value)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}