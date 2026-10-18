import { timingSafeEqual } from "node:crypto";

const MAX_BODY_BYTES = 128 * 1024;

function authorized(request: Request): boolean | Response {
  const expected = process.env.COMMERCIAL_API_KEY;
  if (!expected) {
    return Response.json({ error: "Commercial integration is not configured." }, { status: 503 });
  }

  const received = request.headers.get("x-railwise-key") ?? "";
  const expectedBytes = Buffer.from(expected, "utf8");
  const receivedBytes = Buffer.from(received, "utf8");
  if (receivedBytes.length !== expectedBytes.length || !timingSafeEqual(receivedBytes, expectedBytes)) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }
  return true;
}

export async function proxyCommercialRequest(request: Request, action: "evaluate" | "scan") {
  const access = authorized(request);
  if (access !== true) return access;

  const backend = (process.env.BACKEND_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  let body: string | undefined;

  if (action === "evaluate") {
    if (!request.headers.get("content-type")?.toLowerCase().includes("application/json")) {
      return Response.json({ error: "Content-Type must be application/json." }, { status: 415 });
    }
    body = await request.text();
    if (Buffer.byteLength(body, "utf8") > MAX_BODY_BYTES) {
      return Response.json({ error: "Commercial request is too large." }, { status: 413 });
    }
    try {
      JSON.parse(body);
    } catch {
      return Response.json({ error: "Invalid JSON" }, { status: 400 });
    }
  }

  try {
    const response = await fetch(`${backend}/commercial/${action}`, {
      method: "POST",
      headers: {
        "X-Railwise-Key": process.env.COMMERCIAL_API_KEY!,
        ...(body ? { "Content-Type": "application/json" } : {}),
      },
      ...(body ? { body } : {}),
      signal: AbortSignal.timeout(action === "scan" ? 65_000 : 25_000),
      cache: "no-store",
    });
    const responseBody = await response.text();
    return new Response(responseBody, {
      status: response.status,
      headers: { "Content-Type": response.headers.get("content-type") || "application/json" },
    });
  } catch {
    return Response.json({ error: "Commercial backend unavailable." }, { status: 503 });
  }
}
