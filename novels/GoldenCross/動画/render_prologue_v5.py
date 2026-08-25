# -*- coding: utf-8 -*-
import os, sys, json, re, subprocess, wave, shutil
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = r'C:\Users\GoldRush\Documents\MyProject\AINovel'
SHARED = os.path.join(ROOT, 'novels', '制作共通')
GC_V = os.path.join(ROOT, 'novels', 'GoldenCross', '動画')
BG_DIR = os.path.join(GC_V, '_bg_images')
SRC = os.path.join(ROOT, 'novels', 'GoldenCross', '本文', 'プロローグ.md')
FONT_PATH = os.path.join(SHARED, 'font', 'NotoSansJP-VF.ttf')
TTS_WAV = os.path.join(GC_V, 'prologue_tts.wav')
TIMING_F = os.path.join(GC_V, 'timing.json')
BGM_DIR = os.path.join(SHARED, 'bgm')
OUT = os.path.join(GC_V, 'release', 'GC_ep01_プロローグ_凛音エル_v5.mp4')
TMP = r'C:\Users\GoldRush\Documents\MyProject\AINovel\_vt5'
shutil.rmtree(TMP, ignore_errors=True); os.makedirs(TMP); os.makedirs(os.path.dirname(OUT), exist_ok=True)

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
def ff(a):
    r = subprocess.run([FFMPEG, '-y', '-loglevel', 'error'] + a, capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(r.stderr[-600:])
def probe(p):
    import re; r = subprocess.run([FFMPEG, '-i', p], capture_output=True, text=True)
    m = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', r.stderr)
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3)) if m else 0

W, H, FPS = 1920, 1080, 30
FS, LH, TW = 38, 52, 1700
MX = (W - TW) // 2; CPL = 44

import wave
with wave.open(TTS_WAV, 'rb') as w: TTS_DUR = w.getnframes() / w.getframerate()
with open(TIMING_F, encoding='utf-8') as f: tj = json.load(f)
chunks = tj['chunks']; total_chars = tj['total_chars']

with open(SRC, encoding='utf-8') as f:
    paras = [l.strip() for l in f.read().split('\n') if l.strip() and not l.startswith('##')]

def wrap_jp(t):
    out = []
    for sent in re.split(r'(?<=[。！？])', t):
        s = sent.strip()
        if not s: continue
        while len(s) > CPL:
            b = max(s.rfind('、', 0, CPL), s.rfind('。', 0, CPL), 0)
            if b <= 0: b = CPL
            out.append(s[:b]); s = s[b:]
        if s: out.append(s)
    return out

all_lines = []
for _ in range(4): all_lines.append(('', 'blank'))
all_lines.append(('Golden Cross', 'title'))
all_lines.append(('プロローグ', 'title'))
for _ in range(3): all_lines.append(('', 'blank'))
for p in paras:
    for wl in wrap_jp(p): all_lines.append((wl, 'body'))
for _ in range(10): all_lines.append(('', 'blank'))
all_lines.append(('第1章へ', 'end'))
for _ in range(6): all_lines.append(('', 'blank'))

n_lines = len(all_lines)
content_h = n_lines * LH
scroll_h = content_h + H
print(f'Lines:{n_lines} Strip:{scroll_h}px TTS:{TTS_DUR:.0f}s')

# 背景画像（暗くして準備）
bg_src = os.path.join(BG_DIR, 'bg01_street_night.png')
bim = Image.open(bg_src).convert('RGB')
bw_, bh_ = bim.size; sc_r = max(W/bw_, H/bh_)
bim = bim.resize((int(bw_*sc_r)+1, int(bh_*sc_r)+1), Image.LANCZOS)
cx, cy = (bim.width-W)//2, (bim.height-H)//2
cropped = bim.crop((cx, cy, cx+W, cy+H))
dark = Image.new('RGB', (W,H), (5,5,15))
cropped = Image.blend(cropped, dark, 120/255.0)
print('BG prepared')

# ストリップ描画（背景＋テキスト合成済み・一枚の不透明画像）
strip_p = os.path.join(TMP, '_strip.png')
strip = Image.new('RGB', (W, scroll_h))
y_fill = 0
while y_fill < scroll_h:
    strip.paste(cropped, (0, y_fill)); y_fill += H

d = ImageDraw.Draw(strip)
fb = ImageFont.truetype(FONT_PATH, FS)
ft = ImageFont.truetype(FONT_PATH, 52)
fe = ImageFont.truetype(FONT_PATH, 40)

yp = 200
for txt, tp in all_lines:
    if tp == 'title':
        w2 = d.textlength(txt, font=ft)
        d.text(((W-w2)//2, yp), txt, font=ft, fill=(245,215,66))
    elif tp == 'end':
        w2 = d.textlength(txt, font=fe)
        d.text(((W-w2)//2, yp), txt, font=fe, fill=(180,180,190))
    elif tp == 'body':
        d.text((MX+2, yp+2), txt, font=fb, fill=(20,20,20))
        d.text((MX, yp), txt, font=fb, fill=(235,235,240))
    yp += LH
strip.save(strip_p)
print('Strip saved')

# FFmpeg: スクロール
rate = scroll_h / TTS_DUR
scroll_vid = os.path.join(TMP, '_scroll.mp4')
ff(['-loop','1','-framerate',str(FPS),'-i',strip_p,
    '-vf', f'crop={W}:{H}:0:max(0\\,min(ih-{H}\\,trunc(t*{rate:.3f})))',
    '-t', f'{TTS_DUR:.2f}', '-r', str(FPS),
    '-c:v','libx264','-preset','fast','-crf','20',
    '-pix_fmt','yuv420p', scroll_vid])
print('Scroll OK')

# BGM
bgm_m4a = os.path.join(TMP, '_bgm.m4a')
fade_st = max(0, TTS_DUR - 3)
ff(['-stream_loop','-1','-i',os.path.join(BGM_DIR,'acoustic52_ast_daily_sound.mp3'),
    '-t', f'{TTS_DUR:.2f}',
    '-af', f'volume=0.25,afade=t=out:st={fade_st:.1f}:d=3',
    '-c:a','aac','-b:a','192k', bgm_m4a])
print('BGM OK')

# 最終ミックス
ff(['-i', scroll_vid, '-i', TTS_WAV, '-i', bgm_m4a,
    '-map','0:v','-map','1:a','-map','2:a',
    '-filter_complex',
    '[1:a]volume=1.0[tts];[2:a]volume=0.25[bgm];[tts][bgm]amix=inputs=2:duration=first[a]',
    '-map','[a]', '-c:v','copy','-c:a','aac','-b:a','192k',
    '-shortest', OUT])
dur_a = probe(OUT); size_mb = os.path.getsize(OUT)/1048576
print(f'=== DONE === {OUT}')
print(f'{dur_a/60:.1f}min / {size_mb:.1f}MB')
