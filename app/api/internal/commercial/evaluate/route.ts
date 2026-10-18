import { proxyCommercialRequest } from "@/lib/commercial-webhook-proxy";

export const runtime = "nodejs";

export async function POST(request: Request) {
  return proxyCommercialRequest(request, "evaluate");
}
