from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .generate import suite_commitment
from .models import Task


def render_collector(tasks: list[Task], output: str | Path) -> Path:
    """Build an answer-free, offline response collector.

    The regular lab deliberately contains the private answer key so it can
    grade in the browser. This artifact has the opposite contract: it may be
    handed to a collector, so only public task records are embedded and all
    scoring happens later with the private JSONL file.
    """
    if not tasks:
        raise ValueError("cannot render a collector without tasks")
    commitment = suite_commitment(tasks)
    public_tasks = [task.to_dict(public=True) for task in tasks]
    task_json = json.dumps(
        public_tasks,
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    generated = datetime.now(UTC).isoformat(timespec="seconds")
    html = _COLLECTOR_HTML.replace("__TASKS__", task_json)
    html = html.replace("__COMMITMENT__", commitment)
    html = html.replace("__GENERATED__", generated)
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding="utf-8")
    return destination


_COLLECTOR_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>OhmJudge - Blind response collector</title>
<style>
:root{--ink:#172630;--muted:#617079;--paper:#f6f4ee;--panel:#fff;--line:#d0cec6;--blue:#2f6f9f;--navy:#15324b;--rust:#b65d3a;--green:#55723b;--soft:#f1f0eb;--focus:#dceaf3}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.55 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}button,input,textarea{font:inherit}.shell{max-width:1320px;margin:auto;padding:28px}.top{display:flex;justify-content:space-between;gap:24px;align-items:flex-start;margin-bottom:24px;padding-bottom:22px;border-bottom:1px solid var(--line)}.brand{display:flex;gap:16px;align-items:center}.mark{display:grid;place-items:center;width:48px;height:48px;border:2px solid var(--navy);color:var(--navy);font-family:Georgia,serif;font-weight:700;font-size:22px}.eyebrow{color:var(--blue);letter-spacing:.13em;text-transform:uppercase;font-size:11px;font-weight:800}h1{font-family:Georgia,"Times New Roman",serif;font-size:31px;line-height:1.1;margin:4px 0 6px}.sub{color:var(--muted);max-width:760px}.blind{padding:8px 12px;border:1px solid #9bad8a;background:#edf3e9;color:#3e542f;font-weight:800;white-space:nowrap}.layout{display:grid;grid-template-columns:250px minmax(0,1fr) 310px;gap:14px}.card{background:var(--panel);border:1px solid var(--line);border-radius:4px}.side,.summary{padding:16px}.section-title{font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:var(--navy);font-weight:800;margin:2px 0 10px}.model-row{display:flex;gap:8px;margin-bottom:12px}.model-row input{min-width:0;width:100%}.input,textarea{background:#fff;color:var(--ink);border:1px solid #b9b7b0;border-radius:3px;padding:10px 11px;outline:none}.input:focus,textarea:focus{border-color:var(--blue);box-shadow:0 0 0 3px var(--focus)}.btn{border:1px solid var(--navy);border-radius:3px;padding:9px 12px;background:var(--navy);color:#fff;font-weight:750;cursor:pointer}.btn.secondary{background:#fff;color:var(--navy);border-color:#9aa7ae}.btn.save{background:var(--rust);border-color:var(--rust)}.btn:disabled{opacity:.45;cursor:not-allowed}.model-list,.task-list{display:grid;gap:5px}.model,.task{width:100%;text-align:left;border:1px solid transparent;background:#f6f5f1;color:var(--ink);border-radius:2px;padding:9px;cursor:pointer}.model.active,.task.active{border-color:var(--blue);background:#edf3f7}.model small,.task small{display:block;color:var(--muted)}.task.done{box-shadow:inset 3px 0 var(--green)}.task-list{max-height:530px;overflow:auto;padding-right:4px}.workspace{padding:24px;min-height:660px}.meta{display:flex;justify-content:space-between;gap:12px;color:var(--muted);font-size:13px}.pack{color:var(--rust);font-weight:800;text-transform:uppercase;letter-spacing:.08em}.prompt{font-family:Georgia,"Times New Roman",serif;font-size:19px;line-height:1.65;padding:22px;margin:18px 0;background:#f8f7f3;border-left:4px solid var(--blue);white-space:pre-wrap}.toolbar{display:flex;gap:8px;flex-wrap:wrap}textarea{width:100%;min-height:220px;resize:vertical;margin:16px 0 10px}.status{min-height:52px;border:1px solid var(--line);background:var(--soft);border-radius:2px;padding:12px 14px;margin-top:12px;color:var(--muted)}.status.ok{background:#edf3e9;border-color:#afbf9f;color:#3e542f}.status.bad{background:#f7ecea;border-color:#d1aaa5;color:#78362f}.progress-card{padding:13px 0;margin-bottom:8px;border-bottom:1px solid #e2e0da}.progress-head{display:flex;justify-content:space-between;gap:8px;font-weight:800}.bar{height:6px;background:#e7e5df;margin:9px 0;overflow:hidden}.bar i{display:block;height:100%;background:var(--blue)}.progress-card small{color:var(--muted)}.actions{display:grid;gap:8px;margin-top:14px}.protocol{margin-top:18px;padding-top:16px;border-top:1px solid var(--line)}.protocol label{display:block;color:var(--muted);font-size:11px;margin:9px 0 4px}.protocol input{width:100%}.note{font-size:11px;color:var(--muted);margin:8px 0}.foot{margin-top:16px;color:var(--muted);font-size:11px;word-break:break-all;border-top:1px solid var(--line);padding-top:14px}.answer-free{margin:0 0 14px;padding:11px 12px;border-left:3px solid var(--green);background:#f2f5ef;color:#44543a;font-size:13px}
@media(max-width:1040px){.layout{grid-template-columns:220px 1fr}.summary{grid-column:1/-1}.top{flex-direction:column}}@media(max-width:680px){.shell{padding:14px}.layout{display:block}.side,.workspace,.summary{margin-bottom:12px}.task-list{max-height:240px}.blind{white-space:normal}.brand{align-items:flex-start}.mark{flex:0 0 auto;width:40px;height:40px;font-size:18px}.prompt{font-size:16px}.meta{display:block}}
</style>
</head>
<body>
<main class="shell">
  <header class="top">
    <div class="brand"><div class="mark">OJ</div><div><div class="eyebrow">OhmJudge field collection</div><h1>Blind response collector</h1><div class="sub">Copy each committed EE prompt into the named model, paste the complete response, and export a checkpoint. Collection stays in this file until you choose to export it.</div></div></div>
    <div class="blind">ANSWER-FREE - COLLECTION ONLY</div>
  </header>
  <div class="layout">
    <aside class="card side">
      <div class="section-title">Models under test</div>
      <div class="model-row"><input id="newModel" class="input" placeholder="Visible model label"><button id="addModel" class="btn" aria-label="Add model">+</button></div>
      <div id="modelList" class="model-list"></div>
      <div class="section-title" style="margin-top:20px">Committed tasks</div>
      <div id="taskList" class="task-list"></div>
    </aside>
    <section class="card workspace">
      <div class="meta"><span id="taskMeta"></span><span id="position"></span></div>
      <div id="prompt" class="prompt"></div>
      <div class="toolbar">
        <button id="copy" class="btn">Copy prompt</button>
        <button id="previous" class="btn secondary">Previous</button>
        <button id="next" class="btn secondary">Next</button>
      </div>
      <textarea id="response" placeholder="Paste the model's complete response here" aria-label="Model response"></textarea>
      <div class="toolbar"><button id="saveNext" class="btn save">Save and next unanswered</button><button id="save" class="btn secondary">Save here</button><button id="clear" class="btn secondary">Clear editor</button></div>
      <div id="status" class="status">No answer key or grading code is present in this collector. Export responses and grade them later with the private task file.</div>
    </section>
    <aside class="card summary">
      <p class="answer-free"><strong>Blind by construction.</strong> This file contains public prompts and a suite commitment, but no reference values, tolerances, or live scores.</p>
      <div class="section-title">Collection progress</div>
      <div id="progress"></div>
      <div class="protocol">
        <div class="section-title">Capture protocol</div>
        <p class="note">These fields are copied into every exported response.</p>
        <label for="surface">Product / surface</label><input id="surface" class="input" placeholder="e.g. ChatGPT web">
        <label for="settings">Visible settings</label><input id="settings" class="input" placeholder="e.g. default; reasoning high">
        <label for="tools">Tools</label><input id="tools" class="input" placeholder="e.g. disabled">
        <label for="retryPolicy">Retry policy</label><input id="retryPolicy" class="input" placeholder="e.g. no retries">
      </div>
      <div class="actions">
        <button id="export" class="btn">Export checkpoint (.jsonl)</button>
        <button id="importButton" class="btn secondary">Import checkpoint</button>
        <input id="importFile" type="file" accept=".jsonl,.ndjson,application/x-ndjson" hidden>
        <button id="reset" class="btn secondary">Reset this collector</button>
      </div>
      <div class="foot">Suite commitment<br><code>__COMMITMENT__</code><br><br>Generated __GENERATED__</div>
    </aside>
  </div>
</main>
<script>
const TASKS=__TASKS__,COMMITMENT="__COMMITMENT__",STORAGE="ohmjudge:collector:"+COMMITMENT,PROTOCOL_FIELDS=["surface","settings","tools","retryPolicy"],TASK_IDS=new Set(TASKS.map(t=>t.id));
let state=load(),model=state.models[0],index=0;
function load(){let value=null;try{value=JSON.parse(localStorage.getItem(STORAGE))}catch{}if(!value||!Array.isArray(value.models)||!value.models.length)value={models:["Model A"],results:{},protocols:{}};value.results??={};value.protocols??={};if(value.protocol&&!Object.keys(value.protocols).length)value.protocols[value.models[0]]=value.protocol;delete value.protocol;return value}
function saveState(){localStorage.setItem(STORAGE,JSON.stringify(state))}
function esc(value){return String(value).replace(/[&<>\"]/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;",'\"':"&quot;"}[char]))}
function recordsFor(name){return state.results[name]||{}}
function protocolFor(name){state.protocols[name]??={};return state.protocols[name]}
function currentRecord(){return recordsFor(model)[TASKS[index].id]}
function setStatus(message,kind=""){const box=document.getElementById("status");box.className="status "+kind;box.textContent=message}
function renderModels(){document.getElementById("modelList").innerHTML=state.models.map(name=>`<button class="model ${name===model?"active":""}" data-model="${esc(name)}"><strong>${esc(name)}</strong><small>${Object.keys(recordsFor(name)).length} captured</small></button>`).join("");document.querySelectorAll("[data-model]").forEach(button=>button.onclick=()=>{saveEditor();model=button.dataset.model;render()})}
function renderTasks(){document.getElementById("taskList").innerHTML=TASKS.map((task,taskIndex)=>{const done=recordsFor(model)[task.id];return`<button class="task ${taskIndex===index?"active":""} ${done?"done":""}" data-task="${taskIndex}"><strong>${taskIndex+1}. ${esc(task.template.replaceAll("_"," "))}</strong><small>${esc(task.pack)} - ${esc(task.metadata?.difficulty||"unspecified")}</small></button>`}).join("");document.querySelectorAll("[data-task]").forEach(button=>button.onclick=()=>{saveEditor();index=Number(button.dataset.task);render()})}
function renderProgress(){document.getElementById("progress").innerHTML=state.models.map(name=>{const count=Object.keys(recordsFor(name)).length,percent=100*count/TASKS.length;return`<div class="progress-card"><div class="progress-head"><span>${esc(name)}</span><span>${count}/${TASKS.length}</span></div><div class="bar"><i style="width:${percent}%"></i></div><small>${TASKS.length-count} remaining - no score is computed</small></div>`}).join("")}
function render(){const task=TASKS[index],record=currentRecord();syncProtocol();renderModels();renderTasks();renderProgress();document.getElementById("taskMeta").innerHTML=`<span class="pack">${esc(task.pack)}</span> - ${esc(task.template)} - ${esc(task.metadata?.difficulty||"unspecified")}`;document.getElementById("position").textContent=`${index+1} / ${TASKS.length}`;document.getElementById("prompt").textContent=task.prompt;document.getElementById("response").value=record?.text||"";document.getElementById("previous").disabled=index===0;document.getElementById("next").disabled=index===TASKS.length-1}
function saveEditor(){const text=document.getElementById("response").value.trim();if(!text)return false;state.results[model]??={};state.results[model][TASKS[index].id]={text,captured_at:currentRecord()?.captured_at||new Date().toISOString()};saveState();return true}
function nextUnanswered(){for(let offset=1;offset<=TASKS.length;offset++){const candidate=(index+offset)%TASKS.length;if(!recordsFor(model)[TASKS[candidate].id]){index=candidate;return true}}return false}
function checkpointRows(){let rows=[];for(const name of state.models)for(const task of TASKS){const record=recordsFor(name)[task.id],protocol=protocolFor(name);if(record)rows.push({task_id:task.id,provider:"manual-web",model:name,text:record.text,latency_ms:null,usage:{},error:null,metadata:{captured_at:record.captured_at,surface:protocol.surface||"",settings:protocol.settings||"",tools:protocol.tools||"",retry_policy:protocol.retryPolicy||"",suite_commitment:COMMITMENT,capture_method:"answer-free-collector"}})}return rows}
function downloadCheckpoint(){saveEditor();const rows=checkpointRows();if(!rows.length){setStatus("Nothing to export yet.","bad");return}const blob=new Blob([rows.map(row=>JSON.stringify(row)).join("\n")+"\n"],{type:"application/x-ndjson"}),anchor=document.createElement("a");anchor.href=URL.createObjectURL(blob);anchor.download="ohmjudge-responses.jsonl";anchor.click();URL.revokeObjectURL(anchor.href);setStatus(`Exported ${rows.length} response record(s).`,"ok")}
async function importCheckpoint(file){const lines=(await file.text()).split(/\r?\n/).filter(line=>line.trim()),rows=[],seen=new Set(),incoming={};for(let lineIndex=0;lineIndex<lines.length;lineIndex++){let row;try{row=JSON.parse(lines[lineIndex])}catch{throw new Error(`Line ${lineIndex+1} is not valid JSON.`)}if(row?.metadata?.suite_commitment!==COMMITMENT)throw new Error(`Line ${lineIndex+1} belongs to a different or uncommitted suite.`);if(!TASK_IDS.has(row.task_id))throw new Error(`Line ${lineIndex+1} references unknown task ${row.task_id}.`);const name=String(row.model||"").trim(),key=name+"\0"+row.task_id;if(row.provider!=="manual-web"||!name)throw new Error(`Line ${lineIndex+1} is not a manual-web collector record.`);if(!String(row.text||"").trim())throw new Error(`Line ${lineIndex+1} has an empty response.`);if(seen.has(key))throw new Error(`Line ${lineIndex+1} duplicates ${name}/${row.task_id}.`);seen.add(key);incoming[name]??={};for(const [field,source] of [["surface","surface"],["settings","settings"],["tools","tools"],["retryPolicy","retry_policy"]]){const value=String(row.metadata?.[source]||"");if(incoming[name][field]&&value&&incoming[name][field]!==value)throw new Error(`Line ${lineIndex+1} conflicts with ${name}'s ${source}.`);if(value)incoming[name][field]=value}rows.push(row)}if(!rows.length)throw new Error("Checkpoint contains no response records.");for(const [name,protocol] of Object.entries(incoming)){const existing=protocolFor(name);for(const [field,value] of Object.entries(protocol)){if(existing[field]&&existing[field]!==value)throw new Error(`Imported protocol conflicts with locally saved ${name}/${field}.`)}}for(const row of rows){const name=String(row.model).trim(),existing=recordsFor(name)[row.task_id];if(existing&&existing.text!==String(row.text))throw new Error(`Imported response conflicts with locally saved ${name}/${row.task_id}.`)}for(const row of rows){const name=String(row.model).trim();if(!state.models.includes(name))state.models.push(name);state.results[name]??={};state.results[name][row.task_id]={text:String(row.text),captured_at:row.metadata.captured_at||new Date().toISOString()};Object.assign(protocolFor(name),incoming[name])}saveState();model=String(rows[0].model).trim();index=0;render();setStatus(`Imported ${rows.length} response record(s) bound to this suite.`,"ok")}
function syncProtocol(){const protocol=protocolFor(model);for(const id of PROTOCOL_FIELDS){const element=document.getElementById(id);element.value=protocol[id]||""}}
async function copyPrompt(){const text=TASKS[index].prompt;try{await navigator.clipboard.writeText(text)}catch{const helper=document.createElement("textarea");helper.value=text;helper.style.position="fixed";helper.style.opacity="0";document.body.appendChild(helper);helper.select();document.execCommand("copy");helper.remove()}setStatus("Prompt copied. Paste it into the recorded model surface.","ok")}
document.getElementById("addModel").onclick=()=>{const input=document.getElementById("newModel"),name=input.value.trim();if(name&&!state.models.includes(name)){saveEditor();state.models.push(name);model=name;input.value="";saveState();render()}};
document.getElementById("newModel").onkeydown=event=>{if(event.key==="Enter")document.getElementById("addModel").click()};
document.getElementById("copy").onclick=copyPrompt;
document.getElementById("save").onclick=()=>{if(saveEditor()){render();setStatus("Response saved locally. No score was computed.","ok")}else setStatus("Paste a response before saving.","bad")};
document.getElementById("saveNext").onclick=()=>{if(!saveEditor()){setStatus("Paste a response before saving.","bad");return}const moved=nextUnanswered();render();setStatus(moved?"Saved. Moved to the next unanswered task.":"Saved. This model now has a response for every task.","ok")};
document.getElementById("clear").onclick=()=>{document.getElementById("response").value=""};
document.getElementById("previous").onclick=()=>{saveEditor();if(index>0)index--;render()};
document.getElementById("next").onclick=()=>{saveEditor();if(index<TASKS.length-1)index++;render()};
document.getElementById("response").onkeydown=event=>{if((event.ctrlKey||event.metaKey)&&event.key==="Enter"){event.preventDefault();document.getElementById("saveNext").click()}};
for(const id of PROTOCOL_FIELDS){const element=document.getElementById(id);element.oninput=()=>{protocolFor(model)[id]=element.value.trim();saveState()}}
document.getElementById("export").onclick=downloadCheckpoint;
document.getElementById("importButton").onclick=()=>document.getElementById("importFile").click();
document.getElementById("importFile").onchange=async event=>{const file=event.target.files[0];if(!file)return;try{await importCheckpoint(file)}catch(error){setStatus(error.message,"bad")}finally{event.target.value=""}};
document.getElementById("reset").onclick=()=>{if(confirm("Delete all locally saved responses for this suite?")){localStorage.removeItem(STORAGE);location.reload()}};
render();
</script>
</body>
</html>
"""
