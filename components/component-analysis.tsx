export type ComponentAnalysis = {
 decision_brief?:{ranking_stability:string;sensitivity_method:string;qualification_coverage:string;buyer_actions:{owner:string;request:string;status:string}[]};
 status:string; component?:string; methodology?:string; limitations?:string[];
 items?:{supplier_id:string;company:string;rank:number|null;component_score:number|null;original_total_risk:number;
 sensitivity?:{top_rank_scenarios:number;scenarios_tested:number};dominated_by?:string[];
 decision:string;factors:{column:string;score:number;weight:number;contribution:number}[];
 critical_factors:{column:string;score:number}[];required_checks:string[]}[];
};
export function ComponentAnalysisCards({analysis}:{analysis:ComponentAnalysis}) {
 if(analysis.status!=="complete")return null;
 return <div className="component-analysis"><h3>{analysis.component}</h3><p>{analysis.methodology}</p>{analysis.decision_brief&&<article><h3>Decision readiness · Evidence required</h3><p>{analysis.decision_brief.qualification_coverage}. This shortlist is not ready for a contract award.</p><p>Ranking: {analysis.decision_brief.ranking_stability.replaceAll("_"," ")}</p><details><summary>What could change this decision?</summary><p>{analysis.decision_brief.sensitivity_method}</p><ul>{analysis.decision_brief.buyer_actions.map(action=><li key={action.owner}><strong>{action.owner}:</strong> {action.request}</li>)}</ul></details></article>}{analysis.items?.map(item=><article key={item.supplier_id}>
 <header><div><strong>{item.company}</strong><small>{item.supplier_id} · Qualification unverified</small></div><b>{item.component_score??"N/A"}<small>/100</small></b></header>
 <p>{item.rank?`Rank ${item.rank} · `:""}{item.decision}</p>
 <div className="component-factor-head"><span>Risk dimension</span><span>Score × weight</span></div>
 {item.factors.map(f=><div className="component-factor" key={f.column}><span>{f.column.replace(/_Score$/,"").replaceAll("_"," ")}</span><span>{f.score} × {(f.weight*100).toFixed(0)}%</span></div>)}
 {item.critical_factors.length>0&&<p className="component-warning">Critical: {item.critical_factors.map(f=>`${f.column.replace(/_Score$/,"").replaceAll("_"," ")} (${f.score})`).join(", ")}</p>}
 {item.sensitivity&&<p>Top rank in {item.sensitivity.top_rank_scenarios}/{item.sensitivity.scenarios_tested} weight scenarios · not a probability</p>}
 {!!item.dominated_by?.length&&<p>Lower or equal risk on every selected dimension: {item.dominated_by.join(", ")}. Component suitability remains unverified.</p>}
 <details><summary>Required component checks</summary><ul>{item.required_checks.map(check=><li key={check}>{check}</li>)}</ul></details>
 <small>Original total risk: {item.original_total_risk} · Source: supplied supplier CSV</small></article>)}<p>{analysis.limitations?.join(" ")}</p></div>
}
