import { useState } from "react";
import { useGetOptions, usePredict, useSimilar, PredictRequest } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { motion, AnimatePresence } from "framer-motion";
import { RotateCcw, Sparkles, AlertCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

const defaultValues: PredictRequest = {
  brand: "",
  model: "",
  seller_type: "",
  fuel_type: "",
  transmission_type: "",
  vehicle_age: 5,
  km_driven: 50000,
  mileage: 18,
  engine: 1200,
  max_power: 80,
  seats: 5,
};

const formatCurrency = (val: number) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(val);

export default function Predict() {
  const { data: optionsData, isLoading: isLoadingOptions } = useGetOptions();
  const predictMutation = usePredict();
  const similarMutation = useSimilar();

  const [form, setForm] = useState<PredictRequest>(defaultValues);

  const handlePredict = async () => {
    if (!form.brand || !form.model || !form.fuel_type || !form.transmission_type || !form.seller_type) {
      return;
    }
    const result = await predictMutation.mutateAsync(form);
    
    // Save to history
    const history = JSON.parse(localStorage.getItem("carapp_history") || "[]");
    history.push({
      id: Date.now(),
      date: new Date().toISOString(),
      car: `${form.brand} ${form.model} (${new Date().getFullYear() - form.vehicle_age})`,
      predicted_price: result.predicted_price,
      inputs: form,
    });
    localStorage.setItem("carapp_history", JSON.stringify(history));

    similarMutation.mutate({ target_price: result.predicted_price });
  };

  const handleReset = () => {
    setForm(defaultValues);
    predictMutation.reset();
    similarMutation.reset();
  };

  if (isLoadingOptions || !optionsData) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-1/3" />
        <Skeleton className="h-[500px] w-full" />
      </div>
    );
  }

  const { options, brand_models } = optionsData;
  const availableModels = form.brand && brand_models[form.brand] ? brand_models[form.brand] : [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Predict Price</h1>
        <p className="text-muted-foreground mt-2">Enter car details to get an estimated resale value.</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Car Details</CardTitle>
            <CardDescription>Fill in the specifications of the vehicle.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Brand</Label>
                <Select
                  value={form.brand}
                  onValueChange={(val) => setForm({ ...form, brand: val, model: "" })}
                >
                  <SelectTrigger><SelectValue placeholder="Select Brand" /></SelectTrigger>
                  <SelectContent>
                    {options.brand.map((b) => <SelectItem key={b} value={b}>{b}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Model</Label>
                <Select
                  value={form.model}
                  onValueChange={(val) => setForm({ ...form, model: val })}
                  disabled={!form.brand}
                >
                  <SelectTrigger><SelectValue placeholder="Select Model" /></SelectTrigger>
                  <SelectContent>
                    {availableModels.map((m) => <SelectItem key={m} value={m}>{m}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Fuel Type</Label>
                <Select
                  value={form.fuel_type}
                  onValueChange={(val) => setForm({ ...form, fuel_type: val })}
                >
                  <SelectTrigger><SelectValue placeholder="Fuel Type" /></SelectTrigger>
                  <SelectContent>
                    {options.fuel_type.map((f) => <SelectItem key={f} value={f}>{f}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Transmission</Label>
                <Select
                  value={form.transmission_type}
                  onValueChange={(val) => setForm({ ...form, transmission_type: val })}
                >
                  <SelectTrigger><SelectValue placeholder="Transmission" /></SelectTrigger>
                  <SelectContent>
                    {options.transmission_type.map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Seller Type</Label>
                <Select
                  value={form.seller_type}
                  onValueChange={(val) => setForm({ ...form, seller_type: val })}
                >
                  <SelectTrigger><SelectValue placeholder="Seller Type" /></SelectTrigger>
                  <SelectContent>
                    {options.seller_type.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label>Vehicle Age (Years)</Label>
                <Input type="number" min={0} value={form.vehicle_age} onChange={(e) => setForm({ ...form, vehicle_age: Number(e.target.value) })} />
              </div>
              <div className="space-y-2">
                <Label>Km Driven</Label>
                <Input type="number" min={0} value={form.km_driven} onChange={(e) => setForm({ ...form, km_driven: Number(e.target.value) })} />
              </div>
              <div className="space-y-2">
                <Label>Mileage (kmpl)</Label>
                <Input type="number" step="0.1" min={0} value={form.mileage} onChange={(e) => setForm({ ...form, mileage: Number(e.target.value) })} />
              </div>
              <div className="space-y-2">
                <Label>Engine (cc)</Label>
                <Input type="number" min={0} value={form.engine} onChange={(e) => setForm({ ...form, engine: Number(e.target.value) })} />
              </div>
              <div className="space-y-2">
                <Label>Max Power (bhp)</Label>
                <Input type="number" step="0.1" min={0} value={form.max_power} onChange={(e) => setForm({ ...form, max_power: Number(e.target.value) })} />
              </div>
              <div className="space-y-2">
                <Label>Seats</Label>
                <Input type="number" min={1} value={form.seats} onChange={(e) => setForm({ ...form, seats: Number(e.target.value) })} />
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between border-t p-6">
            <Button variant="outline" onClick={handleReset}>
              <RotateCcw className="mr-2 h-4 w-4" /> Reset
            </Button>
            <Button 
              onClick={handlePredict} 
              disabled={predictMutation.isPending || !form.brand || !form.model || !form.fuel_type || !form.transmission_type || !form.seller_type}
            >
              {predictMutation.isPending ? "Calculating..." : "Predict Price"} <Sparkles className="ml-2 h-4 w-4" />
            </Button>
          </CardFooter>
        </Card>

        <div>
          <AnimatePresence mode="wait">
            {predictMutation.isError && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}>
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Error</AlertTitle>
                  <AlertDescription>Failed to predict price. Please check inputs.</AlertDescription>
                </Alert>
              </motion.div>
            )}

            {predictMutation.data && (
              <motion.div
                key="result"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="space-y-6"
              >
                <Card className="border-primary bg-primary/5">
                  <CardHeader>
                    <CardTitle className="text-primary">Predicted Price</CardTitle>
                    <CardDescription>Estimated market value</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-4xl font-bold text-primary">
                      {formatCurrency(predictMutation.data.predicted_price)}
                    </div>
                    <div className="text-sm text-muted-foreground mt-2">
                      Expected Range: {formatCurrency(predictMutation.data.price_range.low)} – {formatCurrency(predictMutation.data.price_range.high)}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>

          {similarMutation.data && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 space-y-4"
            >
              <h3 className="font-semibold text-lg">Similar Cars in Market</h3>
              <div className="grid gap-3">
                {similarMutation.data.items.slice(0, 4).map((car, idx) => (
                  <Card key={idx} className="overflow-hidden">
                    <div className="p-4 flex justify-between items-center bg-card">
                      <div>
                        <div className="font-medium">{car.brand} {car.model}</div>
                        <div className="text-xs text-muted-foreground">
                          {new Date().getFullYear() - car.vehicle_age} • {car.km_driven.toLocaleString()} km • {car.fuel_type}
                        </div>
                      </div>
                      <div className="font-bold text-sm">
                        {formatCurrency(car.selling_price)}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
