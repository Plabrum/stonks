import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { Sidebar } from "@/components/sidebar"
import { TanstackQueryProvider } from "@/lib/tanstack-query-provider"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Company Analytics Platform",
  description: "Comprehensive company financial analysis and database",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <TanstackQueryProvider>
            <div className="flex h-screen bg-background">
              <Sidebar />
              <main className="flex-1 overflow-auto">{children}</main>
            </div>
          </TanstackQueryProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
