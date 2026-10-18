"use client";
import {Button} from "@/components/ui/button";
export type ChatArtifactData={
 tables?:{title:string;columns:string[];rows:string[][]}[];
 sources?:{label:string;url:string}[];
 supplier_ids?:string[];
 memo_html?:string;
 navigate_to?:string;
 supervisor_status?:string;
};
export function ChatArtifacts({data,onNavigate,onAddSuppliers,onCompareSuppliers}:{data:ChatArtifactData;onNavigate:(view:string)=>void;onAddSuppliers:(ids:string[])=>void;onCompareSuppliers:(ids:string[])=>void}){
 function downloadMemo(){if(!data.memo_html)return;const url=URL.createObjectURL(new Blob([data.memo_html],{type:"text/html"}));const a=document.createElement("a");a.href=url;a.download="railwise-shortlist-memo.html";a.click();URL.revokeObjectURL(url)}
 return <div className="chat-artifacts">
 {!!data.supplier_ids?.length&&<div className="chat-result-actions"><Button variant="outline" onClick={()=>onAddSuppliers(data.supplier_ids!)}>Add {data.supplier_ids.length} to shortlist</Button><Button onClick={()=>onCompareSuppliers(data.supplier_ids!)}>Compare these {data.supplier_ids.length}</Button></div>}
 {data.tables?.map((table,i)=><div className="table-scroll" key={i}><strong>{table.title}</strong><table><thead><tr>{table.columns.map((c,j)=><th key={j}>{c}</th>)}</tr></thead><tbody>{table.rows.map((row,j)=><tr key={j}>{row.map((cell,k)=><td key={k}>{cell}</td>)}</tr>)}</tbody></table></div>)}
 {data.sources?.length?<details><summary>{data.sources.length} evidence sources</summary><ul>{data.sources.filter(s=>/^https?:\/\//i.test(s.url)).map((s,i)=><li key={i}><a href={s.url} target="_blank" rel="noreferrer">{s.label} ↗</a></li>)}</ul></details>:null}
 {data.memo_html&&<Button onClick={downloadMemo}>Download draft memo</Button>}
 {data.navigate_to&&["Research","Commercial","Sourcing"].includes(data.navigate_to)&&<Button variant="outline" onClick={()=>onNavigate(data.navigate_to!)}>Open {data.navigate_to}</Button>}
 </div>
}
