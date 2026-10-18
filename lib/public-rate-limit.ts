type RateWindow = { startedAt: number; count: number };

const windows = new Map<string, RateWindow>();

/** In-memory per-client guard for the single-instance hackathon demo. */
export function enforcePublicRateLimit(
  request: Request,
  key: string,
  maxRequests: number,
  windowMs: number,
): Response | null {
  // Caddy overwrites this header with the actual peer address before proxying.
  const client = request.headers.get("x-real-ip")?.trim() || "unknown-client";
  const bucketKey = `${key}:${client}`;
  const now = Date.now();
  let window = windows.get(bucketKey);

  if (!window || now - window.startedAt >= windowMs) {
    window = { startedAt: now, count: 0 };
    windows.set(bucketKey, window);
  }

  if (window.count >= maxRequests) {
    const retryAfter = Math.max(1, Math.ceil((window.startedAt + windowMs - now) / 1000));
    return Response.json(
      { error: "Demo request limit reached. Please wait before trying again.", retry_after_seconds: retryAfter },
      { status: 429, headers: { "Retry-After": String(retryAfter), "Cache-Control": "no-store" } },
    );
  }

  window.count += 1;

  // Bound memory even if the public demo receives requests from many addresses.
  if (windows.size > 5000) {
    for (const [entryKey, entry] of windows) {
      if (now - entry.startedAt >= windowMs) windows.delete(entryKey);
      if (windows.size <= 4000) break;
    }
  }

  return null;
}
