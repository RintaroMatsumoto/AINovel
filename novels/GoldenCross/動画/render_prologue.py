# -*- coding: utf-8 -*-
"""GoldenCross プロローグ 動画レンダリング（横型1920×1080・TTS同期）"""
import os, sys, json, math, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\GoldRush\Documents\MyProject\AINovel"
SHARED = os.path.join(ROOT, "novels", "制作共通")
SRC = os.path.join(ROOT, "novels", "GoldenCross", "本文", "プロローグ.md")
IMG_DIR = os.path.join(ROOT, "novels", "GoldenCross", "動画", "images")
BGM_DIR = os.path.join(SHARED, "bgm")
FONT_PATH = os.path.join(SHARED, "font", "NotoSansJP-VF.ttf")
TTS_WAV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prologue_tts.wav")
TIMING = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timing.json")
OUT_DIR = os.path.join(ROOT, "novels", "GoldenCross", "動画", "release")
TMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_render")
os.makedirs(TMP, exist_ok=True); os.makedirs(OUT_DIR, exist_ok=True)

import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

W, H, FPS = 1920, 1080, 30
FONT_SIZE = 36
LINE_HEIGHT = 52
TEXT_WIDTH = 900
MARGIN_X = (W - TEXT_WIDTH) // 2
BOTTOM_OFFSET = 250
BG_COLOR = (10, 10, 18)
OVERLAY_ALPHA = 76  # 約30%

# 挿絵リスト（順番に出現）
IMAGES = [
    "img06_train_night.png",
    "img07_office_win.png",
    "img05_envelope.png",
    "img01_doll.png",
    "img02_goldcoins.png",
    "img03_notebook.png",
]

def wrap_jp(text, max_chars=21):
    lines = []
    for sent in re.split(r"(?<=[。！？])", text):
        s = sent.strip()
        if not s: continue
        while len(s) > max_chars:
            brk = max(s.rfind("、", 0, max_chars), s.rfind("。", 0, max_chars))
            if brk <= 0: brk = max_chars
            lines.append(s[:brk]); s = s[brk:]
        if s: lines.append(s)
    return lines

import re
with open(SRC, encoding="utf-8") as f:
    raw_lines = [l.strip() for l in f.read().split("\n") if l.strip() and not l.startswith("##")]

with open(TIMING, encoding="utf-8") as f:
    tj = json.load(f)
TOTAL_DUR = tj["total_duration"]

# 全行構築（タイトルブランク＋本文＋エンドブランク）
all_lines = []
for _ in range(8): all_lines.append({"text": "", "type": "blank"})
all_lines.append({"text": "Golden Cross", "type": "title"})
all_lines.append({"text": "プロローグ", "type": "title"})
for _ in range(6): all_lines.append({"text": "", "type": "blank"})
for para in raw_lines:
    for wl in wrap_jp(para):
        all_lines.append({"text": wl, "type": "body"})
for _ in range(12): all_lines.append({"text": "", "type": "blank"})
all_lines.append({"text": "第1章へ", "type": "end"})
for _ in range(8): all_lines.append({"text": "", "type": "blank"})

num_lines = len(all_lines)
content_h = num_lines * LINE_HEIGHT
scroll_h = H + BOTTOM_OFFSET + content_h + H
initial_offset = H + BOTTOM_OFFSET - 200
scroll_distance = (scroll_h - H) - initial_offset
scroll_speed = scroll_distance / TOTAL_DUR  # px/sec

print(f"Lines: {num_lines} / Strip: {scroll_h}px / Speed: {scroll_speed:.1f}px/s / TTS: {TOTAL_DUR:.0f}s")

# --- ストリップ描画 ---
strip_path = os.path.join(TMP, "_strip.png")
strip = Image.new("RGB", (W, scroll_h))
d = ImageDraw.Draw(strip)
# グラデ背景
for y in range(scroll_h):
    t = min(1.0, y / (scroll_h * 0.6))
    r, g, b = int(10*(1-t)), int(10*(1-t)), int(32*(1-t))
    d.line([(0, y), (W, y)], fill=(r, g, b))

font_body = ImageFont.truetype(FONT_PATH, FONT_SIZE)
font_title = ImageFont.truetype(FONT_PATH, 52)
font_end = ImageFont.truetype(FONT_PATH, 40)

y_pos = initial_offset
for line_obj in all_lines:
    txt = line_obj["text"]
    tp = line_obj["type"]
    if tp == "title":
        w = d.textlength(txt, font=font_title)
        d.text(((W - w) // 2, y_pos), txt, font=font_title, fill=(245, 215, 66))
    elif tp == "end":
        w = d.textlength(txt, font=font_end)
        d.text(((W - w) // 2, y_pos), txt, font=font_end, fill=(170, 170, 180))
    elif tp == "body":
        d.text((MARGIN_X, y_pos), txt, font=font_body, fill=(230, 230, 235))
    y_pos += LINE_HEIGHT
strip.save(strip_path)
print(f"Strip saved: {strip_path}")

# --- FFmpeg レンダリング ---
out_name = "GC_ep01_プロローグ_凛音エル.mp4"
out_path = os.path.join(OUT_DIR, out_name)

# Step1: スクロールテキスト動画
scroll_vid = os.path.join(TMP, "_scroll.mp4")
run_ff = lambda args: subprocess.run([FFMPEG, "-y", "-loglevel", "error"] + args, check=True, capture_output=True)

vf_scroll = f"crop={W}:{H}:0:'min(ih-{H},max(0,trunc(t*{scroll_speed:.3f})*{H}/max(1,ih-{H})))',format=yuv420p"
# シンプル版：crop y を線形移動
vf_scroll = f"crop={W}:{H}:0:'max(0,min(ih-{H},trunc(t*{scroll_speed:.3f})))',fps={FPS},format=yuv420p"

run_ff(["-loop", "1", "-framerate", str(FPS), "-i", strip_path,
        "-vf", vf_scroll, "-t", f"{TOTAL_DUR:.2f}", "-r", str(FPS),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", scroll_vid])
print(f"Scroll video: {scroll_vid}")

# Step2: 挿絵オーバーレイ（背景合成）
bg_img = os.path.join(IMG_DIR, IMAGES[0])
bg_scaled = os.path.join(TMP, "_bg.png")
bim = Image.open(bg_img).convert("RGB")
bw, bh = bim.size
scale = W / bw if bw / bh > W / H else H / bh
nw, nh = int(bw * scale) + 1, int(bh * scale) + 1
bim = bim.resize((nw, nh), Image.LANCZOS)
cx, cy = (nw - W) // 2, (nh - H) // 2
bim.crop((cx, cy, cx + W, cy + H)).save(bg_scaled)

bg_vid = os.path.join(TMP, "_bg.mp4")
run_ff(["-loop", "1", "-framerate", str(FPS), "-i", bg_scaled,
        "-t", f"{TOTAL_DUR:.2f}", "-r", str(FPS),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", bg_vid])

# 合成：暗いオーバーレイ＋スクロールテキスト
final_v = os.path.join(TMP, "_final_v.mp4")
fc = (
    f"[0:v]eq=brightness=-0.15[bg_dark];"
    f"[bg_dark][1:v]overlay=format=auto[v1];"
    f"[v1][2:v]overlay=format=auto,fps={FPS},format=yuv420p[out]"
)
run_ff(["-i", bg_vid,
        "-i", strip_path,
        "-i", scroll_vid,
        "-filter_complex", fc,
        "-map", "[out]", "-t", f"{TOTAL_DUR:.2f}", "-r", str(FPS),
        "-c:v", "libx264", "-preset", "fast", "-crf", "20", final_v])
print(f"Final video: {final_v}")

# Step3: BGM ミックス
bgm_src = os.path.join(BGM_DIR, "acoustic52_ast_daily_sound.mp3")
bgm_mixed = os.path.join(TMP, "_bgm.m4a")
fade_st = max(0, TOTAL_DUR - 3)
run_ff(["-stream_loop", "-1", "-i", bgm_src, "-t", f"{TOTAL_DUR:.2f}",
        "-af", f"volume=0.25,afade=t=out:st={fade_st:.2f}:d=3",
        "-c:a", "aac", "-b:a", "160k", bgm_mixed])

# Step4: TTS + BGM ミックス＆最終出力
tts_vol = os.path.join(TMP, "_tts_vol.wav")
run_ff(["-i", TTS_WAV, "-af", "volume=1.0", "-c:a", "pcm_s16le", tts_vol])
final = out_path
run_ff(["-i", final_v, "-i", tts_vol, "-i", bgm_mixed,
        "-map", "0:v", "-map", "1:a", "-map", "2:a",
        "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=first:weights=1 0.3[a]",
        "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
        "-shortest", final])
print(f"\n=== DONE ===\n{final}")
