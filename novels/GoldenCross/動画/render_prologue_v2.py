# -*- coding: utf-8 -*-
"""GoldenCross プロローグ v2 —— シンプル堅牢版"""
import os, sys, json, re, subprocess
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = r"C:\Users\GoldRush\Documents\MyProject\AINovel"
SHARED = os.path.join(ROOT, "novels", "制作共通")
GC_V = os.path.join(ROOT, "novels", "GoldenCross", "動画")
SRC = os.path.join(ROOT, "novels", "GoldenCross", "本文", "プロローグ.md")
IMG_DIR = os.path.join(GC_V, "images")
FONT_PATH = os.path.join(SHARED, "font", "NotoSansJP-VF.ttf")
TTS_WAV = os.path.join(GC_V, "prologue_tts.wav")
TIMING_F = os.path.join(GC_V, "timing.json")
BGM_SRC = os.path.join(SHARED, "bgm", "acoustic52_ast_daily_sound.mp3")
OUT = os.path.join(GC_V, "release", "GC_ep01_プロローグ_凛音エル_v2.mp4")
TMP = os.path.join(GC_V, "_r2"); os.makedirs(TMP, exist_ok=True)

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1920, 1080, 30
FONT_SIZE = 38
LINE_H = 56
TEXT_W = 1600
MARGIN_X = (W - TEXT_W) // 2
CHARS_PER_LINE = 42

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
        while len(s) > CHARS_PER_LINE:
            b = max(s.rfind("、", 0, CHARS_PER_LINE), s.rfind("。", 0, CHARS_PER_LINE), 0)
            if b <= 0: b = CHARS_PER_LINE
            out.append(s[:b]); s = s[b:]
        if s: out.append(s)
    return out

all_lines = []
for _ in range(8): all_lines.append(("", "blank"))
all_lines.append(("Golden Cross", "title"))
all_lines.append(("プロローグ", "title"))
for _ in range(5): all_lines.append(("", "blank"))
for p in paras:
    for wl in wrap_jp(p): all_lines.append((wl, "body"))
for _ in range(12): all_lines.append(("", "blank"))
all_lines.append(("第1章へ", "end"))
for _ in range(8): all_lines.append(("", "blank"))

n_lines = len(all_lines)
content_h = n_lines * LINE_H
scroll_h = H + content_h + H * 2
init_off = H - 200

print(f"Lines:{n_lines} Strip:{scroll_h}px TTS:{TTS_DUR:.0f}s")

# --- ストリップ描画（RGBA透明） ---
strip = Image.new("RGBA", (W, scroll_h), (0, 0, 0, 0))
d = ImageDraw.Draw(strip)
fb = ImageFont.truetype(FONT_PATH, FONT_SIZE)
ft = ImageFont.truetype(FONT_PATH, 52)
fe = ImageFont.truetype(FONT_PATH, 40)

yp = init_off + H
for txt, tp in all_lines:
    if tp == "title":
        w2 = d.textlength(txt, font=ft)
        d.text(((W - w2) // 2, yp), txt, font=ft, fill=(245, 215, 66, 255))
    elif tp == "end":
        w2 = d.textlength(txt, font=fe)
        d.text(((W - w2) // 2, yp), txt, font=fe, fill=(170, 170, 180, 255))
    elif tp == "body":
        d.text((MARGIN_X, yp), txt, font=fb, fill=(235, 235, 240, 255))
    yp += LINE_H

strip_p = os.path.join(TMP, "_strip.png")
strip.save(strip_p)
print("Strip saved")

# --- 背景（単一画像・暗オーバーレイ） ---
bg_src = os.path.join(IMG_DIR, "img06_train_night.png")
bim = Image.open(bg_src).convert("RGB")
bw, bh = bim.size
sc = max(W / bw, H / bh)
nw, nh = int(bw * sc) + 1, int(bh * sc) + 1
bim = bim.resize((nw, nh), Image.LANCZOS)
cx, cy = (nw - W) // 2, (nh - H) // 2
cropped = bim.crop((cx, cy, cx + W, cy + H))
dark = Image.new("RGB", (W, H), (5, 5, 15))
cropped = Image.blend(cropped, dark, 110 / 255.0)  # 約43%暗く
bg_p = os.path.join(TMP, "_bg.png")
cropped.save(bg_p)

# --- FFmpeg Step1: 背景動画 ---
bg_vid = os.path.join(TMP, "_bg.mp4")
subprocess.run([FFMPEG, "-y", "-loglevel", "error",
    "-loop", "1", "-framerate", str(FPS), "-i", bg_p,
    "-t", f"{TTS_DUR:.2f}", "-r", str(FPS),
    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
    "-pix_fmt", "yuv420p", bg_vid], check=True, capture_output=True)
print("BG video OK")

# --- FFmpeg Step2: テキストスクロール ---
txt_vid = os.path.join(TMP, "_txt.mp4")
rate = scroll_distance / TTS_DUR if 'scroll_distance' in dir() else (scroll_h - H - init_off) / TTS_DUR
vf = f"crop={W}:{H}:0:'max(0,min(ih-{H},trunc(t*{rate:.3f})))',format=rgba"
subprocess.run([FFMPEG, "-y", "-loglevel", "error",
    "-loop", "1", "-framerate", str(FPS), "-i", strip_p,
    "-vf", vf, "-t", f"{TTS_DUR:.2f}", "-r", str(FPS),
    "-c:v", "libx264", "-preset", "fast", "-crf", "18",
    "-pix_fmt", "yuva420p", txt_vid], check=True, capture_output=True)
print("Text scroll OK")

# --- FFmpeg Step3: 合成 ---
final_v = os.path.join(TMP, "_final.mp4")
fc = f"[0:v][1:v]overlay=format=auto,fps={FPS},format=yuv420p[out]"
subprocess.run([FFMPEG, "-y", "-loglevel", "error",
    "-i", bg_vid, "-i", txt_vid,
    "-filter_complex", fc, "-map", "[out]",
    "-t", f"{TTS_DUR:.2f}", "-r", str(FPS),
    "-c:v", "libx264", "-preset", "fast", "-crf", "20", final_v], check=True, capture_output=True)
print("Composite OK")

# --- FFmpeg Step4: BGM ---
bgm_m4a = os.path.join(TMP, "_bgm.m4a")
fade_st = max(0, TTS_DUR - 3)
subprocess.run([FFMPEG, "-y", "-loglevel", "error",
    "-stream_loop", "-1", "-i", BGM_SRC, "-t", f"{TTS_DUR:.2f}",
    "-af", f"volume=0.25,afade=t=out:st={fade_st:.1f}:d=3",
    "-c:a", "aac", "-b:a", "192k", bgm_m4a], check=True, capture_output=True)
print("BGM OK")

# --- FFmpeg Step5: TTS＋BGM ミックス＆最終出力 ---
subprocess.run([FFMPEG, "-y", "-loglevel", "error",
    "-i", final_v, "-i", TTS_WAV, "-i", bgm_m4a,
    "-map", "0:v", "-map", "1:a", "-map", "2:a",
    "-filter_complex",
    "[1:a]volume=1.0[tts];[2:a]volume=0.3[bgm];[tts][bgm]amix=inputs=2:duration=first[a]",
    "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
    "-shortest", OUT], check=True, capture_output=True)
print(f"\n=== DONE ===\n{OUT}")
