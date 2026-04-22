import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Trash2, Eye, History as HistoryIcon } from "lucide-react";
import { format } from "date-fns";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

type HistoryEntry = {
  id: number;
  date: string;
  car: string;
  predicted_price: number;
  inputs: Record<string, any>;
};

const formatCurrency = (val: number) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(val);

export default function History() {
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  useEffect(() => {
    const data = localStorage.getItem("carapp_history");
    if (data) {
      setHistory(JSON.parse(data).sort((a: any, b: any) => b.id - a.id));
    }
  }, []);

  const handleDelete = (id: number) => {
    const updated = history.filter((h) => h.id !== id);
    setHistory(updated);
    localStorage.setItem("carapp_history", JSON.stringify(updated));
  };

  const handleClear = () => {
    setHistory([]);
    localStorage.removeItem("carapp_history");
  };

  if (history.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-4">
        <div className="h-20 w-20 bg-muted rounded-full flex items-center justify-center">
          <HistoryIcon className="h-10 w-10 text-muted-foreground" />
        </div>
        <h2 className="text-2xl font-bold">No History Yet</h2>
        <p className="text-muted-foreground max-w-sm">
          You haven't made any predictions. Go to the Predict page to estimate your first car's value.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Prediction History</h1>
          <p className="text-muted-foreground mt-2">Review your past price estimates.</p>
        </div>
        <Button variant="destructive" onClick={handleClear}>
          Clear History
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Car</TableHead>
                <TableHead>Predicted Price</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {history.map((entry) => (
                <TableRow key={entry.id}>
                  <TableCell>{format(new Date(entry.date), "MMM d, yyyy HH:mm")}</TableCell>
                  <TableCell className="font-medium">{entry.car}</TableCell>
                  <TableCell className="text-primary font-semibold">{formatCurrency(entry.predicted_price)}</TableCell>
                  <TableCell className="text-right">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="ghost" size="icon" title="View details">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>{entry.car} Details</DialogTitle>
                        </DialogHeader>
                        <div className="grid grid-cols-2 gap-4 py-4">
                          {Object.entries(entry.inputs).map(([key, value]) => (
                            <div key={key}>
                              <span className="text-xs text-muted-foreground uppercase font-semibold">{key.replace('_', ' ')}</span>
                              <p className="font-medium">{String(value)}</p>
                            </div>
                          ))}
                        </div>
                      </DialogContent>
                    </Dialog>
                    <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive hover:bg-destructive/10" onClick={() => handleDelete(entry.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
