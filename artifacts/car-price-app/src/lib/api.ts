import { useQuery, useMutation } from "@tanstack/react-query";

const BASE_URL = "/api/ml";

export type PredictRequest = {
  brand: string;
  model: string;
  seller_type: string;
  fuel_type: string;
  transmission_type: string;
  vehicle_age: number;
  km_driven: number;
  mileage: number;
  engine: number;
  max_power: number;
  seats: number;
};

export type PredictResponse = {
  predicted_price: number;
  price_range: { low: number; high: number };
  currency: string;
  model_metrics: any;
};

export type SimilarRequest = {
  target_price: number;
};

export type SimilarResponse = {
  items: Array<{
    car_name: string;
    brand: string;
    model: string;
    vehicle_age: number;
    km_driven: number;
    fuel_type: string;
    transmission_type: string;
    selling_price: number;
  }>;
};

export type OptionsResponse = {
  options: {
    brand: string[];
    model: string[];
    seller_type: string[];
    fuel_type: string[];
    transmission_type: string[];
  };
  brand_models: Record<string, string[]>;
};

export type InsightsResponse = {
  totals: {
    rows: number;
    average_price: number;
    median_price: number;
    most_popular_brand: string;
  };
  by_brand: Array<{ brand: string; average_price: number; count: number }>;
  by_fuel: Array<{ fuel_type: string; average_price: number }>;
  by_age: Array<{ vehicle_age: number; average_price: number }>;
  by_transmission: Array<{ transmission_type: string; average_price: number }>;
};

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }
  return response.json();
}

export function useGetOptions() {
  return useQuery({
    queryKey: ["options"],
    queryFn: () => fetchApi<OptionsResponse>("/options"),
  });
}

export function useGetInsights() {
  return useQuery({
    queryKey: ["insights"],
    queryFn: () => fetchApi<InsightsResponse>("/insights"),
  });
}

export function usePredict() {
  return useMutation({
    mutationFn: (data: PredictRequest) =>
      fetchApi<PredictResponse>("/predict", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  });
}

export function useSimilar() {
  return useMutation({
    mutationFn: (data: SimilarRequest) =>
      fetchApi<SimilarResponse>("/similar", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  });
}
