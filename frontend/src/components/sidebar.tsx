"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Building2, Database, BarChart3, TrendingUp, Moon, Sun } from "lucide-react"

const navigation = [
  {
    name: "Company Database",
    href: "/company",
    icon: Database,
    description: "Search and filter all companies",
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const { theme, setTheme } = useTheme()

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark")
  }

  return (
    <div className="w-64 bg-muted/10 border-r border-border flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary rounded-lg">
            <BarChart3 className="h-6 w-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">Company Analytics</h1>
            <p className="text-sm text-muted-foreground">Financial Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        <div className="mb-4">
          <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Navigation</h2>
        </div>

        {navigation.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          return (
            <Link key={item.name} href={item.href}>
              <Button
                variant={isActive ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start h-auto p-3 text-left",
                  isActive && "bg-secondary text-secondary-foreground",
                )}
              >
                <div className="flex items-start gap-3">
                  <Icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm">{item.name}</div>
                    <div className="text-xs text-muted-foreground mt-0.5">{item.description}</div>
                  </div>
                </div>
              </Button>
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-border space-y-3">
        {/* Market Status Card */}
        <Card className="p-3">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="h-4 w-4 text-green-600" />
            <span className="text-sm font-medium">Market Status</span>
          </div>
          <p className="text-xs text-muted-foreground">Real-time data updated every 15 minutes</p>
        </Card>

        {/* Dark Mode Toggle */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Theme</span>
          <Button variant="outline" size="sm" onClick={toggleTheme} className="h-8 w-8 p-0 bg-transparent">
            <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">Toggle theme</span>
          </Button>
        </div>
      </div>
    </div>
  )
}
