import { enforcePublicRateLimit } from "@/lib/public-rate-limit";

export async function POST(request: Request) {
 const limited = enforcePublicRateLimit(request, "research", 3, 60 * 60 * 1000);
 if (limited) return limited;
 let payload: unknown;
 try { payload=await request.json(); } catch { return Response.json({error:'Invalid JSON'}, {status:400}); }
 const base=(process.env.BACKEND_URL||'http://127.0.0.1:8000').replace(/\/$/,'');
 try {
  const response=await fetch(`${base}/research`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(160000)});
  const data=await response.json() as {research_id?:string;detail?:unknown};
  if(!response.ok)return Response.json(data,{status:response.status});
  if(!data.research_id)return Response.json({error:'Research did not return a report ID'},{status:502});
  const report=await fetch(`${base}/research/${encodeURIComponent(data.research_id)}`,{signal:AbortSignal.timeout(10000)});
  return Response.json(await report.json(),{status:report.status});
 }catch{return Response.json({error:'Research backend unavailable or timed out. Check the server and provider configuration.'},{status:503});}
}
