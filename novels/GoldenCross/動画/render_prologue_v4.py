# -*- coding: utf-8 -*-
"""GoldenCross プロローグ v4 —— チャンク同期（段落境界分割版）"""
import os, sys, json, re, subprocess, wave, shutil
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
BGM_DIR = os.path.join(SHARED, "bgm")
OUT = os.path.join(GC_V, "release", "GC_ep01_プロローグ_凛音エル_v4.mp4")
TMP = r"C:\Users\GoldRush\Documents\MyProject\AINovel\_vt4"
shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP); os.makedirs(os.path.dirname(OUT), exist_ok=True)

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
def ff(a):
    r = subprocess.run([FFMPEG, "-y", "-loglevel", "error"] + a, capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(r.stderr[-600:])
def probe(p):
    import re; r = subprocess.run([FFMPEG, "-i", p], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3)) if m else 0

W, H, FPS = 1920, 1080, 30
FS, LH, TW = 38, 52, 1600
MX = (W - TW) // 2; CPL = 44

import wave
with wave.open(TTS_WAV, "rb") as w: TTS_DUR = w.getnframes() / w.getframerate()
with open(TIMING_F, encoding="utf-8") as f: tj = json.load(f)
chunks = tj["chunks"]; total_chars = tj["total_chars"]
n_chunks = len(chunks)

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
for _ in range(4): all_lines.append(("", "blank"))
all_lines.append(("Golden Cross", "title"))
all_lines.append(("プロローグ", "title"))
for _ in range(3): all_lines.append(("", "blank"))
for p in paras:
    for wl in wrap_jp(p): all_lines.append((wl, "body"))
for _ in range(10): all_lines.append(("", "blank"))
all_lines.append(("第1章へ", "end"))
for _ in range(8): all_lines.append(("", "blank"))

n_lines = len(all_lines)
print(f"Lines:{n_lines} TTS:{TTS_DUR:.0f}s Chunks:{n_chunks}")

# --- チャンク境界を段落インデックスにマッピング ---
cum_para_chars = [0]
for p in paras: cum_para_chars.append(cum_para_chars[-1] + len(p))

def find_chunk_boundaries():
    """各チャンクに属する最初の段落インデックスを返す"""
    boundaries = [0]  # チャンク0は段落0から
    target = 0
    ci = 1
    total = sum(len(p) for p in paras)
    acc = 0
    for pi, p in enumerate(paras):
        acc += len(p)
        ratio = acc / total
        while ci < n_chunks and ratio >= ci / n_chunks:
            boundaries.append(pi); ci += 1
    while len(boundaries) < n_chunks:
        boundaries.append(len(paras))
    return boundaries[:n_chunks]

para_bounds = find_chunk_boundaries()
print(f"チャンク段落境界: {para_bounds}")

# --- ストリップ描画（RGBA・単一） ---
strip_p = os.path.join(TMP, "_strip.png")
content_h = n_lines * LH
strip = Image.new("RGBA", (W, content_h), (0,0,0,0))
d = ImageDraw.Draw(strip)
fb = ImageFont.truetype(FONT_PATH, FS)
ftt = ImageFont.truetype(FONT_PATH, 52)
fe = ImageFont.truetype(FONT_PATH, 40)
yp = 100
for txt, tp in all_lines:
    if tp == "title":
        w2 = d.textlength(txt, font=ftt); d.text(((W-w2)//2, yp), txt, font=ftt, fill=(245,215,66,255))
    elif tp == "end":
        w2 = d.textlength(txt, font=fe); d.text(((W-w2)//2, yp), txt, font=fe, fill=(170,170,180,255))
    elif tp == "body":
        d.text((MX, yp), txt, font=fb, fill=(235,235,240,255))
    yp += LH
strip.save(strip_p)
print(f"Strip: {content_h}px")

# --- 背景 ---
bg_src = os.path.join(BG_DIR, "bg01_street_night.png")
bim = Image.open(bg_src).convert("RGB"); bw_, bh_ = bim.size
sc_r = max(W/bw_, H/bh_)
bim = bim.resize((int(bw_*sc_r)+1, int(bh_*sc_r)+1), Image.LANCZOS)
cx, cy = (bim.width-W)//2, (bim.height-H)//2
cropped = bim.crop((cx, cy, cx+W, cy+H))
dark = Image.new("RGB", (W,H), (5,5,15))
cropped = Image.blend(cropped, dark, 110/255.0)
bg_p = os.path.join(TMP, "_bg.png"); cropped.save(bg_p)
bg_vid = os.path.join(TMP, "_bg.mp4")
ff(["-loop","1","-framerate",str(FPS),"-i",bg_p,
    "-t",f"{TTS_DUR:.2f}","-r",str(FPS),
    "-c:v","libx264","-preset","fast","-crf","20","-pix_fmt","yuv420p", bg_vid])

# --- BGM（4トーン切替） ---
TONES = [("acoustic52_ast_daily_sound.mp3", 0.25),
         ("piano37_セピアの風.mp3", 0.25),
         ("acoustic52_ast_daily_sound.mp3", 0.25),
         ("piano37_セピアの風.mp3", 0.25)]
aparts = []
for i, (tn, ratio) in enumerate(TONES):
    dur = TTS_DUR * ratio
    pth = os.path.join(TMP, f"_ap_{i}.wav")
    fi = "afade=t=in:st=0:d=1," if i > 0 else ""
    fo = f",afade=t=out:st={dur-1:.1f}:d=1" if i < len(TONES)-1 else ""
    ff(["-stream_loop","-1","-i",os.path.join(BGM_DIR,tn),"-t",f"{dur:.2f}",
        "-af", f"{fi}volume=0.28{fo}", "-c:a","pcm_s16le", pth])
    aparts.append(pth)
alst = os.path.join(TMP, "_al.txt")
with open(alst, "w") as f:
    for i, ap in enumerate(aparts):
        f.write(f"file '{ap.replace(chr(92),'/')}'\n")
        if i < len(aparts)-1:
            sil = os.path.join(TMP, f"_sil_{i}.wav")
            ff(["-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-t","0.5","-c:a","pcm_s16le", sil])
            f.write(f"file '{sil.replace(chr(92),'/')}'\n")
bgm_all = os.path.join(TMP, "_bgm_all.wav")
ff(["-f","concat","-safe","0","-i",alst,
    "-af", f"afade=t=out:st={TTS_DUR-3:.1f}:d=3",
    "-c:a","pcm_s16le", bgm_all])
print("BGM OK")

# --- チャンク同期スクロール（セグメント分割） ---
# 各チャンクに属する行範囲を計算
line_groups = []
line_idx = 13  # blank×4 + title×2 + blank×3 = 9行をスキップ（本文開始行）
for ci in range(n_chunks):
    start_para = para_bounds[ci]
    end_para = para_bounds[ci+1] if ci+1 < n_chunks else len(paras)
    
    # このチャンクに属する行数をカウント
    n_body_lines = 0
    for pi in range(start_para, end_para):
        n_body_lines += len(wrap_jp(paras[pi]))
    
    # 前のチャンクからの継続分も含める
    if ci == 0:
        n_body_lines += 0  # チャンク0はそのまま
    
    line_groups.append((start_para, end_para, n_body_lines))

# 行グループ→ストリップセグメント
seg_files = []
strip_ypos = 0  # 現在のストリップY位置（行番号×LH）

# タイトル部分を先に処理（全チャンク共通の前置き）
title_strip_h = (4 + 2 + 3) * LH  # blank×4+title×2+blank×3 = 9行
# タイトル部のストリップを切り出し
title_crop = strip.crop((0, 0, W, title_strip_h))
# RGB変換（背景色を黒に合成）
bg_black = Image.new("RGB", (W, title_strip_h), (5, 5, 15))
title_rgb = Image.alpha_composite(bg_black.convert("RGBA"), title_crop).convert("RGB")
title_frame = os.path.join(TMP, "_title_frame.png")
title_rgb.save(title_frame)
title_vid = os.path.join(TMP, "_title_seg.mp4")
title_dur = 12.0  # タイトル表示12秒
ff(["-loop","1","-framerate",str(FPS),"-i",title_frame,
    "-t",f"{title_dur:.1f}","-r",str(FPS),
    "-c:v","libx264","-preset","fast","-crf","20",
    "-pix_fmt","yuv420p", title_vid])

# 実際にはタイトルフレームをストリップから切り出して使う
# （簡略化：最初のセグメントとして扱う）
seg_files.append(title_vid)

# 本文部分：各チャンクごとにストリップセグメントを作成
for ci in range(n_chunks):
    start_para = para_bounds[ci]
    end_para = para_bounds[ci+1] if ci+1 < n_chunks else len(paras)
    d_i = chunks[ci]["duration"]
    
    # このチャンクに属する段落の行を収集
    chunk_lines = []
    for pi in range(start_para, end_para):
        for wl in wrap_jp(paras[pi]):
            chunk_lines.append({"text": wl, "type": "body"})
    
    if not chunk_lines:
        continue
    
    # セグメントストリップ描画
    seg_h = len(chunk_lines) * LH + H  # +H で画面分の余裕
    seg_strip = Image.new("RGBA", (W, seg_h), (0,0,0,0))
    sd = ImageDraw.Draw(seg_strip)
    sy = LH // 2
    for lo in chunk_lines:
        if lo["type"] == "body":
            sd.text((MX, sy), lo["text"], font=fb, fill=(235,235,240,255))
        sy += LH
    seg_p = os.path.join(TMP, f"_chunk_strip_{ci:02d}.png")
    seg_strip.save(seg_p)
    
    # スクロール速度：テキスト量÷時間（最低速度を保証）
    dist = max(1, seg_h - H)  # 最低限スクロールする距離
    rate = dist / d_i
    
    out_p = os.path.join(TMP, f"_segs_{ci:02d}.mp4")
    vf = f"crop={W}:{H}:0:'max(0,min(ih-{H},trunc(t*{rate:.3f})))',format=yuv420p"
    try:
        ff(["-loop","1","-framerate",str(FPS),"-i",seg_p,
            "-vf",vf, "-t",f"{d_i:.2f}", "-r",str(FPS),
            "-c:v","libx264","-preset","fast","-crf","20", out_p])
        seg_files.append(out_p)
        print(f"  chunk {ci}: {d_i:.1f}s rate={rate:.1f}")
    except Exception as e:
        print(f"  chunk {ci}: ERROR {e}")
        raise

print(f"Total segments: {len(seg_files)}")

# --- 全セグメント連結（テキストスクロール） ---
lst = os.path.join(TMP, "_list.txt")
with open(lst, "w") as f:
    for sf in seg_files: f.write(f"file '{sf.replace(chr(92),'/')}'\n")

txt_vid = os.path.join(TMP, "_txt_all.mp4")
ff(["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", txt_vid])

txt_bg_vid = os.path.join(TMP, "_txt_and_bg.mp4")
fc = (
    f"[0:v][1:v]overlay=format=auto,fps={FPS},format=yuv420p[out]"
)
ff(["-i", bg_vid, "-i", txt_vid,
    "-filter_complex", fc, "-map","[out]",
    "-t", f"{TTS_DUR:.2f}", "-r", str(FPS),
    "-c:v","libx264","-preset","fast","-crf","20", txt_bg_vid])

# --- 最終ミックス ---
ff(["-i", txt_bg_vid, "-i", TTS_WAV, "-i", bgm_all,
    "-map","0:v","-map","1:a","-map","2:a",
    "-filter_complex", "[1:a]volume=1.0[tts];[2:a]volume=0.28[bgm];[tts][bgm]amix=inputs=2:duration=first[a]",
    "-map","[a]", "-c:v","copy","-c:a","aac","-b:a","192k","-shortest", OUT])

dur_a = probe(OUT); size_mb = os.path.getsize(OUT)/1048576
print(f"\n=== DONE ===\n{OUT}\n{dur_a/60:.1f}min / {size_mb:.1f}MB")
