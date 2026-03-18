import { Suspense } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import {
  Outlet,
  createRootRoute,
  createRoute,
  createRouter,
  redirect,
} from "@tanstack/react-router";

import { Sidebar } from "@/components/sidebar";
import { ThemeProvider } from "@/components/theme-provider";
import { CompanyClientPage } from "@/components/company-client-page";
import CompanySearchPage from "@/components/company-search-page";

export const queryClient = new QueryClient();

const rootRoute = createRootRoute({
  component: () => (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <div className="flex h-screen bg-background">
          <Sidebar />
          <main className="flex-1 overflow-auto">
            <Outlet />
          </main>
        </div>
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </ThemeProvider>
  ),
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  beforeLoad: () => {
    throw redirect({ to: "/company" });
  },
});

const companyRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/company",
  component: () => (
    <Suspense fallback={<div className="p-8">Loading...</div>}>
      <CompanySearchPage />
    </Suspense>
  ),
});

const companyDetailRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/company/$ticker",
  component: function CompanyDetailPage() {
    const { ticker } = companyDetailRoute.useParams();
    return (
      <Suspense fallback={<div className="p-8">Loading...</div>}>
        <CompanyClientPage ticker={ticker} />
      </Suspense>
    );
  },
});

const routeTree = rootRoute.addChildren([
  indexRoute,
  companyRoute,
  companyDetailRoute,
]);

export const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
