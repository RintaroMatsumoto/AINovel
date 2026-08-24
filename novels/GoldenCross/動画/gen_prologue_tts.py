# -*- coding: utf-8 -*-
"""GoldenCross プロローグ TTS —— 凛音エル"""
import json, urllib.request, urllib.parse, wave, io, time, os, sys, re
sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://100.112.59.35:10101"
SPEAKER = 1388823424  # 凛音エル ノーマル
OUT = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\GoldenCross\本文\プロローグ.md"

# 本文読み込み（見出し除去）
with open(SRC, encoding="utf-8") as f:
    raw = f.read()
lines = [l.strip() for l in raw.split("\n") if l.strip() and not l.startswith("##")]
text = "\n".join(lines)
print(f"Text: {len(text)} chars")

# チャンク分割（500字以内・段落単位）
def split_chunks(t, max_chars=280):
    paras = t.split("\n")
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 1 <= max_chars:
            cur += p + "\n"
        else:
            if cur.strip(): chunks.append(cur.strip())
            while len(p) > max_chars:
                chunks.append(p[:max_chars]); p = p[max_chars:]
            cur = p + "\n"
    if cur.strip(): chunks.append(cur.strip())
    return chunks

chunks = split_chunks(text)
print(f"Chunks: {len(chunks)}")

# 合成
wav_parts, timing = [], []
total_duration = 0.0
for i, chunk in enumerate(chunks):
    print(f"  [{i+1}/{len(chunks)}] {len(chunk)}字...", end=" ", flush=True)
    ok_flag = False
    for attempt in range(3):
        try:
            url = f"{BASE}/audio_query?speaker={SPEAKER}&text={urllib.parse.quote(chunk)}"
            req = urllib.request.Request(url, method="POST")
            query = json.loads(urllib.request.urlopen(req, timeout=180).read())
            query["speedScale"] = 0.9
            url2 = f"{BASE}/synthesis?speaker={SPEAKER}"
            req2 = urllib.request.Request(url2, data=json.dumps(query).encode(), method="POST")
            req2.add_header("Content-Type", "application/json")
            wav_data = urllib.request.urlopen(req2, timeout=600).read()
            with wave.open(io.BytesIO(wav_data), "rb") as w:
                dur = w.getnframes() / w.getframerate()
            wav_parts.append(wav_data)
            timing.append({"duration": round(dur, 2), "chars": len(chunk)})
            total_duration += dur
            print(f"OK {dur:.1f}s")
            ok_flag = True
            break
        except Exception as e:
            print(f"retry({attempt+1}): {e}")
            time.sleep(5)
    if not ok_flag:
        print("FAIL"); sys.exit(1)
    time.sleep(0.3)

# WAV結合
out_wav = os.path.join(OUT, "prologue_tts.wav")
nch = sw = fr = None
frames = []
for wd in wav_parts:
    with wave.open(io.BytesIO(wd), "rb") as w:
        if nch is None:
            nch = w.getnchannels(); sw = w.getsampwidth(); fr = w.getframerate()
        frames.append(w.readframes(w.getnframes()))

with wave.open(out_wav, "wb") as w:
    w.setnchannels(nch); w.setsampwidth(sw); w.setframerate(fr)
    for fr_data in frames: w.writeframes(fr_data)

print(f"\nAudio: {out_wav}")
print(f"  Duration: {total_duration:.1f}s ({total_duration/60:.1f}min)")

# timing.json
cps = len(text) / total_duration
pos = 0.0
for t in timing:
    t["scroll_start"] = round(pos, 2); pos += t["duration"]; t["scroll_end"] = round(pos, 2)
tj = {"total_chars": len(text), "total_duration": round(total_duration, 2),
      "scroll_speed_cps": round(cps, 2), "chunks": timing}
with open(os.path.join(OUT, "timing.json"), "w", encoding="utf-8") as f:
    json.dump(tj, f, ensure_ascii=False, indent=1)
print(f"Timing: cps={cps:.1f}")
print("DONE")
