# -*- coding: utf-8 -*-
"""GoldenCross プロローグ — ページ方式（ズレ構造的に不可能）"""
import os, sys, json, re, subprocess, wave, shutil, math
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
def ff(a):
    r = subprocess.run([FFMPEG, "-y", "-loglevel", "error"] + a, capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(r.stderr[-600:])

ROOT = r"C:\Users\GoldRush\Documents\MyProject\AINovel"
SHARED = os.path.join(ROOT, "novels", "制作共通")
GC_V = os.path.join(ROOT, "novels", "GoldenCross", "動画")
BG_DIR = os.path.join(GC_V, "_bg_images")
SRC = os.path.join(ROOT, "novels", "GoldenCross", "本文", "プロローグ.md")
FONT_PATH = os.path.join(SHARED, "font", "NotoSansJP-VF.ttf")
TTS_WAV = os.path.join(GC_V, "prologue_tts.wav")
TIMING_F = os.path.join(GC_V, "timing.json")
BGM_DIR = os.path.join(SHARED, "bgm")
OUT = os.path.join(GC_V, "release", "GC_ep01_プロローグ_ページ方式.mp4")
TMP = r"C:\Users\GoldRush\Documents\MyProject\AINovel\_pg7"
shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP); os.makedirs(os.path.dirname(OUT), exist_ok=True)

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1920, 1080, 30

import wave
with wave.open(TTS_WAV, "rb") as w:
    TTS_DUR = w.getnframes() / w.getframerate()

with open(TIMING_F, encoding="utf-8") as f:
    tj = json.load(f)
chunks = tj["chunks"]
total_chars = sum(ch["chars"] for ch in chunks)
cps = total_chars / TTS_DUR  # 平均読速（字/秒）

print(f"TTS: {TTS_DUR:.1f}s / {total_chars}chars / {cps:.1f}c/s")

# --- 本文読み込み・段落分割 ---
with open(SRC, encoding="utf-8") as f:
    paras = [l.strip() for l in f.read().split("\n") if l.strip() and not l.startswith("##")]

def wrap_lines(t, width=40):
    out = []
    for sent in re.split(r"(?<=[。！？])", t):
        s = sent.strip()
        if not s: continue
        while len(s) > width:
            b = max(s.rfind("、", 0, width), s.rfind("。", 0, width), 0)
            if b <= 0: b = width
            out.append(s[:b]); s = s[b:]
        if s: out.append(s)
    return out

# --- スライドグループ作成 ---
# タイトルスライド
title_slide = {
    "lines": [("Golden Cross", "title"), ("プロローグ", "subtitle")],
    "dur": 6.0,
    "bg": None,
}

# 本文スライド：2〜3段落ごとにグループ化
body_paras = paras[:]
slide_paras = []
current_group = []
current_chars = 0
for p in body_paras:
    current_group.append(p)
    current_chars += len(p)
    if current_chars >= 180:  # 約180字で1スライド
        slide_paras.append(current_group)
        current_group = []
        current_chars = 0
if current_group:
    slide_paras.append(current_group)

print(f"本文スライド数: {len(slide_paras)}")

# 各スライドの表示時間をTTSチャンクから比例配分
total_body_chars = sum(sum(len(p) for p in grp) for grp in slide_paras)
time_per_char = TTS_DUR / total_body_chars

# 背景画像リスト（シーンごとに切替）
bg_files = [
    os.path.join(BG_DIR, "bg01_street_night.png"),
    os.path.join(BG_DIR, "bg02_study_monitor.png"),
    os.path.join(BG_DIR, "bg03_family_dinner.png"),
    os.path.join(BG_DIR, "bg04_house_lamp.png"),
]

font_title = ImageFont.truetype(FONT_PATH, 64)
font_sub = ImageFont.truetype(FONT_PATH, 44)
font_body = ImageFont.truetype(FONT_PATH, 40)
font_small = ImageFont.truetype(FONT_PATH, 28)
MX = (W - 1700) // 2

def render_slide(lines, bg_img=None):
    """スライド画像を描画"""
    if bg_img and os.path.exists(bg_img):
        bim = Image.open(bg_img).convert("RGB")
        bw_, bh_ = bim.size
        sc_r = max(W/bw_, H/bh_)
        bim = bim.resize((int(bw_*sc_r)+1, int(bh_*sc_r)+1), Image.LANCZOS)
        cx, cy = (bim.width-W)//2, (bim.height-H)//2
        img = bim.crop((cx, cy, cx+W, cy+H))
        dark = Image.new("RGB", (W,H), (0,0,0))
        img = Image.blend(img, dark, 140/255.0)  # 55%暗く
    else:
        img = Image.new("RGB", (W,H), (8,8,14))
    
    d = ImageDraw.Draw(img)
    
    y_start = H // 2 - len(lines) * 36
    
    for line_data in lines:
        txt = line_data[0]
        tp = line_data[1] if len(line_data) > 1 else "body"
        
        if tp == "title":
            w = d.textlength(txt, font=font_title)
            d.text(((W-w)//2, H//2-80), txt, font=font_title, fill=(245,215,66))
        elif tp == "subtitle":
            w = d.textlength(txt, font=font_sub)
            d.text(((W-w)//2, H//2+20), txt, font=font_sub, fill=(220,220,230))
        elif tp == "end":
            w = d.textlength(txt, font=font_body)
            d.text(((W-w)//2, H//2-30), txt, font=font_body, fill=(180,180,190))
        else:
            # 本文：影→本体
            d.text((MX+2, y_start+2), txt, font=font_body, fill=(15,15,20))
            d.text((MX, y_start), txt, font=font_body, fill=(240,240,245))
        y_start += 62
    
    return img

# --- スライド画像一括生成 ---
slides = []

# タイトルスライド
tl = [(t, t2) for t, t2 in title_slide["lines"]]
tpath = os.path.join(TMP, "slide_000.png")
render_slide(tl).save(tpath)
slides.append({"img": tpath, "dur": title_slide["dur"]})

# 本文スライド
for si, grp in enumerate(slide_paras):
    lines = []
    total_grp_chars = 0
    for p in grp:
        for wl in wrap_lines(p):
            lines.append((wl, "body"))
            total_grp_chars += len(wl)
    
    dur = total_grp_chars * time_per_char
    dur = max(3.0, dur)  # 最低3秒
    
    # 背景：4枚を順番に割り当て
    bg_idx = min(si * len(bg_files) // max(1, len(slide_paras)), len(bg_files)-1)
    bg = bg_files[bg_idx]
    
    pth = os.path.join(TMP, f"slide_{si+1:03d}.png")
    render_slide([(l[0], l[1]) for l in lines], bg).save(pth)
    slides.append({"img": pth, "dur": dur})

# エンドスライド
epath = os.path.join(TMP, f"slide_{len(slides)+1:03d}.png")
render_slide([("第1章へ", "end")]).save(epath)
slides.append({"img": epath, "dur": 4.0})

total_slides = len(slides)
total_vid_dur = sum(s["dur"] for s in slides)
print(f"Total slides: {total_slides} / Video duration: {total_vid_dur:.1f}s")

# --- FFmpeg: 動画構築 ---
# Step 1: 各スライドをセグメント動画化
seg_files = []
for i, sl in enumerate(slides):
    out_p = os.path.join(TMP, f"_vid_{i:03d}.mp4")
    fade_in = ",fade=t=in:st=0:d=0.5" if i > 0 else ""
    fade_out = f",fade=t=out:st={sl['dur']-0.5:.1f}:d=0.5" if i < total_slides-1 else ""
    ff(["-loop","1","-framerate",str(FPS),"-i",sl["img"],
        "-vf", f"scale={W}:{H},format=yuv420p{fade_in}{fade_out}",
        "-t", f"{sl['dur']:.2f}", "-r", str(FPS),
        "-c:v","libx264","-preset","fast","-crf","20", out_p])
    seg_files.append(out_p)
    print(f"  slide {i+1}/{total_slides}: {sl['dur']:.1f}s")

# Step 2: 連結
lst = os.path.join(TMP, "_list.txt")
with open(lst, "w") as f:
    for sf in seg_files: f.write(f"file '{sf.replace(chr(92),'/')}'\n")
video_noaudio = os.path.join(TMP, "_video.mp4")
ff(["-f","concat","-safe","0","-i",lst,"-c","copy", video_noaudio])

# Step 3: TTS音声を全尺にループ延長
tts_full = os.path.join(TMP, "_tts_full.m4a")
fade_st = max(0, TTS_DUR - 3)
ff(["-i", TTS_WAV, "-af", f"apad=whole_dur={total_vid_dur:.1f},afade=t=out:st={total_vid_dur-3:.1f}:d=3",
    "-c:a","aac","-b:a","192k", tts_full])

# Step 4: BGM構築（4トーン切替）
TONES = [
    ("acoustic52_ast_daily_sound.mp3", 0.25),
    ("piano37_セピアの風.mp3", 0.25),
    ("acoustic52_ast_daily_sound.mp3", 0.25),
    ("piano37_セピアの風.mp3", 0.25),
]
bgm_segs = []
acc = 0.0
for i, (tn, ratio) in enumerate(TONES):
    dur = total_vid_dur * ratio
    src = os.path.join(BGM_DIR, tn)
    pth = os.path.join(TMP, f"_bgm_{i}.wav")
    fi = "afade=t=in:st=0:d=1," if i > 0 else ""
    fo = f",afade=t=out:st={dur-1:.1f}:d=1" if i < len(TONES)-1 else ""
    ff(["-stream_loop","-1","-i",src,"-t",f"{dur:.2f}",
        "-af", f"{fi}volume=0.22{fo}", "-c:a","pcm_s16le", pth])
    bgm_segs.append(pth)

blst = os.path.join(TMP, "_bl.txt")
with open(blst, "w") as f:
    for bp in bgm_segs: f.write(f"file '{bp.replace(chr(92),'/')}'\n")
bgm_full = os.path.join(TMP, "_bgm_full.wav")
ff(["-f","concat","-safe","0","-i",blst,
    "-af", f"afade=t=out:st={total_vid_dur-3:.1f}:d=3",
    "-c:a","pcm_s16le", bgm_full])

# Step 5: 最終ミックス（TTS音声＋BGM）
final = OUT
ff(["-i", video_noaudio, "-i", tts_full, "-i", bgm_full,
    "-map","0:v","-map","1:a","-map","2:a",
    "-filter_complex",
    "[1:a]volume=0.9[tts];[2:a]volume=0.25[bgm];[tts][bgm]amix=inputs=2:duration=first[a]",
    "-map","[a]", "-c:v","copy","-c:a","aac","-b:a","192k",
    "-movflags","+faststart", final])

size_mb = os.path.getsize(final)/1048576
print(f"\n=== DONE ===\n{final}\n{total_vid_dur/60:.1f}min / {size_mb:.1f}MB")
