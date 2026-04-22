# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.

## Python Flask Backend (Used Car Price Prediction)

- Location: `backend/`
- Files: `app.py`, `requirements.txt`, `cardekho.csv`
- Runtime: Python 3.11
- Workflow: `Flask Backend` (port 5000)
- Trains a `RandomForestRegressor` on `cardekho.csv` at startup.
- Endpoints:
  - `GET /` — service info + model metrics
  - `GET /health` — liveness + metrics
  - `GET /options` — available brands/models/fuels/etc. for dropdowns
  - `POST /predict` — body: `{brand, model, seller_type, fuel_type, transmission_type, vehicle_age, km_driven, mileage, engine, max_power, seats}` → predicted price + range
