# -*- coding: utf-8 -*-
"""GoldenCross プロローグ v7 — フレーム単位チャンク同期（ズレ完全解消）"""
import os, sys, json, re, subprocess, wave, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = r"C:\Users\GoldRush\Documents\MyProject\AINovel"
SHARED = os.path.join(ROOT, "novels", "制作共通")
GC_V = os.path.join(ROOT, "novels", "GoldenCross", "動画")
SRC = os.path.join(ROOT, "novels", "GoldenCross", "本文", "プロローグ.md")
FONT_PATH = os.path.join(SHARED, "font", "NotoSansJP-VF.ttf")
TTS_WAV = os.path.join(GC_V, "prologue_tts.wav")
TIMING_F = os.path.join(GC_V, "timing.json")
BGM_SRC = os.path.join(SHARED, "bgm", "acoustic52_ast_daily_sound.mp3")
OUT = os.path.join(GC_V, "release", "GC_ep01_プロローグ_v7.mp4")
TMP = os.path.join(GC_V, "_v7"); os.makedirs(TMP, exist_ok=True)
os.makedirs(os.path.dirname(OUT), exist_ok=True)

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1920, 1080, 30
FS, LH = 42, 58
TW = 1700; MX = (W - TW) // 2; CPL = 44

# --- 本文パース ---
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
for _ in range(3): all_lines.append(("", "blank"))
all_lines.append(("Golden Cross", "title"))
all_lines.append(("プロローグ", "title"))
for _ in range(3): all_lines.append(("", "blank"))
for p in paras:
    for wl in wrap_jp(p): all_lines.append((wl, "body"))
for _ in range(8): all_lines.append(("", "blank"))
all_lines.append(("第1章へ", "end"))
for _ in range(6): all_lines.append(("", "blank"))

n_lines = len(all_lines); LH = 52; content_h = n_lines * LH
print(f"Lines:{n_lines} Content:{content_h}px")

# --- ストリップ描画（黒背景＋白文字・RGB） ---
strip_img = Image.new("RGB", (W, content_h), (8, 8, 12))
d = ImageDraw.Draw(strip_img)
fb = ImageFont.truetype(FONT_PATH, FS)
ft = ImageFont.truetype(FONT_PATH, 56)
fe = ImageFont.truetype(FONT_PATH, 40)
yp = 50
for txt, tp in all_lines:
    if tp == "title":
        w2 = d.textlength(txt, font=ft); d.text(((W-w2)//2, yp), txt, font=ft, fill=(245,215,66))
    elif tp == "end":
        w2 = d.textlength(txt, font=fe); d.text(((W-w2)//2, yp), txt, font=fe, fill=(170,170,180))
    elif tp == "body":
        d.text((MX, yp), txt, font=fb, fill=(235,235,240))
    yp += LH
strip_arr = np.asarray(strip_img)  # (content_h, W, 3) uint8
print(f"Strip rendered: {strip_arr.shape}")

# --- timing.json から時間→Y位置マッピング構築 ---
with open(TIMING_F, encoding="utf-8") as f:
    tj = json.load(f)
chunks = tj["chunks"]
total_chars = tj["total_chars"]; total_dur = tj["total_duration"]
TTS_DUR = total_dur

# 各チャンクの累積文字位置と時間
cum_chars = [0]
cum_time = [0.0]
for ch in chunks:
    cum_chars.append(cum_chars[-1] + ch["chars"])
    cum_time.append(cum_time[-1] + ch["duration"])

# 文字位置→ストリップY座標のマッピング
def char_to_y(cp):
    return int(cp / total_chars * content_h)

# 時間→文字位置（区分線形補間）
def time_to_char(t):
    for i in range(len(chunks)):
        t0, t1 = cum_time[i], cum_time[i+1]
        c0, c1 = cum_chars[i], cum_chars[i+1]
        if t0 <= t <= t1:
            frac = (t - t0) / (t1 - t0) if t1 > t0 else 0
            return c0 + frac * (c1 - c0)
    return total_chars if t > total_dur else 0

# 時間→Y位置
def time_to_y(t):
    cp = time_to_char(t)
    y_base = char_to_y(cp)
    # 画面中央にテキストが来るようにオフセット
    return max(0, min(content_h - H, y_base))

print(f"Time mapping: {len(chunks)} chunks, {total_dur:.1f}s, {total_chars} chars")

# --- フレーム生成＆FFmpegパイプ ---
out_vid = os.path.join(TMP, "_video.mp4")
total_frames = int(TTS_DUR * FPS)

proc = subprocess.Popen(
    [FFMPEG, "-y", "-loglevel", "error",
     "-f", "rawvideo", "-pix_fmt", "bgr24",
     "-s", f"{W}x{H}", "-r", str(FPS),
     "-i", "-",
     "-c:v", "libx264", "-preset", "fast", "-crf", "20",
     "-pix_fmt", "yuv420p",
     out_vid],
    stdin=subprocess.PIPE, stderr=subprocess.PIPE)

print(f"Rendering {total_frames} frames...", flush=True)
bg_frame = np.full((H, W, 3), (8, 8, 12), dtype=np.uint8)

for frame_num in range(total_frames):
    t = frame_num / FPS
    y = time_to_y(t)
    # ストリップから切り出し（numpy高速スライス）
    y_end = y + H
    if y_end <= content_h:
        frame = strip_arr[y:y_end]
    else:
        # 端：残りを暗部で埋める
        visible = content_h - y
        frame = np.vstack([strip_arr[y:content_h],
                          np.full((H - max(0,visible), W, 3), (8,8,12), dtype=np.uint8)])
    # BGR変換（FFmpegはBGR期待）
    frame_bgr = frame[:, :, ::-1]
    proc.stdin.write(frame_bgr.tobytes())
    
    if frame_num % (FPS * 60) == 0:
        print(f"  {t/60:.0f}min...", flush=True)

proc.stdin.close()
proc.wait()
if proc.returncode != 0:
    print(f"FFmpeg error: {proc.stderr.read().decode()[:500]}")
    sys.exit(1)
print("Video OK")

# --- 音声 ---
bgm_m4a = os.path.join(TMP, "_bgm.m4a")
fade_st = max(0, TTS_DUR - 3)
subprocess.run([FFMPEG, "-y", "-loglevel", "error",
    "-stream_loop", "-1", "-i", BGM_SRC, "-t", f"{TTS_DUR:.2f}",
    "-af", f"volume=0.22,afade=t=out:st={fade_st:.2f}:d=3",
    "-c:a", "aac", "-b:a", "192k", bgm_m4a], check=True)

final = OUT
subprocess.run([FFMPEG, "-y", "-loglevel", "error",
    "-i", out_vid, "-i", TTS_WAV, "-i", bgm_m4a,
    "-map", "0:v", "-map", "1:a", "-map", "2:a",
    "-filter_complex",
    "[1:a]volume=1.0[tts];[2:a]volume=0.22[bgm];[tts][bgm]amix=inputs=2:duration=first[a]",
    "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart", final], check=True)

dur_s = os.path.getsize(final) / 1048576
print(f"\n=== DONE ===\n{final}\n{TTS_DUR/60:.1f}min / {dur_s:.1f}MB")
