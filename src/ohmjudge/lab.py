from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .generate import suite_commitment
from .models import Task


def render_lab(tasks: list[Task], output: str | Path) -> Path:
    if not tasks:
        raise ValueError("cannot render a lab without tasks")
    commitment = suite_commitment(tasks)
    task_json = json.dumps(
        [task.to_dict() for task in tasks],
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    generated = datetime.now(UTC).isoformat(timespec="seconds")
    html = _LAB_HTML.replace("__TASKS__", task_json)
    html = html.replace("__COMMITMENT__", commitment)
    html = html.replace("__GENERATED__", generated)
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding="utf-8")
    return destination


_LAB_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>OhmJudge — No-API Model Lab</title>
<style>
:root{--ink:#eaf4f4;--muted:#8ca6a6;--panel:#10262b;--panel2:#15343a;--line:#28515a;--teal:#4de0c1;--amber:#ffc857;--coral:#ff6b6b;--bg:#07181c}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 15% 0,#14343b 0,transparent 34%),var(--bg);color:var(--ink);font:15px/1.55 Inter,ui-sans-serif,system-ui,sans-serif}
button,input,textarea{font:inherit}.shell{max-width:1280px;margin:auto;padding:28px}.top{display:flex;justify-content:space-between;gap:24px;align-items:flex-start;margin-bottom:22px}.brand{display:flex;gap:14px;align-items:center}.mark{display:grid;place-items:center;width:50px;height:50px;border-radius:15px;background:var(--teal);color:#052126;font-weight:900;font-size:24px;box-shadow:0 12px 35px #4de0c12a}.eyebrow{color:var(--teal);letter-spacing:.14em;text-transform:uppercase;font-size:12px;font-weight:800}h1{font-size:30px;line-height:1.1;margin:4px 0 6px}.sub{color:var(--muted);max-width:720px}.privacy{padding:8px 12px;border:1px solid #4de0c166;background:#4de0c110;border-radius:99px;color:var(--teal);font-weight:700;white-space:nowrap}
.layout{display:grid;grid-template-columns:250px minmax(0,1fr) 300px;gap:16px}.card{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:18px;box-shadow:0 18px 45px #0005}.side{padding:16px}.section-title{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);font-weight:800;margin:2px 0 10px}.model-row{display:flex;gap:8px;margin-bottom:12px}.model-row input{min-width:0;width:100%}.input,textarea{background:#071a1e;color:var(--ink);border:1px solid var(--line);border-radius:10px;padding:10px 12px;outline:none}.input:focus,textarea:focus{border-color:var(--teal);box-shadow:0 0 0 3px #4de0c11a}.btn{border:0;border-radius:10px;padding:9px 12px;background:var(--teal);color:#052126;font-weight:800;cursor:pointer}.btn.secondary{background:#1c4148;color:var(--ink);border:1px solid var(--line)}.btn.warn{background:var(--amber)}.btn:disabled{opacity:.45;cursor:not-allowed}
.model-list,.task-list{display:grid;gap:7px}.model,.task{width:100%;text-align:left;border:1px solid transparent;background:#0a2025;color:var(--ink);border-radius:11px;padding:10px;cursor:pointer}.model.active,.task.active{border-color:var(--teal);background:#12373d}.model small,.task small{display:block;color:var(--muted)}.task.done{box-shadow:inset 3px 0 var(--teal)}.task.wrong{box-shadow:inset 3px 0 var(--coral)}.task-list{max-height:545px;overflow:auto;padding-right:4px}
.workspace{padding:24px;min-height:660px}.meta{display:flex;justify-content:space-between;gap:12px;color:var(--muted);font-size:13px}.pack{color:var(--amber);font-weight:800;text-transform:uppercase;letter-spacing:.08em}.prompt{font-size:19px;line-height:1.6;padding:22px;margin:18px 0;background:#071a1e;border:1px solid var(--line);border-radius:14px;white-space:pre-wrap}.toolbar{display:flex;gap:8px;flex-wrap:wrap}textarea{width:100%;min-height:190px;resize:vertical;margin:16px 0 10px}.result{min-height:52px;border-radius:12px;padding:12px 14px;margin-top:12px}.result.ok{background:#4de0c114;border:1px solid #4de0c166;color:var(--teal)}.result.bad{background:#ff6b6b12;border:1px solid #ff6b6b66;color:#ff9b9b}.hint{font-size:13px;color:var(--muted)}
.score{padding:14px;margin-bottom:10px;background:#0a2025;border-radius:13px}.score-head{display:flex;justify-content:space-between;gap:8px;font-weight:800}.bar{height:7px;background:#061619;border-radius:99px;margin:9px 0;overflow:hidden}.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--teal),#93f3df);border-radius:99px}.score small{color:var(--muted)}.summary{padding:16px}.summary-actions{display:grid;gap:8px;margin-top:14px}.foot{margin-top:16px;color:var(--muted);font-size:12px;word-break:break-all}
@media(max-width:980px){.layout{grid-template-columns:220px 1fr}.summary{grid-column:1/-1}.top{flex-direction:column}}@media(max-width:680px){.shell{padding:14px}.layout{display:block}.side,.workspace,.summary{margin-bottom:12px}.task-list{max-height:240px}.privacy{white-space:normal}.prompt{font-size:16px}}
</style>
</head>
<body>
<main class="shell">
  <header class="top">
    <div class="brand"><div class="mark">Ω</div><div><div class="eyebrow">OhmJudge field lab</div><h1>No-API frontier-model bench</h1><div class="sub">Copy one fresh EE problem into any model's web chat, paste its answer here, and grade it locally. Responses never leave this file.</div></div></div>
    <div class="privacy">● local only · no API key</div>
  </header>
  <div class="layout">
    <aside class="card side">
      <div class="section-title">Models under test</div>
      <div class="model-row"><input id="newModel" class="input" placeholder="e.g. Claude"><button id="addModel" class="btn">+</button></div>
      <div id="modelList" class="model-list"></div>
      <div class="section-title" style="margin-top:20px">Fresh tasks</div>
      <div id="taskList" class="task-list"></div>
    </aside>
    <section class="card workspace">
      <div class="meta"><span id="taskMeta"></span><span id="progress"></span></div>
      <div id="prompt" class="prompt"></div>
      <div class="toolbar">
        <button id="copy" class="btn">Copy prompt</button>
        <button id="reveal" class="btn secondary">Reveal reference</button>
        <button id="previous" class="btn secondary">← Previous</button>
        <button id="next" class="btn secondary">Next →</button>
      </div>
      <textarea id="response" placeholder="Paste the model's complete answer here…"></textarea>
      <div class="toolbar"><button id="grade" class="btn warn">Grade & save</button><button id="clear" class="btn secondary">Clear response</button></div>
      <div id="result" class="result hint">The answer contract asks the model for one JSON object. A plain numeric answer with a unit is accepted as a fallback and marked as such.</div>
    </section>
    <aside class="card summary">
      <div class="section-title">Live scoreboard</div>
      <div id="scoreboard"></div>
      <div class="summary-actions">
        <button id="export" class="btn">Export responses (.jsonl)</button>
        <button id="reset" class="btn secondary">Reset this lab</button>
      </div>
      <div class="foot">Suite commitment<br><code>__COMMITMENT__</code><br><br>Generated __GENERATED__</div>
    </aside>
  </div>
</main>
<script>
const TASKS=__TASKS__, COMMITMENT="__COMMITMENT__", STORAGE="ohmjudge:"+COMMITMENT;
const unitMap={v:["voltage",1],mv:["voltage",1e-3],a:["current",1],ma:["current",1e-3],ua:["current",1e-6],"a/m":["magnetic_field",1],"ma/m":["magnetic_field",1e-3],ohm:["resistance",1],ohms:["resistance",1],milliohm:["resistance",1e-3],kohm:["resistance",1e3],megaohm:["resistance",1e6],hz:["frequency",1],khz:["frequency",1e3],mhz:["frequency",1e6],ghz:["frequency",1e9],s:["time",1],sec:["time",1],second:["time",1],seconds:["time",1],hour:["time",3600],hours:["time",3600],hr:["time",3600],hrs:["time",3600],ms:["time",1e-3],us:["time",1e-6],ns:["time",1e-9],w:["power",1],mw:["power",1e-3],kw:["power",1e3],j:["energy",1],mj:["energy",1e-3],f:["capacitance",1],uf:["capacitance",1e-6],nf:["capacitance",1e-9],pf:["capacitance",1e-12],h:["inductance",1],mh:["inductance",1e-3],uh:["inductance",1e-6],t:["flux_density",1],ut:["flux_density",1e-6],m:["length",1],cm:["length",1e-2],mm:["length",1e-3],db:["db",1],dbm:["dbm",1],"%":["percent",1],bps:["rate",1],"bit/s":["rate",1],kbps:["rate",1e3],"kbit/s":["rate",1e3],mbps:["rate",1e6],"mbit/s":["rate",1e6],gbps:["rate",1e9],"gbit/s":["rate",1e9],baud:["symbol",1],"symbol/s":["symbol",1],kbaud:["symbol",1e3],"ksymbol/s":["symbol",1e3],mbaud:["symbol",1e6],"msymbol/s":["symbol",1e6],samples:["count",1],sample:["count",1],bits:["bit_count",1],bit:["bit_count",1],kib:["data_size",1024],degc:["temperature",1],celsius:["temperature",1],"°c":["temperature",1],unitless:["none",1],none:["none",1],"1":["none",1],"rad/s":["angular",1]};
let state=load(), model=state.models[0], index=0;
function load(){try{const x=JSON.parse(localStorage.getItem(STORAGE));if(x&&Array.isArray(x.models)&&x.models.length)return x}catch{}return{models:["ChatGPT"],results:{}}}
function save(){localStorage.setItem(STORAGE,JSON.stringify(state))}
function esc(s){return String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function normUnit(s){let x=String(s??"").trim().replaceAll("µ","u").replaceAll("μ","u");if(x==="mΩ"||x==="mohm")return"milliohm";if(x==="MΩ"||x==="Mohm")return"megaohm";if(x==="kΩ")return"kohm";return x.toLowerCase().replaceAll("ω","ohm").replaceAll("Ω","ohm").replaceAll(" ","").replaceAll("_","")}
function objects(text){let out=[],start=-1,depth=0,str=false,slash=false;for(let i=0;i<text.length;i++){const c=text[i];if(str){if(slash)slash=false;else if(c==="\\")slash=true;else if(c==='"')str=false;continue}if(c==='"')str=true;else if(c==="{"){if(depth===0)start=i;depth++}else if(c==="}"&&depth){depth--;if(depth===0&&start>=0){out.push(text.slice(start,i+1));start=-1}}}return out}
function parse(text){for(const candidate of objects(text)){try{const x=JSON.parse(candidate);if(x&&Object.hasOwn(x,"answer")){const n=Number(x.answer);return{value:Number.isFinite(n)?n:x.answer,unit:x.unit??null,mode:"json"}}}catch{}}const m=text.replace(/\s+/g," ").match(/(?:answer\s*[:=]\s*)?([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[-+]?\d+)?)\s*([A-Za-z%Ωµμ/]+(?:\/[A-Za-z]+)?)?/i);return m?{value:Number(m[1]),unit:m[2]??null,mode:"numeric_fallback"}:{error:"No JSON object or numeric answer found",mode:"none"}}
function assess(task,text){if(!text.trim())return{correct:false,error_type:"empty_response",mode:"none"};const p=parse(text);if(p.error)return{correct:false,error_type:"parse_error",...p};if(!Number.isFinite(Number(p.value)))return{correct:false,error_type:"non_numeric_answer",...p};if(!p.unit)return{correct:false,error_type:"missing_unit",value:p.value,unit:null,mode:p.mode};const from=normUnit(p.unit),to=normUnit(task.expected.unit),a=unitMap[from],b=unitMap[to];if(!a)return{correct:false,error_type:"unknown_unit",value:p.value,unit:p.unit,mode:p.mode};if(!b)throw new Error("Unknown expected unit: "+task.expected.unit);if(a[0]!==b[0])return{correct:false,error_type:"incompatible_unit",value:p.value,unit:p.unit,mode:p.mode};const observed=Number(p.value)*a[1]/b[1],expected=Number(task.expected.value),error=Math.abs(observed-expected),allowed=Math.max(Number(task.tolerance.absolute||0),Number(task.tolerance.relative||0)*Math.abs(expected));return{correct:error<=allowed+1e-15,error_type:error<=allowed+1e-15?"correct":"wrong_value",value:observed,unit:task.expected.unit,absolute_error:error,allowed_error:allowed,mode:p.mode}}
function currentRecord(){return state.results[model]?.[TASKS[index].id]}
function renderModels(){document.getElementById("modelList").innerHTML=state.models.map(m=>`<button class="model ${m===model?"active":""}" data-model="${esc(m)}"><strong>${esc(m)}</strong><small>${Object.keys(state.results[m]||{}).length} answered</small></button>`).join("");document.querySelectorAll("[data-model]").forEach(b=>b.onclick=()=>{model=b.dataset.model;render()})}
function renderTasks(){document.getElementById("taskList").innerHTML=TASKS.map((t,i)=>{const r=state.results[model]?.[t.id];return`<button class="task ${i===index?"active":""} ${r?(r.grade.correct?"done":"wrong"):""}" data-task="${i}"><strong>${i+1}. ${esc(t.template.replaceAll("_"," "))}</strong><small>${esc(t.pack)} · ${esc(t.metadata.difficulty)}</small></button>`}).join("");document.querySelectorAll("[data-task]").forEach(b=>b.onclick=()=>{index=Number(b.dataset.task);render()})}
function renderScore(){document.getElementById("scoreboard").innerHTML=state.models.map(m=>{const rows=Object.values(state.results[m]||{}),right=rows.filter(x=>x.grade.correct).length,acc=rows.length?100*right/rows.length:0;return`<div class="score"><div class="score-head"><span>${esc(m)}</span><span>${right}/${rows.length}</span></div><div class="bar"><i style="width:${acc}%"></i></div><small>${acc.toFixed(1)}% correct · ${TASKS.length-rows.length} remaining</small></div>`}).join("")}
function render(){const t=TASKS[index],r=currentRecord();renderModels();renderTasks();renderScore();document.getElementById("taskMeta").innerHTML=`<span class="pack">${esc(t.pack)}</span> · ${esc(t.template)} · ${esc(t.metadata.difficulty)}`;document.getElementById("progress").textContent=`${index+1} / ${TASKS.length}`;document.getElementById("prompt").textContent=t.prompt;document.getElementById("response").value=r?.text||"";const box=document.getElementById("result");if(r){box.className="result "+(r.grade.correct?"ok":"bad");box.textContent=r.grade.correct?`Correct · ${r.grade.mode}`:`${r.grade.error_type.replaceAll("_"," ")} · expected ${t.expected.value} ${t.expected.unit}`;}else{box.className="result hint";box.textContent=`Pasting for ${model}. Nothing is sent over the network.`}document.getElementById("previous").disabled=index===0;document.getElementById("next").disabled=index===TASKS.length-1}
document.getElementById("addModel").onclick=()=>{const input=document.getElementById("newModel"),name=input.value.trim();if(name&&!state.models.includes(name)){state.models.push(name);model=name;input.value="";save();render()}};
document.getElementById("newModel").onkeydown=e=>{if(e.key==="Enter")document.getElementById("addModel").click()};
document.getElementById("copy").onclick=async()=>{await navigator.clipboard.writeText(TASKS[index].prompt);const b=document.getElementById("copy"),old=b.textContent;b.textContent="Copied";setTimeout(()=>b.textContent=old,900)};
document.getElementById("grade").onclick=()=>{const text=document.getElementById("response").value.trim();if(!text)return;state.results[model]??={};state.results[model][TASKS[index].id]={text,grade:assess(TASKS[index],text),saved_at:new Date().toISOString()};save();render()};
document.getElementById("clear").onclick=()=>{document.getElementById("response").value=""};
document.getElementById("reveal").onclick=()=>{const t=TASKS[index];document.getElementById("result").className="result ok";document.getElementById("result").textContent=`Reference: ${t.expected.value} ${t.expected.unit} · tolerance rel=${t.tolerance.relative}, abs=${t.tolerance.absolute}`};
document.getElementById("previous").onclick=()=>{if(index>0){index--;render()}};
document.getElementById("next").onclick=()=>{if(index<TASKS.length-1){index++;render()}};
document.getElementById("export").onclick=()=>{let lines=[];for(const m of state.models)for(const t of TASKS){const r=state.results[m]?.[t.id];if(r)lines.push(JSON.stringify({task_id:t.id,provider:"manual-web",model:m,text:r.text,latency_ms:null,usage:{},metadata:{saved_at:r.saved_at}}))}const blob=new Blob([lines.join("\n")+"\n"],{type:"application/x-ndjson"}),a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="ohmjudge-responses.jsonl";a.click();URL.revokeObjectURL(a.href)};
document.getElementById("reset").onclick=()=>{if(confirm("Delete all locally saved responses for this suite?")){localStorage.removeItem(STORAGE);state=load();model=state.models[0];index=0;render()}};
render();
</script>
</body>
</html>
"""
