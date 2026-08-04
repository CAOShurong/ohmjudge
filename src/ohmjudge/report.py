from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import GradeRecord
from .stats import summarize


def render_report(
    records: list[GradeRecord],
    output: str | Path,
    *,
    title: str = "OhmJudge benchmark report",
    note: str = "",
    suite_commitment: str = "",
    price_metadata: list[dict[str, Any]] | None = None,
) -> Path:
    if not records:
        raise ValueError("cannot render an empty report")
    data = {
        "title": title,
        "note": note,
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "suite_commitment": suite_commitment,
        "summary": summarize(records),
        "records": [record.to_dict() for record in records],
        "prices": price_metadata or [],
    }
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )
    html = _REPORT_HTML.replace("__DATA__", payload)
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding="utf-8")
    return destination


_REPORT_HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OhmJudge report</title>
<style>
:root{--bg:#fbfaf7;--panel:#fff;--line:#d3d0c8;--ink:#172630;--muted:#64727a;--blue:#2f6f9f;--navy:#15324b;--rust:#b65d3a;--green:#55723b;--red:#a3483e}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 Inter,ui-sans-serif,system-ui,sans-serif}.shell{max-width:1240px;margin:auto;padding:32px}.hero{display:flex;justify-content:space-between;gap:24px;align-items:flex-end;margin-bottom:22px;padding-bottom:22px;border-bottom:1px solid var(--line)}.kicker{color:var(--blue);font-weight:850;letter-spacing:.14em;text-transform:uppercase;font-size:11px}h1{font-family:Georgia,Times New Roman,serif;font-size:38px;line-height:1.1;margin:7px 0}.subtitle{color:var(--muted);max-width:770px}.stamp{color:var(--muted);font-size:12px;text-align:right}.notice{border:1px solid #d2b59a;background:#f8f0e8;color:#6e422c;padding:11px 14px;margin:16px 0}.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:12px}.card{background:var(--panel);border:1px solid var(--line);border-radius:3px;padding:18px}.kpi{grid-column:span 3;border-top:3px solid var(--blue)}.kpi strong{display:block;font-family:Georgia,Times New Roman,serif;font-size:30px;margin:5px 0}.kpi small,.muted{color:var(--muted)}.scatter{grid-column:span 7}.matrix{grid-column:span 5}.errors{grid-column:span 4}.models{grid-column:span 8}.results{grid-column:1/-1}h2{font-family:Georgia,Times New Roman,serif;font-size:18px;margin:0 0 14px}.badge{display:inline-flex;border:1px solid #aebd9d;background:#eef3ea;padding:4px 9px;color:#42552e;font-size:11px}svg{width:100%;height:315px;overflow:visible}.axis{stroke:#849198;stroke-width:1}.gridline{stroke:#e0ddd6;stroke-width:1;stroke-dasharray:3 5}.dot{stroke:#fff;stroke-width:2}.label{fill:var(--ink);font-size:11px}.tick{fill:var(--muted);font-size:10px}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:9px 8px;border-bottom:1px solid #e2e0da}th{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.08em}.bar{height:6px;background:#e7e5df;overflow:hidden;min-width:80px}.bar i{display:block;height:100%;background:var(--blue)}.heat{display:grid;gap:7px}.heat-row{display:grid;grid-template-columns:120px repeat(var(--cols),1fr);gap:6px;align-items:center}.cell{border-radius:2px;text-align:center;padding:9px 4px;font-weight:800;color:#172630}.legend{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}.model-key{display:flex;align-items:center;gap:6px;color:var(--muted)}.swatch{width:9px;height:9px}.error-row{display:grid;grid-template-columns:110px 1fr 34px;gap:8px;align-items:center;margin:10px 0}.error-row .bar i{background:var(--rust)}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}.filters input,.filters select{background:#fff;color:var(--ink);border:1px solid #b9b7b0;border-radius:2px;padding:8px 10px}.table-wrap{overflow:auto;max-height:520px}.status{font-weight:850}.status.ok{color:var(--green)}.status.bad{color:var(--red)}.mono{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:12px}.foot{color:var(--muted);font-size:12px;margin-top:18px;word-break:break-all}
@media(max-width:900px){.kpi{grid-column:span 6}.scatter,.matrix,.errors,.models{grid-column:1/-1}}@media(max-width:560px){.shell{padding:16px}.hero{display:block}.stamp{text-align:left;margin-top:12px}.kpi{grid-column:1/-1}.heat-row{grid-template-columns:90px repeat(var(--cols),70px);overflow:auto}}
</style></head><body><main class="shell">
<header class="hero"><div><div class="kicker">Ω OhmJudge / executable EE evaluation</div><h1 id="title"></h1><div id="subtitle" class="subtitle"></div></div><div class="stamp"><span class="badge">deterministic grading</span><br><span id="created"></span></div></header>
<div id="notice" class="notice" hidden></div>
<section class="grid">
<div class="card kpi"><small>Models compared</small><strong id="modelCount"></strong><span class="muted">same generated suite</span></div>
<div class="card kpi"><small>Responses graded</small><strong id="responseCount"></strong><span class="muted">no LLM judge</span></div>
<div class="card kpi"><small>Best accuracy</small><strong id="bestAccuracy"></strong><span id="bestModel" class="muted"></span></div>
<div class="card kpi"><small>Pareto frontier</small><strong id="paretoCount"></strong><span class="muted">cost ↓ / quality ↑</span></div>
<div class="card scatter"><h2>Cost × accuracy</h2><svg id="scatter" viewBox="0 0 680 315" role="img" aria-label="Cost versus accuracy scatter plot"></svg><div id="legend" class="legend"></div></div>
<div class="card matrix"><h2>Domain accuracy</h2><div id="matrix" class="heat"></div></div>
<div class="card models"><h2>Model scorecard</h2><div class="table-wrap"><table><thead><tr><th>Model</th><th>Accuracy</th><th>95% interval</th><th>Median latency</th><th>Total cost</th></tr></thead><tbody id="models"></tbody></table></div></div>
<div class="card errors"><h2>Error taxonomy</h2><div id="errors"></div></div>
<div class="card results"><h2>Auditable result rows</h2><div class="filters"><input id="search" placeholder="Search model or task"><select id="pack"><option value="">All domains</option></select><select id="outcome"><option value="">All outcomes</option><option value="correct">Correct</option><option value="wrong">Incorrect</option></select></div><div class="table-wrap"><table><thead><tr><th>Model</th><th>Domain</th><th>Task</th><th>Result</th><th>Observed</th><th>Expected</th></tr></thead><tbody id="rows"></tbody></table></div></div>
</section><div class="foot">Suite commitment: <code id="commitment"></code></div>
</main>
<script>
const D=__DATA__, S=D.summary, colors=["#2f6f9f","#b65d3a","#55723b","#76527b","#c08a27","#548b8e","#7b6c55"];
const pct=x=>(100*x).toFixed(1)+"%", money=x=>x==null?"not priced":"$"+x.toFixed(x<.01?5:3), latency=x=>x==null?"—":Math.round(x)+" ms", esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
document.title=D.title;document.getElementById("title").textContent=D.title;document.getElementById("subtitle").textContent=D.note||"Freshly generated EE tasks, deterministic validators, and provider-neutral result records.";document.getElementById("created").textContent=new Date(D.created_at).toLocaleString();if(D.note){const n=document.getElementById("notice");n.hidden=false;n.textContent=D.note}
document.getElementById("modelCount").textContent=S.model_count;document.getElementById("responseCount").textContent=S.record_count;const best=[...S.models].sort((a,b)=>b.accuracy-a.accuracy)[0];document.getElementById("bestAccuracy").textContent=pct(best.accuracy);document.getElementById("bestModel").textContent=best.model;document.getElementById("paretoCount").textContent=S.pareto.length;document.getElementById("commitment").textContent=D.suite_commitment||"not supplied";
document.getElementById("models").innerHTML=S.models.map((m,i)=>`<tr><td><span class="swatch" style="display:inline-block;background:${colors[i%colors.length]}"></span> <strong>${esc(m.model)}</strong><br><small class="muted">${esc(m.provider)}</small></td><td>${pct(m.accuracy)}<div class="bar"><i style="width:${100*m.accuracy}%"></i></div></td><td>${pct(m.ci95_low)}–${pct(m.ci95_high)}</td><td>${latency(m.median_latency_ms)}</td><td>${money(m.total_cost)}</td></tr>`).join("");
const packs=S.packs, matrix=document.getElementById("matrix");matrix.style.setProperty("--cols",S.models.length);matrix.innerHTML=`<div class="heat-row"><span></span>${S.models.map(m=>`<small class="muted">${esc(m.model)}</small>`).join("")}</div>`+packs.map(p=>`<div class="heat-row"><strong>${esc(p)}</strong>${S.models.map(m=>{const a=m.packs[p]?.accuracy??0,light=95-40*a,ink=a>.64?"#fff":"#172630";return`<span class="cell" style="background:hsl(204 45% ${light}%);color:${ink}">${pct(a)}</span>`}).join("")}</div>`).join("");
const errorTotals={};for(const r of D.records)errorTotals[r.error_type]=(errorTotals[r.error_type]||0)+1;const maxErr=Math.max(...Object.values(errorTotals),1);document.getElementById("errors").innerHTML=Object.entries(errorTotals).sort((a,b)=>b[1]-a[1]).map(([k,v])=>`<div class="error-row"><span>${esc(k.replaceAll("_"," "))}</span><div class="bar"><i style="width:${100*v/maxErr}%"></i></div><strong>${v}</strong></div>`).join("");
const svg=document.getElementById("scatter"),priced=S.models.filter(m=>m.total_cost!=null),W=680,H=315,pad={l:58,r:30,t:24,b:46},positive=priced.map(m=>m.total_cost).filter(x=>x>0),scale=positive.length?Math.min(...positive)/10:1,maxLog=Math.max(...priced.map(m=>Math.log10(1+m.total_cost/scale)),1),frontier=new Set(S.pareto.map(x=>x.provider+"\0"+x.model));let marks=`<line class="axis" x1="${pad.l}" y1="${H-pad.b}" x2="${W-pad.r}" y2="${H-pad.b}"/><line class="axis" x1="${pad.l}" y1="${pad.t}" x2="${pad.l}" y2="${H-pad.b}"/>`;for(let i=0;i<=4;i++){const y=H-pad.b-i*(H-pad.t-pad.b)/4;marks+=`<line class="gridline" x1="${pad.l}" y1="${y}" x2="${W-pad.r}" y2="${y}"/><text class="tick" x="8" y="${y+4}">${i*25}%</text>`}priced.forEach((m,i)=>{const x=pad.l+(Math.log10(1+m.total_cost/scale)/maxLog)*(W-pad.l-pad.r),y=H-pad.b-m.accuracy*(H-pad.t-pad.b),f=frontier.has(m.provider+"\0"+m.model),edge=x>W-125,tx=edge?x-11:x+11,anchor=edge?"end":"start";marks+=`<circle class="dot" cx="${x}" cy="${y}" r="${f?9:7}" fill="${colors[i%colors.length]}" ${f?'stroke="#fff" stroke-width="3"':""}/><text class="label" x="${tx}" y="${y+4}" text-anchor="${anchor}">${esc(m.model)}</text>`});marks+=`<text class="tick" x="${W/2-78}" y="${H-8}">log-scaled measured cost →</text>`;svg.innerHTML=marks;document.getElementById("legend").innerHTML=S.models.map((m,i)=>`<span class="model-key"><i class="swatch" style="background:${colors[i%colors.length]}"></i>${esc(m.model)}${frontier.has(m.provider+"\0"+m.model)?" · Pareto":""}</span>`).join("");
const packSel=document.getElementById("pack");packSel.innerHTML+=packs.map(p=>`<option>${esc(p)}</option>`).join("");function renderRows(){const q=document.getElementById("search").value.toLowerCase(),p=packSel.value,o=document.getElementById("outcome").value,rows=D.records.filter(r=>(!q||(r.model+" "+r.task_id).toLowerCase().includes(q))&&(!p||r.pack===p)&&(!o||(o==="correct"?r.correct:!r.correct)));document.getElementById("rows").innerHTML=rows.map(r=>`<tr><td><strong>${esc(r.model)}</strong><br><small class="muted">${esc(r.provider)}</small></td><td>${esc(r.pack)}</td><td class="mono">${esc(r.template)}</td><td class="status ${r.correct?"ok":"bad"}">${r.correct?"pass":esc(r.error_type)}</td><td>${r.observed_value==null?"—":esc(r.observed_value)} ${esc(r.observed_unit||"")}</td><td>${esc(r.expected_value)} ${esc(r.expected_unit)}</td></tr>`).join("")}document.querySelectorAll(".filters input,.filters select").forEach(x=>x.oninput=renderRows);renderRows();
</script></body></html>"""
