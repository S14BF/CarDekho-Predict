import { useState } from "react";
import { useGetOptions, usePredict, PredictRequest } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Scale, CheckCircle2 } from "lucide-react";

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

function CarForm({
  title,
  form,
  setForm,
  optionsData
}: {
  title: string,
  form: PredictRequest,
  setForm: (v: PredictRequest) => void,
  optionsData: any
}) {
  const { options, brand_models } = optionsData;
  const availableModels = form.brand && brand_models[form.brand] ? brand_models[form.brand] : [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Brand</Label>
            <Select value={form.brand} onValueChange={(val) => setForm({ ...form, brand: val, model: "" })}>
              <SelectTrigger><SelectValue placeholder="Select Brand" /></SelectTrigger>
              <SelectContent>
                {options.brand.map((b: string) => <SelectItem key={b} value={b}>{b}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Model</Label>
            <Select value={form.model} onValueChange={(val) => setForm({ ...form, model: val })} disabled={!form.brand}>
              <SelectTrigger><SelectValue placeholder="Select Model" /></SelectTrigger>
              <SelectContent>
                {availableModels.map((m: string) => <SelectItem key={m} value={m}>{m}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Fuel</Label>
            <Select value={form.fuel_type} onValueChange={(val) => setForm({ ...form, fuel_type: val })}>
              <SelectTrigger><SelectValue placeholder="Fuel" /></SelectTrigger>
              <SelectContent>
                {options.fuel_type.map((f: string) => <SelectItem key={f} value={f}>{f}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Transmission</Label>
            <Select value={form.transmission_type} onValueChange={(val) => setForm({ ...form, transmission_type: val })}>
              <SelectTrigger><SelectValue placeholder="Transmission" /></SelectTrigger>
              <SelectContent>
                {options.transmission_type.map((t: string) => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Age (Yrs)</Label>
            <Input type="number" min={0} value={form.vehicle_age} onChange={(e) => setForm({ ...form, vehicle_age: Number(e.target.value) })} />
          </div>
          <div className="space-y-2">
            <Label>Km Driven</Label>
            <Input type="number" min={0} value={form.km_driven} onChange={(e) => setForm({ ...form, km_driven: Number(e.target.value) })} />
          </div>
        </div>
        {/* Simplified for space, default the rest in state or add if needed */}
        <div className="space-y-2">
            <Label>Seller Type</Label>
            <Select value={form.seller_type} onValueChange={(val) => setForm({ ...form, seller_type: val })}>
              <SelectTrigger><SelectValue placeholder="Seller Type" /></SelectTrigger>
              <SelectContent>
                {options.seller_type.map((s: string) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
      </CardContent>
    </Card>
  );
}

export default function Compare() {
  const { data: optionsData, isLoading } = useGetOptions();
  const predictMutationA = usePredict();
  const predictMutationB = usePredict();

  const [carA, setCarA] = useState<PredictRequest>(defaultValues);
  const [carB, setCarB] = useState<PredictRequest>(defaultValues);

  const handleCompare = async () => {
    if (!carA.brand || !carB.brand) return;
    await Promise.all([
      predictMutationA.mutateAsync(carA),
      predictMutationB.mutateAsync(carB)
    ]);
  };

  if (isLoading || !optionsData) return <div className="p-8"><Skeleton className="h-[400px] w-full" /></div>;

  const resultA = predictMutationA.data;
  const resultB = predictMutationB.data;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Compare Cars</h1>
        <p className="text-muted-foreground mt-2">Evaluate two different configurations side-by-side.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <CarForm title="Car A" form={carA} setForm={setCarA} optionsData={optionsData} />
        <CarForm title="Car B" form={carB} setForm={setCarB} optionsData={optionsData} />
      </div>

      <div className="flex justify-center">
        <Button size="lg" onClick={handleCompare} disabled={predictMutationA.isPending || predictMutationB.isPending}>
          <Scale className="mr-2 h-5 w-5" /> Compare Both
        </Button>
      </div>

      {resultA && resultB && (
        <Card className="mt-8 border-primary/20">
          <CardHeader>
            <CardTitle>Comparison Results</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-1/3">Feature</TableHead>
                  <TableHead className="w-1/3">Car A ({carA.brand} {carA.model})</TableHead>
                  <TableHead className="w-1/3">Car B ({carB.brand} {carB.model})</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell className="font-semibold">Predicted Price</TableCell>
                  <TableCell className={resultA.predicted_price > resultB.predicted_price ? "text-muted-foreground" : "text-primary font-bold"}>
                    {formatCurrency(resultA.predicted_price)}
                  </TableCell>
                  <TableCell className={resultB.predicted_price > resultA.predicted_price ? "text-muted-foreground" : "text-primary font-bold"}>
                    {formatCurrency(resultB.predicted_price)}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Price Range</TableCell>
                  <TableCell>{formatCurrency(resultA.price_range.low)} - {formatCurrency(resultA.price_range.high)}</TableCell>
                  <TableCell>{formatCurrency(resultB.price_range.low)} - {formatCurrency(resultB.price_range.high)}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Age / Km Driven</TableCell>
                  <TableCell>{carA.vehicle_age} yrs / {carA.km_driven.toLocaleString()} km</TableCell>
                  <TableCell>{carB.vehicle_age} yrs / {carB.km_driven.toLocaleString()} km</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Fuel / Transmission</TableCell>
                  <TableCell>{carA.fuel_type} / {carA.transmission_type}</TableCell>
                  <TableCell>{carB.fuel_type} / {carB.transmission_type}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
            
            <div className="mt-6 p-4 bg-muted rounded-lg flex items-start gap-3">
              <CheckCircle2 className="h-5 w-5 text-primary mt-0.5" />
              <div>
                <h4 className="font-semibold">Verdict</h4>
                <p className="text-muted-foreground">
                  {resultA.predicted_price > resultB.predicted_price 
                    ? `Car B is cheaper by ${formatCurrency(resultA.predicted_price - resultB.predicted_price)}.`
                    : `Car A is cheaper by ${formatCurrency(resultB.predicted_price - resultA.predicted_price)}.`}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
