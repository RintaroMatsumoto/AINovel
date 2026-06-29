"""DayTrade: TXT（スライド用スマート改行）+ PDF 生成"""
from pathlib import Path
import re
from fpdf import FPDF

OUTPUT_DIR = Path(r"C:\Users\GoldRush\Documents\MyProject\AINovel\pdf")
NOVELS_DIR = Path(r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels")
FONT_PATH = r"C:\Windows\Fonts\NotoSerifJP-VF.ttf"

VOLUMES = [
    ("GoldenCross", NOVELS_DIR / "GoldenCross" / "本文", "GoldenCross", "誠編"),
    ("DeadCross",   NOVELS_DIR / "デッドクロス" / "本文", "DeadCross", "栞編"),
    ("Breakout",    NOVELS_DIR / "ブレイクアウト" / "本文", "Breakout", "翼編"),
]

SEP = '=' * 60
TXT_WIDTH  = 70   # テキスト用 1行の目安文字数
TXT_MIN    = 25   # テキスト用 最小ライン長（これ以下は前行に結合）
PDF_WIDTH  = 35   # A5 PDF 用（10pt だと約32字/行に収まる）
PDF_MIN    = 15


def sorted_md(dir_path):
    files = list(dir_path.glob("*.md"))
    def key(f):
        n = f.name
        if 'モノローグ' in n:
            return 0
        m = re.search(r'第(\d+)章', n)
        return int(m.group(1)) if m else 99
    return sorted(files, key=key)


# ── スマート改行 ────────────────────────────────────────

def _reassemble(parts, max_w, min_w, fallback):
    lines, buf = [], ''
    for p in parts:
        if not buf:
            buf = p
        elif len(buf) + len(p) <= max_w:
            buf += p
        else:
            if len(buf) >= min_w or not lines:
                lines.append(buf)
            else:
                lines[-1] += buf
            buf = p
    if buf:
        if len(buf) >= min_w or not lines:
            lines.append(buf)
        else:
            lines[-1] += buf
    out = []
    for ln in lines:
        if len(ln) <= max_w:
            out.append(ln)
        else:
            out.extend(fallback(ln, max_w, min_w))
    return out


def _hard_wrap(line, max_w):
    out = []
    while line:
        out.append(line[:max_w])
        line = line[max_w:]
    return out


def _split_parts(line, max_w, min_w):
    """助詞で分割 → それでも長ければハードラップ"""
    parts = re.split(r'(?<=[がをにのへでと])', line)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) <= 1:
        return _hard_wrap(line, max_w)
    return _reassemble(parts, max_w, min_w, lambda l, w, m: _hard_wrap(l, w))


def _split_comma(line, max_w, min_w):
    """読点で分割 → それでも長ければ助詞分割へ"""
    parts = re.split(r'(?<=、)', line)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) > 1:
        return _reassemble(parts, max_w, min_w, lambda l, w, m: _split_parts(l, w, m))
    return _split_parts(line, max_w, min_w)


def smart_break(text, max_w, min_w, tolerance=8):
    """段落テキスト → 切りの良い行リスト"""
    sents = re.split(r'(?<=[。！？])', text)
    sents = [s.strip() for s in sents if s.strip()]
    if not sents:
        return []

    lines, buf = [], ''
    for s in sents:
        if not buf:
            buf = s
        elif len(buf) + len(s) <= max_w + tolerance:
            buf += s
        else:
            if len(buf) >= min_w or not lines:
                lines.append(buf)
            else:
                lines[-1] += buf
            buf = s
    if buf:
        if len(buf) >= min_w or not lines:
            lines.append(buf)
        else:
            lines[-1] += buf

    out = []
    for ln in lines:
        if len(ln) <= max_w + tolerance:
            out.append(ln)
        else:
            out.extend(_split_comma(ln, max_w, min_w))
    return out


# ── TXT 生成 ──────────────────────────────────────────

def gen_txt(vol):
    vol_key, src_dir, en_name, suffix = vol
    files = sorted_md(src_dir)
    if not files:
        print(f"  [SKIP] {vol_key}: no files")
        return None

    lines = []

    def put(*args):
        for a in args:
            lines.append(a)

    def sep_block(title):
        s = max((len(SEP) - len(title)) // 2, 0)
        put(SEP, '', ' ' * s + title, '', SEP, '')

    # ── 表紙
    put(SEP, '')
    put('          DayTrade 三部作')
    put('')
    put(f'            {en_name}')
    put(f'            （{suffix}）')
    put('')
    put(SEP, '')

    # ── 各章
    for f in files:
        raw = f.read_text(encoding='utf-8')
        m = re.search(r'^## (.+)', raw, re.MULTILINE)
        if m:
            ch_title = m.group(1).strip()
            body = re.sub(r'^## .+', '', raw, flags=re.MULTILINE).strip()
        else:
            ch_title = 'モノローグ'
            body = raw.strip()

        sep_block(ch_title)

        for para in re.split(r'\n\n+', body):
            para = para.strip()
            if not para:
                continue
            flat = ''.join(l.strip() for l in para.split('\n') if l.strip())
            if not flat:
                continue
            segs = smart_break(flat, TXT_WIDTH, TXT_MIN)
            put('\n'.join(segs), '')

    text = '\n'.join(lines).rstrip('\n') + '\n'
    out = OUTPUT_DIR / f"DayTrade_{vol_key}.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding='utf-8')
    kb = len(text.encode('utf-8')) // 1024
    ch = len(files)
    print(f"  [TXT] DayTrade_{vol_key}.txt  ({ch}ch, {kb}KB)")
    return out


# ── PDF 生成 ──────────────────────────────────────────

class DayTradePDF(FPDF):
    def __init__(self, title):
        super().__init__('P', 'mm', 'A5')
        self.page_title = title
        self.add_font("NotoSerif", "", FONT_PATH)
        self.add_font("NotoSerif", "B", FONT_PATH)
        self.set_auto_page_break(True, 20)

    def header(self):
        if self.page_no() > 1:
            self.set_font("NotoSerif", "", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 5, self.page_title, align='C')
            self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("NotoSerif", "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, str(self.page_no()), align='C')

    def add_chapter(self, title):
        self.ln(6)
        self.set_font("NotoSerif", "B", 13)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 8, title)
        self.ln(4)

    def add_body(self, text):
        self.set_font("NotoSerif", "", 10)
        self.set_text_color(30, 30, 30)
        for p in text.strip().split('\n'):
            p = p.strip()
            if not p:
                continue
            if p.startswith('## '):
                self.add_chapter(p[3:])
                continue
            segs = smart_break(p, PDF_WIDTH, PDF_MIN)
            for seg in segs:
                if seg.startswith('「') and seg.endswith('」'):
                    self.set_x(self.l_margin + 8)
                    self.multi_cell(self.w - self.l_margin - self.r_margin - 8, 6.5, seg)
                    self.set_x(self.l_margin)
                else:
                    self.multi_cell(0, 6.5, seg)
                self.ln(0.3)
            self.ln(0.5)


def gen_pdf(vol):
    vol_key, src_dir, en_name, suffix = vol
    files = sorted_md(src_dir)
    if not files:
        print(f"  [SKIP] {vol_key}: no files")
        return

    title = f"{en_name}（{suffix}）"
    pdf = DayTradePDF(title)
    pdf.set_margin(18)

    # 表紙
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("NotoSerif", "B", 22)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 12, "DayTrade", align='C')
    pdf.ln(16)
    pdf.set_font("NotoSerif", "B", 18)
    pdf.cell(0, 10, title, align='C')
    pdf.ln(20)
    pdf.set_font("NotoSerif", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, f"全{len(files)}章", align='C')

    # 本文
    for f in files:
        pdf.add_page()
        pdf.add_body(f.read_text(encoding='utf-8'))

    out = OUTPUT_DIR / f"DayTrade_{vol_key}.pdf"
    pdf.output(str(out))
    kb = out.stat().st_size // 1024
    print(f"  [PDF] DayTrade_{vol_key}.pdf  ({kb}KB)")


# ── メイン ──────────────────────────────────────────

def main():
    print("DayTrade TXT + PDF 生成")
    print()

    for vol in VOLUMES:
        print(f"── {vol[0]} ──")
        gen_txt(vol)
        gen_pdf(vol)
        print()

    print("完了")

if __name__ == '__main__':
    main()
