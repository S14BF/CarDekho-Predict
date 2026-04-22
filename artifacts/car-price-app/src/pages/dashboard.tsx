import { useAuth } from "@/hooks/use-auth";
import { useGetInsights } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Car, Scale, BarChart3, History, TrendingUp, IndianRupee, Hash, Award } from "lucide-react";
import { Link } from "wouter";
import { motion } from "framer-motion";
import { Skeleton } from "@/components/ui/skeleton";

export default function Dashboard() {
  const { user } = useAuth();
  const { data: insights, isLoading, isError } = useGetInsights();

  const formatCurrency = (val: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(val);

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold tracking-tight">Welcome, {user?.username}</h1>
        <p className="text-muted-foreground mt-2">Here's a quick overview of the used car market data.</p>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {isLoading || !insights ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <Skeleton className="h-4 w-[100px]" />
                <Skeleton className="h-4 w-4 rounded-full" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-[120px]" />
              </CardContent>
            </Card>
          ))
        ) : isError ? (
          <div className="col-span-full p-4 bg-destructive/10 text-destructive rounded-md">
            Failed to load market insights.
          </div>
        ) : (
          <>
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }}>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Cars Analyzed</CardTitle>
                  <Hash className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{insights.totals.rows.toLocaleString('en-IN')}</div>
                </CardContent>
              </Card>
            </motion.div>
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }}>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Avg Market Price</CardTitle>
                  <IndianRupee className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatCurrency(insights.totals.average_price)}</div>
                </CardContent>
              </Card>
            </motion.div>
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3 }}>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Median Price</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatCurrency(insights.totals.median_price)}</div>
                </CardContent>
              </Card>
            </motion.div>
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.4 }}>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Popular Brand</CardTitle>
                  <Award className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{insights.totals.most_popular_brand}</div>
                </CardContent>
              </Card>
            </motion.div>
          </>
        )}
      </div>

      {/* Quick Nav */}
      <h2 className="text-xl font-bold tracking-tight pt-4">Quick Actions</h2>
      <div className="grid gap-4 md:grid-cols-2">
        <Link href="/predict">
          <Card className="hover:border-primary transition-colors cursor-pointer group">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <Car className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Predict Price</h3>
                <p className="text-sm text-muted-foreground">Estimate the resale value of a car</p>
              </div>
            </CardContent>
          </Card>
        </Link>
        <Link href="/compare">
          <Card className="hover:border-primary transition-colors cursor-pointer group">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <Scale className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Compare Cars</h3>
                <p className="text-sm text-muted-foreground">Side-by-side spec & price comparison</p>
              </div>
            </CardContent>
          </Card>
        </Link>
        <Link href="/analysis">
          <Card className="hover:border-primary transition-colors cursor-pointer group">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <BarChart3 className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">Market Analysis</h3>
                <p className="text-sm text-muted-foreground">View market trends and charts</p>
              </div>
            </CardContent>
          </Card>
        </Link>
        <Link href="/history">
          <Card className="hover:border-primary transition-colors cursor-pointer group">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <History className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-lg">History</h3>
                <p className="text-sm text-muted-foreground">View your past predictions</p>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>
    </div>
  );
}
