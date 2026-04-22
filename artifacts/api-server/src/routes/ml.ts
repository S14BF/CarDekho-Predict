import { Router, type IRouter, type Request, type Response } from "express";

const router: IRouter = Router();

const FLASK_BASE = process.env["FLASK_URL"] ?? "http://127.0.0.1:5000";

async function proxy(req: Request, res: Response, targetPath: string) {
  const url = `${FLASK_BASE}${targetPath}`;
  const init: RequestInit = {
    method: req.method,
    headers: { "content-type": "application/json" },
  };
  if (req.method !== "GET" && req.method !== "HEAD") {
    init.body = JSON.stringify(req.body ?? {});
  }
  try {
    const upstream = await fetch(url, init);
    const text = await upstream.text();
    res.status(upstream.status);
    const ct = upstream.headers.get("content-type");
    if (ct) res.setHeader("content-type", ct);
    res.send(text);
  } catch (err) {
    req.log.error({ err, url }, "Flask proxy error");
    res.status(502).json({ error: "Backend ML service unavailable" });
  }
}

router.get("/health", (req, res) => proxy(req, res, "/health"));
router.get("/options", (req, res) => proxy(req, res, "/options"));
router.get("/insights", (req, res) => proxy(req, res, "/insights"));
router.post("/predict", (req, res) => proxy(req, res, "/predict"));
router.post("/similar", (req, res) => proxy(req, res, "/similar"));

export default router;
