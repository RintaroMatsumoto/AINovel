# -*- coding: utf-8 -*-
"""GoldenCross プロローグ v3 —— 背景切替＋BGM 4トーン＋TTS同期"""
import os, sys, json, re, subprocess
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = r"C:\Users\GoldRush\Documents\MyProject\AINovel"
SHARED = os.path.join(ROOT, "novels", "制作共通")
GC_V = os.path.join(ROOT, "novels", "GoldenCross", "動画")
BG_DIR = os.path.join(GC_V, "_bg_images")
SRC = os.path.join(ROOT, "novels", "GoldenCross", "本文", "プロローグ.md")
FONT_PATH = os.path.join(SHARED, "font", "NotoSansJP-VF.ttf")
TTS_WAV = os.path.join(GC_V, "prologue_tts.wav")
TIMING_F = os.path.join(GC_V, "timing.json")
OUT = os.path.join(GC_V, "release", "GC_ep01_プロローグ_凛音エル_v3.mp4")
TMP = r"C:\Users\GoldRush\Documents\MyProject\AINovel\_vidtmp"; os.makedirs(TMP, exist_ok=True); os.makedirs(os.path.dirname(OUT), exist_ok=True)
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1920, 1080, 30
FONT_SIZE = 38; LINE_H = 56; TEXT_W = 1600; MARGIN_X = (W - TEXT_W) // 2; CPL = 42

def ff(args):
    r = subprocess.run([FFMPEG, "-y", "-loglevel", "error"] + args, capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(r.stderr[-800:])
def probe(path):
    r = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True)
    import re as _re
    m = _re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    return int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3)) if m else 0

import wave
with wave.open(TTS_WAV, "rb") as w:
    TTS_DUR = w.getnframes() / w.getframerate()

with open(SRC, encoding="utf-8") as f:
    paras = [l.strip() for l in f.read().split("\n") if l.strip() and not l.startswith("##")]

def wrap_jp(t):
    out = []
    for sent in re.split(r"(?<=[。！？])", t):
        s = sent.strip()
        if not s: continue
        while len(s) > CPL:
            b = max(s.rfind("、", 0, CPL), s.rfind("。", 0, CPL), 0)
            if b <= 0: b = CPL
            out.append(s[:b]); s = s[b:]
        if s: out.append(s)
    return out

all_lines = []
for _ in range(6): all_lines.append(("", "blank"))
all_lines.append(("Golden Cross", "title"))
all_lines.append(("プロローグ", "title"))
for _ in range(4): all_lines.append(("", "blank"))
for p in paras:
    for wl in wrap_jp(p): all_lines.append((wl, "body"))
for _ in range(10): all_lines.append(("", "blank"))
all_lines.append(("第1章へ", "end"))
for _ in range(6): all_lines.append(("", "blank"))

n_lines = len(all_lines); content_h = n_lines * LINE_H
scroll_h = content_h + H * 2
print(f"Lines:{n_lines} Strip:{scroll_h}px TTS:{TTS_DUR:.0f}s")

# --- シーン定義 ---
SCENES = [
    {"name": "日常",   "bg": os.path.join(BG_DIR, "bg01_street_night.png"),  "bgm": "acoustic52_ast_daily_sound.mp3"},
    {"name": "書斎",   "bg": os.path.join(BG_DIR, "bg02_study_monitor.png"), "bgm": "acoustic52_ast_daily_sound.mp3"},
    {"name": "家族",   "bg": os.path.join(BG_DIR, "bg03_family_dinner.png"), "bgm": "piano37_セピアの風.mp3"},
    {"name": "夜",     "bg": os.path.join(BG_DIR, "bg04_house_lamp.png"),    "bgm": "acoustic52_ast_daily_sound.mp3"},
]
n_scenes = len(SCENES)
scene_dur = TTS_DUR / n_scenes

# --- ストリップ描画（RGBA） ---
strip_p = os.path.join(TMP, "_strip.png")
strip = Image.new("RGBA", (W, scroll_h), (0, 0, 0, 0))
d = ImageDraw.Draw(strip)
fb = ImageFont.truetype(FONT_PATH, FONT_SIZE)
ft = ImageFont.truetype(FONT_PATH, 52)
fe = ImageFont.truetype(FONT_PATH, 40)
yp = 200
for txt, tp in all_lines:
    if tp == "title":
        w2 = d.textlength(txt, font=ft); d.text(((W-w2)//2, yp), txt, font=ft, fill=(245,215,66,255))
    elif tp == "end":
        w2 = d.textlength(txt, font=fe); d.text(((W-w2)//2, yp), txt, font=fe, fill=(170,170,180,255))
    elif tp == "body":
        d.text((MARGIN_X, yp), txt, font=fb, fill=(235,235,240,255))
    yp += LINE_H
strip.save(strip_p)
print("Strip saved")

# --- Step 1: 背景動画（クロスフェード切替） ---
bg_segs = []
for i, sc in enumerate(SCENES):
    im = Image.open(sc["bg"]).convert("RGB")
    bw, bh = im.size; sc_r = max(W/bw, H/bh)
    nw, nh = int(bw*sc_r)+1, int(bh*sc_r)+1
    im = im.resize((nw, nh), Image.LANCZOS)
    cx, cy = (nw-W)//2, (nh-H)//2
    cropped = im.crop((cx, cy, cx+W, cy+H))
    dark = Image.new("RGB", (W, H), (0,0,0))
    cropped = Image.blend(cropped, dark, 100/255.0)
    pth = os.path.join(TMP, f"_sc{i}.png"); cropped.save(pth)
    out_p = os.path.join(TMP, f"_bgs_{i}.mp4")
    fade = ""
    if i > 0: fade += f",fade=t=in:st=0:d=1"
    if i < n_scenes-1: fade += f",fade=t=out:st={scene_dur-1:.1f}:d=1"
    ff(["-loop","1","-framerate",str(FPS),"-i",pth,
        "-vf", f"format=yuv420p{fade}", "-t", f"{scene_dur:.2f}", "-r", str(FPS),
        "-c:v","libx264","-preset","fast","-crf","20", out_p])
    bg_segs.append(out_p)
lst = os.path.join(TMP, "_list.txt")
with open(lst, "w") as f:
    for bp in bg_segs: f.write(f"file '{bp.replace(chr(92),'/')}'\n")
bg_vid = os.path.join(TMP, "_bg_all.mp4")
ff(["-f","concat","-safe","0","-i",lst,"-c","copy", bg_vid])
bg_dur = probe(bg_vid)
print(f"BG video: {bg_dur:.0f}s")

# --- Step 2: テキストスクロール ---
txt_vid = os.path.join(TMP, "_txt.mp4")
rate = scroll_h / TTS_DUR
ff(["-loop","1","-framerate",str(FPS),"-i",strip_p,
    "-vf", f"crop={W}:{H}:0:'max(0,min(ih-{H},trunc(t*{rate:.3f})))',format=rgba",
    "-t", f"{TTS_DUR:.2f}", "-r", str(FPS),
    "-c:v","libx264","-preset","fast","-crf","18",
    "-pix_fmt","yuva420p", txt_vid])
print("Text scroll OK")

# --- Step 3: 合成 ---
final_v = os.path.join(TMP, "_final.mp4")
ff(["-i", bg_vid, "-i", txt_vid,
    "-filter_complex", f"[0:v][1:v]overlay=format=auto,fps={FPS},format=yuv420p[out]",
    "-map","[out]", "-t", f"{TTS_DUR:.2f}", "-r", str(FPS),
    "-c:v","libx264","-preset","fast","-crf","20", final_v])
print("Composite OK")

# --- Step 4: BGM（4トーン・クロスフェード切替） ---
BGMDIR = os.path.join(SHARED, "bgm")
audio_out = os.path.join(TMP, "_audio.m4a")
pieces = []
for i, sc in enumerate(SCENES):
    src = os.path.join(BGMDIR, sc["bgm"])
    pth = os.path.join(TMP, f"_apiece_{i}.wav")
    fade_in = f"afade=t=in:st=0:d=1," if i > 0 else ""
    fade_out = f"afade=t=out:st={scene_dur-1:.1f}:d=1," if i < n_scenes-1 else ""
    ff(["-stream_loop","-1","-i",src, "-t", f"{scene_dur+1:.2f}",
        "-af", f"{fade_in}volume=0.28,{fade_out}asetpts=PTS-STARTPTS",
        "-c:a","pcm_s16le", pth])
    pieces.append(pth)
# 無音ギャップ挿入（曲間0.5秒）
silence = os.path.join(TMP, "_silence.wav")
ff(["-f","lavfi","-i", f"anullsrc=r=44100:cl=stereo", "-t","0.5",
    "-c:a","pcm_s16le", silence])
concat_lst = os.path.join(TMP, "_alist.txt")
with open(concat_lst, "w", encoding="utf-8") as f:
    for i, pth in enumerate(pieces):
        f.write(f"file '{pth.replace(chr(92),'/')}'\n")
        if i < len(pieces)-1:
            f.write(f"file '{silence.replace(chr(92),'/')}'\n")
ff(["-f","concat","-safe","0","-i",concat_lst,
    "-af", f"afade=t=out:st={TTS_DUR-3:.1f}:d=3,volume=1.0",
    "-c:a","aac","-b:a","192k", audio_out])
print("BGM OK")

# --- Step 5: 最終ミックス＆出力 ---
ff(["-i", final_v, "-i", TTS_WAV, "-i", audio_out,
    "-map","0:v","-map","1:a","-map","2:a",
    "-filter_complex", "[1:a]volume=1.0[tts];[2:a]volume=0.3[bgm];[tts][bgm]amix=inputs=2:duration=first:weights=1 0.3[a]",
    "-map","[a]", "-c:v","copy","-c:a","aac","-b:a","192k","-shortest", OUT])

dur_actual = probe(OUT)
size_mb = os.path.getsize(OUT) / 1048576
print(f"\n=== DONE ===\n{OUT}\n{dur_actual/60:.1f}min / {size_mb:.1f}MB")

def probe_dur(path):
    return probe(path)
