# -*- coding: utf-8 -*-
"""GoldenCross スロスク動画 レンダリングパイプライン"""
import os, re, sys, json, subprocess, math
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\GoldRush\Documents\MyProject\AINovel"
SHARED = os.path.join(ROOT, r"novels\制作共通")
SRC_DIR = os.path.join(ROOT, r"novels\GoldenCross\本文")
IMG_DIR = os.path.join(ROOT, r"novels\GoldenCross\動画\images")
ASSETS = os.path.join(SHARED, "bgm")
OUT_DIR = os.path.join(ROOT, r"novels\GoldenCross\動画\release")
TMP_DIR = os.path.join(ROOT, r"novels\GoldenCross\動画\tmp")
for d in (OUT_DIR, TMP_DIR): os.makedirs(d, exist_ok=True)

FFMPEG = None
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

W, H = 1080, 1920
FONT_BODY = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\制作共通\font\NotoSansJP-VF.ttf"
FONT_TITLE = FONT_BODY
F_BODY = ImageFont.truetype(FONT_BODY, 58)
F_TITLE_S = ImageFont.truetype(FONT_TITLE, 54)
F_TITLE_L = ImageFont.truetype(FONT_TITLE, 92)
BG = (10, 10, 12)
WHITE = (240, 240, 240)
BLUE = (168, 184, 208)
GOLD = (201, 162, 39)
CHARS_PER_LINE = 15
MAX_LINES = 4
CPS = 9.2          # 読速（字/秒）
FPS = 24
GAP_DUR = 0.35     # グループ間ブラックアウト
IMG_DUR = 5.0      # 画像カード表示秒

EPISODES = [
    dict(ep=1, src="プロローグ.md",  title="プロローグ", sub="1億円の夜", bgm="theme",
         thumb=("img09_familyphoto.png", "1億円を稼いだ男の、\n最後の平穏な夜。"), blue=None, cues=[]),
    dict(ep=2, src="第1章.md", title="第1章", sub="退職願と、祖父のノート", bgm="v1",
         thumb=("img01_doll.png", "祖父が残したのは、\nノートだった。"),
         blue=None,
         cues=[("順番通りに去っていく。", "img06_train_night.png"),
               ("部長の席へ向かった。", "img05_envelope.png"),
               ("皇居の緑が見える。", "img07_office_win.png"),
               ("いわゆるフランス人形というやつだ。", "img01_doll.png"),
               ("一冊のノート。", "img03_notebook.png"),
               ("うちの灯りが見えた。", "img08_house_night.png")]),
    dict(ep=3, src="第2章.md", title="第2章", sub="最後の出社日", bgm="v2",
         thumb=("img10_brown_env.png", "差出人のいない\n封筒が届いた。"), blue=None,
         cues=[("そこにあった。", "img10_brown_env.png"),
               ("同じ人だった。", "img11_photos.png"),
               ("包丁の音が一定のリズムで続いている。", "img12_kitchen.png")]),
    dict(ep=4, src="第3章.md", title="第3章", sub="四枚の写真", bgm="v3",
         thumb=("img13_fusuma.png", "写真は、四枚になった。"),
         blue=("街路樹には電球が巻かれ", "換気扇の音が、遠くで回っていた"),
         cues=[("前回と同じ位置だった。", "img10_brown_env.png"),
               ("いつもの食卓があった。", "img12_kitchen.png")]),
    dict(ep=5, src="第4章.md", title="第4章", sub="頷きの意味", bgm="v3",
         thumb=("img16_hotel_curtain.png", "処女だと、思っていた。"),
         blue=("画面が、白く光った。", "蝉の声が、急に大きくなった"),
         cues=[("会社近くの定食屋で、二人で飯を食った。", "img15_teishoku.png"),
               ("ピンクの看板の灯りが、冷えたアスファルトに落ちていた。", "img16_hotel_curtain.png")]),
    dict(ep=6, src="第5章.md", title="第5章", sub="三月の日付", bgm="v3",
         thumb=("img11_photos.png", "一度じゃ、なかった。"),
         blue=("彼女は、あの部屋の空気を、身体で覚えていた。", "水を沸かす音が、階下から上がってきた"),
         cues=[("四通目だった。", "img10_brown_env.png"),
               ("秋刀魚の塩焼きと、茄子の煮浸しと、わかめの味噌汁だった。", "img12_kitchen.png")]),
    dict(ep=7, src="第6章.md", title="第6章", sub="俺たちの部屋", bgm="v2",
         thumb=("img17_saxblue_room.png", "ここは、俺たちの部屋だった。"), blue=None,
         cues=[("ここは、俺たちの部屋だった。", "img17_saxblue_room.png"),
               ("露天風呂の縁から", "img18_sea_lights.png"),
               ("深夜二時、俺は台所に降りた。", "img21_sink_ashes.png")]),
    dict(ep=8, src="第7章.md", title="第7章", sub="封筒の来ない月", bgm="v3",
         thumb=("img19_hanabi_smoke.png", "封筒が、来ない。"),
         blue=("その環を光らせて", "冷蔵庫の稼働音が、低く戻ってきた"),
         cues=[("花火は、約一万発だった。", "img19_hanabi_smoke.png"),
               ("百合子はパートに出はじめた。", "img20_register.png")]),
    dict(ep=9, src="第8章.md", title="第8章", sub="終わりだ", bgm="silent",
         thumb=("img21_sink_ashes.png", "終わりだ。"), blue=None,
         cues=[("六通目。", "img10_brown_env.png"),
               ("灰が、ステンレスの流しの底に積もった。", "img21_sink_ashes.png"),
               ("俺は和室に戻った。", "img22_washitsu.png")]),
    dict(ep=10, src="エピローグ.md", title="エピローグ", sub="人形は待っている", bgm="theme",
         thumb=("img01_doll.png", "人形は、待っている。"), blue=None,
         cues=[("本棚の隅に、フランス人形が座っていた。", "img01_doll.png")]),
]

def split_screens(text):
    """段落テキスト→スクリーン用チャンク列"""
    chunks = []
    for sent in re.split(r"(?<=[。！？])", text):
        s = sent.strip()
        if not s: continue
        while len(s) > CHARS_PER_LINE * MAX_LINES:
            chunks.append(s[:CHARS_PER_LINE * 3]); s = s[CHARS_PER_LINE * 3:]
        chunks.append(s)
    return [c for c in chunks if c]

def wrap(chunk):
    lines, cur = [], ""
    for ch in chunk:
        cur += ch
        if len(cur) >= CHARS_PER_LINE:
            lines.append(cur); cur = ""
    if cur: lines.append(cur)
    return lines

def parse_chapter(path):
    raw = open(path, encoding="utf-8").read()
    lines = [l.strip() for l in raw.split("\n") if l.strip() and not l.startswith("##")]
    return lines

def render_screen_img(chunk, color):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    lines = wrap(chunk)
    lh = 92
    total = lh * len(lines)
    y = (H - total) // 2 - 60
    for ln in lines:
        w = d.textlength(ln, font=F_BODY)
        d.text(((W - w) // 2, y), ln, font=F_BODY, fill=color)
        y += lh
    return im

def render_title_card(ep, title, sub, brand=True):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    if brand:
        w = d.textlength("GoldenCross", font=F_TITLE_S)
        d.text(((W - w) // 2, 620), "GoldenCross", font=F_TITLE_S, fill=GOLD)
    w = d.textlength(title, font=F_TITLE_L)
    d.text(((W - w) // 2, 830), title, font=F_TITLE_L, fill=WHITE)
    w = d.textlength(sub, font=F_BODY)
    d.text(((W - w) // 2, 1000), sub, font=F_BODY, fill=(170, 170, 170))
    return im

def strip_to_file(screens_colors, path):
    """スクリーン列を縦長ストリップPNG化"""
    n = len(screens_colors)
    strip = Image.new("RGB", (W, H * n), BG)
    for i, (chunk, color) in enumerate(screens_colors):
        im = render_screen_img(chunk, color)
        strip.paste(im, (0, H * i))
    strip.save(path)

def run_ff(args):
    cmd = [FFMPEG, "-y", "-loglevel", "error"] + args
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg fail:\n" + r.stderr[-1500:])

def enc_scroll(strip_path, chars, out):
    strip = Image.open(strip_path)
    dur = max(3.0, chars / CPS)
    rate = (strip.height - H) / dur if strip.height > H else 0
    vf = f"crop={W}:{H}:0:'min(ih-{H},max(0,trunc(t*{rate:.2f})))',format=yuv420p"
    run_ff(["-loop", "1", "-framerate", str(FPS), "-i", strip_path,
            "-vf", vf, "-t", f"{dur:.2f}", "-r", str(FPS),
            "-c:v", "libx264", "-preset", "fast", "-crf", "19", out])

def enc_image(img_path, out, dur=IMG_DUR, fade=True):
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p"
    if fade:
        vf += f",fade=t=in:st=0:d=0.5,fade=t=out:st={dur-0.5:.2f}:d=0.5"
    run_ff(["-loop", "1", "-framerate", str(FPS), "-i", img_path,
            "-vf", vf, "-t", f"{dur:.2f}", "-r", str(FPS),
            "-c:v", "libx264", "-preset", "fast", "-crf", "19", out])

def enc_black(out, dur=GAP_DUR):
    run_ff(["-f", "lavfi", "-i", f"color=c=0x0A0A0C:s={W}x{H}:d={dur}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-r", str(FPS), out])

def build_audio(bgm, total, out):
    src = {"theme": os.path.join(ASSETS, "goldencross_theme_song.mp3"),
           "v1": os.path.join(ASSETS, "bgm_v1.wav"),
           "v2": os.path.join(ASSETS, "bgm_v2.wav"),
           "v3": os.path.join(ASSETS, "bgm_v3.wav")}[bgm]
    fade_st = max(0, total - 3)
    run_ff(["-stream_loop", "-1", "-i", src, "-t", f"{total:.2f}",
            "-af", f"volume=0.55,afade=t=out:st={fade_st:.2f}:d=3",
            "-c:a", "aac", "-b:a", "160k", out])

def build_episode(cfg):
    ep = cfg["ep"]
    work = os.path.join(TMP_DIR, f"ep{ep:02d}")
    os.makedirs(work, exist_ok=True)
    paras = parse_chapter(os.path.join(SRC_DIR, cfg["src"]))
    # スクリーン列（色付き）
    screens = []
    blue = cfg.get('blue') or (None, None)
    bstart, bend = blue
    in_blue = False
    for para in paras:
        if bstart and bstart in para: in_blue = True
        color = BLUE if in_blue else WHITE
        for chunk in split_screens(para):
            screens.append((chunk, color))
        if bend and bend in para: in_blue = False
    # キュー配置：アンカー含むスクリーンの直後に画像カード
    segs = []   # (kind, payload)
    used_anchor = set()
    buf = []
    def flush():
        nonlocal buf
        if buf:
            sp = os.path.join(work, f"strip_{len(segs):03d}.png")
            strip_to_file(buf, sp)
            chars = sum(len(c) for c, _ in buf)
            segs.append(("scroll", sp, chars)); buf = []
    for chunk, color in screens:
        buf.append((chunk, color))
        if len(buf) >= 18:
            flush()
            segs.append(("gap",))
        for anchor, img in cfg["cues"]:
            if anchor in chunk and anchor not in used_anchor:
                flush(); used_anchor.add(anchor)
                segs.append(("image", os.path.join(IMG_DIR, img)))
    flush()
    # タイトルカード／エンドカード
    tp = os.path.join(work, "title.png")
    render_title_card(ep, cfg["title"], cfg["sub"]).save(tp)
    ed = Image.new("RGB", (W, H), BG)
    dd = ImageDraw.Draw(ed)
    txt = cfg["title"] + "　完"
    w = dd.textlength(txt, font=F_TITLE_L)
    dd.text(((W - w) // 2, 900), txt, font=F_TITLE_L, fill=WHITE)
    edp = os.path.join(work, "end.png"); ed.save(edp)
    # セグメントエンコード
    seg_files = []
    tp_v = os.path.join(work, "seg_title.mp4")
    if not os.path.exists(tp_v):
        enc_image(tp, tp_v, dur=4.0, fade=False)
    seg_files.append(tp_v)
    idx = 0
    for s in segs:
        idx += 1
        out = os.path.join(work, f"seg_{idx:03d}.mp4")
        if os.path.exists(out) and os.path.getsize(out) > 0:
            seg_files.append(out); continue
        if s[0] == "scroll":
            enc_scroll(s[1], s[2], out)
        elif s[0] == "image":
            enc_image(s[1], out)
        else:
            enc_black(out)
        seg_files.append(out)
    ev = os.path.join(work, "seg_end.mp4")
    enc_image(edp, ev, dur=3.0, fade=False); seg_files.append(ev)
    # 連結
    lst = os.path.join(work, "list.txt")
    with open(lst, "w", encoding="utf-8") as fh:
        for sf in seg_files:
            fh.write("file '" + sf.replace("\\", "/") + "'\n")
    vcat = os.path.join(work, "video_cat.mp4")
    run_ff(["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vcat])
    # 音声
    total = 0
    for sf in seg_files:
        r = subprocess.run([FFMPEG, "-i", sf, "-f", "null", "-"], capture_output=True, text=True)
        m = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", r.stderr)
        if m:
            total += int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    bgm_kind = cfg["bgm"]
    out_name = f"GC_ep{ep:02d}_{cfg['title']}.mp4"
    out_path = os.path.join(OUT_DIR, out_name)
    if bgm_kind == "silent":
        run_ff(["-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo", "-i", vcat,
                "-map", "1:v", "-map", "0:a", "-t", f"{total:.2f}",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", out_path])
    else:
        ap = os.path.join(work, "audio.m4a")
        build_audio(bgm_kind, total, ap)
        run_ff(["-i", vcat, "-i", ap, "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "copy", "-shortest", out_path])
    # サムネ
    tv, tsub = cfg["thumb"]
    base = Image.open(os.path.join(IMG_DIR, tv)).convert("RGB")
    base = base.resize((1280, int(base.height * 1280 / base.width)), Image.LANCZOS)
    th = Image.new("RGB", (1280, 720))
    yy = max(0, (base.height - 720) // 2)
    th.paste(base.crop((0, yy, 1280, yy + 720)), (0, 0))
    ov = Image.new("RGB", (1280, 720), (0, 0, 0))
    th = Image.blend(th, ov, 0.45)
    d = ImageDraw.Draw(th)
    fw = ImageFont.truetype(FONT_TITLE, 44)
    d.text((60, 70), "GoldenCross", font=ImageFont.truetype(FONT_TITLE, 36), fill=GOLD)
    yy2 = 140
    for ln in tsub.split("\n"):
        d.text((60, yy2), ln, font=fw, fill=WHITE); yy2 += 66
    d.text((60, 640), f"#{ep} {cfg['title']}", font=ImageFont.truetype(FONT_BODY, 28), fill=(180, 180, 180))
    th.save(os.path.join(OUT_DIR, f"GC_ep{ep:02d}_thumb.png"), quality=92)
    print(f"[ep{ep:02d}] done: {out_name}  ({total/60:.1f}分, segs={len(seg_files)})")
    return out_name, total

def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else None
    results = []
    for cfg in EPISODES:
        if targets and str(cfg["ep"]) not in targets: continue
        name, total = build_episode(cfg)
        results.append((name, total))
    print("\n=== ALL DONE ===")
    for n, t in results: print(f"{n}  {t/60:.1f}min")

if __name__ == "__main__":
    main()
