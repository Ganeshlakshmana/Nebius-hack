export type ComponentAnalysis = {
 status:string; component?:string; methodology?:string; limitations?:string[];
 items?:{supplier_id:string;company:string;rank:number|null;component_score:number|null;original_total_risk:number;
 decision:string;factors:{column:string;score:number;weight:number;contribution:number}[];
 critical_factors:{column:string;score:number}[];required_checks:string[]}[];
};
export function ComponentAnalysisCards({analysis}:{analysis:ComponentAnalysis}) {
 if(analysis.status!=="complete")return null;
 return <div className="component-analysis"><h3>{analysis.component}</h3><p>{analysis.methodology}</p>{analysis.items?.map(item=><article key={item.supplier_id}>
 <header><div><strong>{item.company}</strong><small>{item.supplier_id} · Qualification unverified</small></div><b>{item.component_score??"N/A"}<small>/100</small></b></header>
 <p>{item.rank?`Rank ${item.rank} · `:""}{item.decision}</p>
 <div className="component-factor-head"><span>Risk dimension</span><span>Score × weight</span></div>
 {item.factors.map(f=><div className="component-factor" key={f.column}><span>{f.column.replace(/_Score$/,"").replaceAll("_"," ")}</span><span>{f.score} × {(f.weight*100).toFixed(0)}%</span></div>)}
 {item.critical_factors.length>0&&<p className="component-warning">Critical: {item.critical_factors.map(f=>`${f.column.replace(/_Score$/,"").replaceAll("_"," ")} (${f.score})`).join(", ")}</p>}
 <details><summary>Required component checks</summary><ul>{item.required_checks.map(check=><li key={check}>{check}</li>)}</ul></details>
 <small>Original total risk: {item.original_total_risk} · Source: supplied supplier CSV</small></article>)}<p>{analysis.limitations?.join(" ")}</p></div>
}
