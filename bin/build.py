#!/usr/bin/env python3
"""Collect the rendered scenes and speaker notes, in talk order, into two files: present.html, the audience window,
and presenter.html, the speaker's window with notes, a timer and the controls.

Playback is one continuous video per scene with pause points at the step boundaries, not one clip per step: swapping a
video's source between clips redraws the element and flickers, while pausing and resuming a single source is seamless.
Scene changes swap between two stacked video elements, the next one already loaded, so they do not flicker either.
Boundaries come from the per-step durations Manim writes into the section index. Usage: bin/build.py <talk> [ql|qm|qh]; writes talks/<talk>/present.html and presenter.html."""
import glob, json, os, re, sys

talk = sys.argv[1] if len(sys.argv) > 1 else None
if not talk:
    sys.exit("usage: bin/build.py <talk> [ql|qm|qh]")
Q = {"ql": "480p15", "qm": "720p30", "qh": "1080p60"}[sys.argv[2] if len(sys.argv) > 2 else "qm"]
root = f"talks/{talk}"
title_line = next((l for l in open(f"{root}/script.md") if l.startswith("# ")), f"# {talk}") if os.path.exists(f"{root}/script.md") else f"# {talk}"
TITLE = title_line[2:].strip()
scenes = []
for f in sorted(glob.glob(f"{root}/scenes/s*.py")):
    stem = os.path.basename(f)[:-3]
    for scene in re.findall(r"^class (\w+)\(TalkSlide\)", open(f).read(), re.M):
        index = f"{root}/media/videos/{stem}/{Q}/sections/{scene}.json"
        if not os.path.exists(index):
            print(f"not rendered: {scene}"); continue
        notes_path = f"{root}/media/notes/{scene}.json"
        notes = json.load(open(notes_path)) if os.path.exists(notes_path) else []
        ends, t = [], 0.0
        for sec in json.load(open(index)):
            t += float(sec["duration"]); ends.append(round(t, 3))
        scenes.append({"name": scene, "src": f"media/videos/{stem}/{Q}/{scene}.mp4", "ends": ends,   # relative to the talk folder, where the pages live
                       "notes": [notes[i] if i < len(notes) else "" for i in range(len(ends))]})
steps = [{"scene": s["name"], "si": i, "k": k, "note": s["notes"][k]} for i, s in enumerate(scenes) for k in range(len(s["ends"]))]
data = json.dumps({"scenes": scenes, "steps": steps})

player_js = """
const D=%s;const S=D.scenes,ST=D.steps;let i=-1;
const vids=[document.getElementById('a'),document.getElementById('b')];let cur=0;   // vids[cur] is on top
function other(){return 1-cur}
function load(v,si){if(v.dataset.si!==String(si)){v.dataset.si=si;v.src=S[si].src;v.load();}}
function show(k){                     // play from the start of step k to its end, then hold the frame
  if(k<0||k>=ST.length)return;const st=ST[k],sc=S[st.si],prev=i>=0?ST[i]:null;i=k;
  const start=st.k?sc.ends[st.k-1]:0,end=sc.ends[st.k];
  if(!prev||prev.si!==st.si){            // new scene: bring up the preloaded element, but only once it shows the right frame
    const v=vids[other()];if(v.dataset.si!==String(st.si))load(v,st.si);
    let done=false;const go=()=>{if(done)return;done=true;cur=1-cur;vids[cur].style.zIndex=2;vids[1-cur].style.zIndex=1;
      v.play().catch(()=>{});hold(v,end);if(S[st.si+1])load(vids[1-cur],st.si+1);};
    if(v.readyState>=2&&Math.abs(v.currentTime-start)<0.04)go();
    else{v.addEventListener('seeked',go,{once:true});v.currentTime=start;setTimeout(go,600);}   // a swap before the seek lands would flash the element's old frame
  }else{const v=vids[cur];if(Math.abs(v.currentTime-start)>0.25)v.currentTime=start;v.play().catch(()=>{});hold(v,end);}
  onstep&&onstep(k);
}
let holdId=0;
// Stop a few frames before the boundary: the check runs once per animation frame, so playback can overshoot into the
// next step's first frame by the time it is seen, and a seek to end-0.001 can snap onto that frame too. Steps end on a
// settled picture, so 0.06 s (four frames at 60 fps) before the boundary is the same picture.
function hold(v,end){cancelAnimationFrame(holdId);const tick=()=>{if(v.currentTime>=end-0.1){v.pause();v.currentTime=Math.max(0,end-0.06);return;}holdId=requestAnimationFrame(tick);};holdId=requestAnimationFrame(tick);}
function next(){show(i+1)} function prev(){show(i-1)}
"""

present = f"""<!doctype html><meta charset="utf-8"><title>{TITLE}</title>
<style>html,body{{margin:0;height:100%;background:#0f1116;overflow:hidden;font:16px Helvetica,sans-serif;color:#e8e8e8}}
video{{position:fixed;inset:0;width:100vw;height:100vh;object-fit:contain;background:#0f1116}}
#hint{{position:fixed;inset:0;z-index:5;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:12px;background:rgba(15,17,22,.85);cursor:pointer}}
#hint b{{font-size:28px;font-weight:500}} #hint span{{color:#9aa0ad}}</style>
<video id="a" playsinline preload="auto" muted></video><video id="b" playsinline preload="auto" muted></video>
<div id="hint"><b>{TITLE}</b><span>{len(steps)} steps. Click or right arrow to advance, left to go back, f for full screen.</span><span>Open presenter.html for notes and remote control.</span></div>
<script>
const ch=new BroadcastChannel('talk');const tell=m=>{{ch.postMessage(m);if(window.opener)window.opener.postMessage(m,'*');}};
let onstep=k=>{{document.getElementById('hint')?.remove();tell({{at:k}});}};
const handle=d=>{{if(!d)return;if(d.go!==undefined)show(d.go);if(d.hello)tell({{at:i}});}};
{player_js.replace('%s', data)}
load(vids[0],0);if(S[1])load(vids[1],1);
document.getElementById('hint').addEventListener('click',e=>{{e.stopPropagation();show(0);}});   // the same click must not also count as 'next'
document.addEventListener('keydown',e=>{{if(e.key==='ArrowRight'||e.key===' '||e.key==='PageDown')next();else if(e.key==='ArrowLeft'||e.key==='PageUp')prev();else if(e.key==='f')document.documentElement.requestFullscreen();else if(e.key==='Home')show(0);}});
document.addEventListener('click',e=>{{if(i>=0)next();}});
ch.onmessage=e=>handle(e.data);window.addEventListener('message',e=>handle(e.data));
</script>"""

presenter = f"""<!doctype html><meta charset="utf-8"><title>Presenter</title>
<style>html,body{{margin:0;height:100%;background:#15181f;color:#e8e8e8;font:18px/1.5 Helvetica,sans-serif}}
#top{{display:flex;gap:24px;align-items:center;padding:14px 22px;border-bottom:1px solid #2a2e38;color:#9aa0ad}}
#top b{{color:#e8e8e8;font-weight:500}} #clock{{margin-left:auto;font-variant-numeric:tabular-nums;font-size:22px}}
#main{{display:grid;grid-template-columns:1.25fr 1fr;gap:22px;padding:22px}}
#nextstage{{position:relative;aspect-ratio:16/9;background:#0f1116;border-radius:8px;overflow:hidden;width:62%;margin-bottom:16px}} #nextstage video{{position:absolute;inset:0;width:100%;height:100%}} #nextlabel{{font-size:12px;color:#9aa0ad;letter-spacing:.04em;margin-bottom:4px}}
#stage{{position:relative;aspect-ratio:16/9;background:#0f1116;border-radius:8px;overflow:hidden}} #stage video{{position:absolute;inset:0;width:100%;height:100%}}
#note{{font-size:21px;line-height:1.55;color:#f2f2f2}} #note h3{{margin:0 0 10px;font-weight:500;color:#58c4dd;font-size:16px;letter-spacing:.02em}}
#nextnote{{margin-top:22px;color:#9aa0ad;font-size:15px;border-top:1px solid #2a2e38;padding-top:14px}}
#keys{{padding:0 22px 16px;color:#5b6070;font-size:14px}} button{{background:#242833;color:#e8e8e8;border:1px solid #3a3f4b;border-radius:6px;padding:6px 14px;font:16px Helvetica;cursor:pointer}}</style>
<div id="top"><button onclick="open_audience()">open audience window</button><button onclick="send(-1)">back</button><button onclick="send(1)">next</button><span id="pos"></span><b id="scene"></b><span id="clock">00:00</span></div>
<div id="main"><div id="stage"><video id="a" muted playsinline preload="auto"></video><video id="b" muted playsinline preload="auto"></video></div>
<div><div id="nextlabel">NEXT: WHERE THE CLICK ENDS UP</div><div id="nextstage"><video id="n" muted playsinline preload="auto"></video></div><div id="note"><h3></h3><div id="txt"></div></div><div id="nextnote"></div></div></div>
<div id="keys">Keys: right or space next, left back, Home first step, t reset timer. The audience window follows this one.</div>
<script>
const ch=new BroadcastChannel('talk');const t0=[Date.now()];let aud=null;
const tell=m=>{{ch.postMessage(m);if(aud&&!aud.closed)aud.postMessage(m,'*');}};
let onstep=k=>{{const s=ST[k],n=ST[k+1];document.getElementById('pos').textContent=(k+1)+' / '+ST.length;document.getElementById('scene').textContent=s.scene;
document.querySelector('#note h3').textContent=s.scene.replace(/([a-z])([A-Z])/g,'$1 $2');document.getElementById('txt').textContent=s.note;
document.getElementById('nextnote').textContent=n?('next: '+n.scene+(n.scene!==s.scene?' (new scene)':'')+'. '+n.note.slice(0,240)+(n.note.length>240?'...':'')):'end of talk';
preview(n);}};
function preview(n){{const nv=document.getElementById('n');if(!n){{nv.removeAttribute('src');nv.load();return;}}const sc=S[n.si],at=Math.max(0,sc.ends[n.k]-0.05);   // the last frame of the next step: where 'next' will end up
  const seek=()=>{{nv.pause();nv.currentTime=at;}};if(nv.dataset.si!==String(n.si)){{nv.dataset.si=n.si;nv.src=sc.src;nv.addEventListener('loadedmetadata',seek,{{once:true}});nv.load();}}else seek();}}
{player_js.replace('%s', data)}
load(vids[0],0);if(S[1])load(vids[1],1);
function open_audience(){{aud=window.open('present.html','audience','width=1280,height=720');setTimeout(()=>tell({{go:Math.max(0,i)}}),1500);}}
function send(d){{const k=Math.max(0,Math.min(ST.length-1,i+d));tell({{go:k}});show(k);}}
const handle=d=>{{if(d&&d.at!==undefined&&d.at!==i)show(d.at);}};
ch.onmessage=e=>handle(e.data);window.addEventListener('message',e=>handle(e.data));
document.addEventListener('keydown',e=>{{if(e.key==='ArrowRight'||e.key===' ')send(1);else if(e.key==='ArrowLeft')send(-1);else if(e.key==='Home'){{tell({{go:0}});show(0);}}else if(e.key==='t')t0[0]=Date.now();}});
setInterval(()=>{{const s=Math.floor((Date.now()-t0[0])/1000);document.getElementById('clock').textContent=String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');}},500);
show(0);tell({{hello:1}});
</script>"""
open(f"{root}/present.html", "w").write(present); open(f"{root}/presenter.html", "w").write(presenter)
missing = sum(1 for s in steps if not s["note"])
print(f"{talk}: {len(steps)} steps in {len(scenes)} scenes -> {root}/present.html, presenter.html ({missing} steps without a note)")
