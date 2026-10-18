export async function POST(request: Request) {
  let payload: unknown;
  try { payload = await request.json(); }
  catch { return Response.json({error:"Invalid JSON request"}, {status:400}); }
  try {
    const base = process.env.BACKEND_URL || "http://127.0.0.1:8000";
    const response = await fetch(`${base.replace(/\/$/, "")}/chat`, {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify(payload), signal:AbortSignal.timeout(20000),
    });
    return Response.json(await response.json(), {status:response.status});
  } catch {
    return Response.json({error:"Backend unavailable. Start the FastAPI server on port 8000 or configure BACKEND_URL."}, {status:503});
  }
}
