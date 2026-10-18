import { enforcePublicRateLimit } from "@/lib/public-rate-limit";

export async function POST(request: Request) {
 const limited = enforcePublicRateLimit(request, "commercial", 12, 10 * 60 * 1000);
 if (limited) return limited;
 let payload:unknown;
 try {payload=await request.json();}catch{return Response.json({error:"Invalid JSON"},{status:400})}
 const webhook=process.env.N8N_COMMERCIAL_WEBHOOK;
 const url=webhook || (process.env.BACKEND_URL||"http://127.0.0.1:8000").replace(/\/$/,"")+"/commercial/evaluate";
 const key=webhook?process.env.N8N_WEBHOOK_KEY:process.env.COMMERCIAL_API_KEY;
 if(webhook&&(!webhook.startsWith("https://")||!key))return Response.json({error:"n8n requires HTTPS and a server-side webhook credential."},{status:503});
 try{
  const response=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json",...(key?{"X-Railwise-Key":key}:{})},body:JSON.stringify(payload),signal:AbortSignal.timeout(25000)});
  const data=await response.json() as {options?:unknown;candidates?:unknown;alerts?:unknown};
  if(response.ok&&(!Array.isArray(data.options)||!Array.isArray(data.candidates)||!Array.isArray(data.alerts)))return Response.json({error:"Workflow returned no valid commercial report."},{status:502});
  return Response.json(data,{status:response.status});
 }catch{return Response.json({error:"Commercial evaluation unavailable. No successful evaluation is being claimed."},{status:503})}
}
export async function GET(){
 try{
  const key=process.env.COMMERCIAL_API_KEY;
  const response=await fetch((process.env.BACKEND_URL||"http://127.0.0.1:8000").replace(/\/$/,"")+"/commercial/alerts",{headers:key?{"X-Railwise-Key":key}:{},signal:AbortSignal.timeout(10000)});
  return Response.json(await response.json(),{status:response.status});
 }catch{return Response.json({error:"Contract monitor unavailable"},{status:503})}
}
