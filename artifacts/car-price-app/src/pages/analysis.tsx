import { useState } from "react";
import { useGetInsights } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import { useTheme } from "@/hooks/use-theme";

export default function Analysis() {
  const { data: insights, isLoading } = useGetInsights();
  const [brandFilter, setBrandFilter] = useState<string>("all");
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const textColor = isDark ? "rgba(255,255,255,0.7)" : "rgba(0,0,0,0.7)";
  const primaryColor = "hsl(var(--primary))";

  if (isLoading || !insights) {
    return (
      <div className="space-y-8">
        <Skeleton className="h-8 w-1/4" />
        <div className="grid md:grid-cols-2 gap-6">
          <Skeleton className="h-[300px] w-full" />
          <Skeleton className="h-[300px] w-full" />
        </div>
      </div>
    );
  }

  const allBrands = insights.by_brand.map((b) => b.brand).sort();
  const filteredBrands = brandFilter === "all" 
    ? insights.by_brand.slice(0, 10) 
    : insights.by_brand.filter((b) => b.brand === brandFilter);

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Market Analysis</h1>
          <p className="text-muted-foreground mt-2">Explore trends in the used car market.</p>
        </div>
        <div className="w-64">
          <Select value={brandFilter} onValueChange={setBrandFilter}>
            <SelectTrigger>
              <SelectValue placeholder="Filter by Brand" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Top 10 Brands</SelectItem>
              {allBrands.map((b) => (
                <SelectItem key={b} value={b}>{b}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Average Price by Brand</CardTitle>
          </CardHeader>
          <CardContent className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={filteredBrands} margin={{ top: 10, right: 10, left: 20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={isDark ? "#333" : "#eee"} />
                <XAxis dataKey="brand" angle={-45} textAnchor="end" tick={{ fill: textColor, fontSize: 12 }} />
                <YAxis tickFormatter={(value) => `₹${(value / 100000).toFixed(1)}L`} tick={{ fill: textColor, fontSize: 12 }} />
                <Tooltip 
                  formatter={(value: number) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value)}
                  contentStyle={{ backgroundColor: isDark ? "#111" : "#fff", borderColor: isDark ? "#333" : "#eee", color: isDark ? "#fff" : "#000" }}
                />
                <Bar dataKey="average_price" fill={primaryColor} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Depreciation Curve (Price vs Age)</CardTitle>
          </CardHeader>
          <CardContent className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={insights.by_age} margin={{ top: 10, right: 10, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={isDark ? "#333" : "#eee"} />
                <XAxis dataKey="vehicle_age" tick={{ fill: textColor, fontSize: 12 }} label={{ value: 'Age (Years)', position: 'insideBottom', offset: -10, fill: textColor }} />
                <YAxis tickFormatter={(value) => `₹${(value / 100000).toFixed(1)}L`} tick={{ fill: textColor, fontSize: 12 }} />
                <Tooltip 
                  formatter={(value: number) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value)}
                  labelFormatter={(label) => `Age: ${label} Years`}
                  contentStyle={{ backgroundColor: isDark ? "#111" : "#fff", borderColor: isDark ? "#333" : "#eee", color: isDark ? "#fff" : "#000" }}
                />
                <Line type="monotone" dataKey="average_price" stroke={primaryColor} strokeWidth={3} dot={{ r: 4, fill: primaryColor }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Average Price by Fuel Type</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={insights.by_fuel} layout="vertical" margin={{ top: 10, right: 10, left: 40, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke={isDark ? "#333" : "#eee"} />
                <XAxis type="number" tickFormatter={(value) => `₹${(value / 100000).toFixed(1)}L`} tick={{ fill: textColor, fontSize: 12 }} />
                <YAxis type="category" dataKey="fuel_type" tick={{ fill: textColor, fontSize: 12 }} />
                <Tooltip 
                  formatter={(value: number) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value)}
                  contentStyle={{ backgroundColor: isDark ? "#111" : "#fff", borderColor: isDark ? "#333" : "#eee", color: isDark ? "#fff" : "#000" }}
                />
                <Bar dataKey="average_price" fill="hsl(var(--chart-2))" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Average Price by Transmission</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={insights.by_transmission} margin={{ top: 10, right: 10, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={isDark ? "#333" : "#eee"} />
                <XAxis dataKey="transmission_type" tick={{ fill: textColor, fontSize: 12 }} />
                <YAxis tickFormatter={(value) => `₹${(value / 100000).toFixed(1)}L`} tick={{ fill: textColor, fontSize: 12 }} />
                <Tooltip 
                  formatter={(value: number) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value)}
                  contentStyle={{ backgroundColor: isDark ? "#111" : "#fff", borderColor: isDark ? "#333" : "#eee", color: isDark ? "#fff" : "#000" }}
                />
                <Bar dataKey="average_price" fill="hsl(var(--chart-3))" radius={[4, 4, 0, 0]} maxBarSize={60} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
