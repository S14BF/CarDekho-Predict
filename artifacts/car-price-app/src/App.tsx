import { Switch, Route, Router as WouterRouter, Redirect } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider, useAuth } from "@/hooks/use-auth";
import { ThemeProvider } from "@/hooks/use-theme";
import { Layout } from "@/components/layout";

import NotFound from "@/pages/not-found";
import Login from "@/pages/login";
import Dashboard from "@/pages/dashboard";
import Predict from "@/pages/predict";
import Compare from "@/pages/compare";
import Analysis from "@/pages/analysis";
import History from "@/pages/history";

const queryClient = new QueryClient();

function ProtectedRoute({ component: Component }: { component: any }) {
  const { user } = useAuth();
  if (!user) {
    return <Redirect to="/login" />;
  }
  return (
    <Layout>
      <Component />
    </Layout>
  );
}

function Router() {
  return (
    <Switch>
      <Route path="/login" component={Login} />
      <Route path="/">{() => <ProtectedRoute component={Dashboard} />}</Route>
      <Route path="/predict">{() => <ProtectedRoute component={Predict} />}</Route>
      <Route path="/compare">{() => <ProtectedRoute component={Compare} />}</Route>
      <Route path="/analysis">{() => <ProtectedRoute component={Analysis} />}</Route>
      <Route path="/history">{() => <ProtectedRoute component={History} />}</Route>
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="system" storageKey="vahanvalue-theme">
        <TooltipProvider>
          <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
            <AuthProvider>
              <Router />
            </AuthProvider>
          </WouterRouter>
          <Toaster />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
