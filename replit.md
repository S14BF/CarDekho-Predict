# Used Car Price Predictor

College PSDL project. Predicts resale prices for used cars in India using machine learning.

## Architecture
- **Flask Backend** (`backend/app.py`, port 5000) — RandomForestRegressor trained on `cardekho.csv` (15411 rows, R²=0.94, MAE≈₹99k). Endpoints: `/health`, `/options`, `/insights`, `/predict`, `/similar`.
- **Express API Server** (`artifacts/api-server`, port 8080) — proxies `/api/ml/*` to the Flask backend.
- **React Frontend** (`artifacts/car-price-app`) — Vite + React + Tailwind + shadcn/ui + wouter + TanStack Query + recharts + framer-motion.

## Frontend pages
- `/login` — local auth (username/password stored in localStorage).
- `/` — Dashboard with stat cards and quick nav.
- `/predict` — Main prediction form with similar-car suggestions, saves to history.
- `/compare` — Side-by-side comparison of two cars.
- `/analysis` — Charts (top brands, fuel, age depreciation, transmission).
- `/history` — Past predictions saved in localStorage.

## Run
All workflows auto-start: Flask Backend, API Server, Car Price App.
