"use client";
import {Button} from "@/components/ui/button";
export type ChatArtifactData={
 agent_trace?:{agent:string;status:string}[];
 tables?:{title:string;columns:string[];rows:string[][]}[];
 sources?:{label:string;url:string}[];
 memo_html?:string;
 navigate_to?:string;
 supervisor_status?:string;
};
export function ChatArtifacts({data,onNavigate}:{data:ChatArtifactData;onNavigate:(view:string)=>void}){
 function downloadMemo(){if(!data.memo_html)return;const url=URL.createObjectURL(new Blob([data.memo_html],{type:"text/html"}));const a=document.createElement("a");a.href=url;a.download="railwise-shortlist-memo.html";a.click();URL.revokeObjectURL(url)}
 return <div className="chat-artifacts">
 {data.agent_trace?.length? <div className="chat-agent-trace" aria-label="Agents used">{data.agent_trace.map((a,i)=><span key={i}>{a.agent} · {a.status}</span>)}</div>:null}
 {data.supervisor_status==="model_unavailable"&&<small>Conversational model unavailable · limited dataset fallback</small>}
 {data.tables?.map((table,i)=><div className="table-scroll" key={i}><strong>{table.title}</strong><table><thead><tr>{table.columns.map((c,j)=><th key={j}>{c}</th>)}</tr></thead><tbody>{table.rows.map((row,j)=><tr key={j}>{row.map((cell,k)=><td key={k}>{cell}</td>)}</tr>)}</tbody></table></div>)}
 {data.sources?.length?<details><summary>{data.sources.length} evidence sources</summary><ul>{data.sources.filter(s=>/^https?:\/\//i.test(s.url)).map((s,i)=><li key={i}><a href={s.url} target="_blank" rel="noreferrer">{s.label} ↗</a></li>)}</ul></details>:null}
 {data.memo_html&&<Button onClick={downloadMemo}>Download draft memo</Button>}
 {data.navigate_to&&["Research","Commercial","Sourcing"].includes(data.navigate_to)&&<Button variant="outline" onClick={()=>onNavigate(data.navigate_to!)}>Open {data.navigate_to}</Button>}
 </div>
}
