"""DayTrade 各巻をPDF出力"""
from pathlib import Path
from fpdf import FPDF
import re

FONT_PATH = r"C:\Windows\Fonts\NotoSerifJP-VF.ttf"
OUTPUT_DIR = Path(r"C:\Users\GoldRush\Documents\MyProject\AINovel\pdf")
NOVELS_DIR = Path(r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels")

VOLUMES = {
    "GoldenCross": ("novels/GoldenCross/本文", "ゴールデンクロス"),
    "DeadCross": ("novels/デッドクロス/本文", "デッドクロス"),
    "Breakout": ("novels/ブレイクアウト/本文", "ブレイクアウト"),
}

class NovelPDF(FPDF):
    def __init__(self, title):
        super().__init__('P', 'mm', 'A5')
        self.title = title
        self.add_font("NotoSerif", "", FONT_PATH)
        self.add_font("NotoSerif", "B", FONT_PATH)
        self.set_auto_page_break(True, 20)
        
    def header(self):
        if self.page_no() > 1:
            self.set_font("NotoSerif", "", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 5, self.title, align='C')
            self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("NotoSerif", "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, str(self.page_no()), align='C')

    def write_chapter_title(self, text):
        """章タイトルを書く"""
        self.ln(6)
        self.set_font("NotoSerif", "B", 13)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 8, text)
        self.ln(4)

    def write_body(self, text):
        """本文を段落ごとに書く"""
        self.set_font("NotoSerif", "", 10)
        self.set_text_color(30, 30, 30)
        paragraphs = text.strip().split('\n')
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            if p.startswith('## '):
                self.write_chapter_title(p[3:])
                continue
            # 会話行のインデント調整
            if p.startswith('「') and p.endswith('」'):
                self.set_x(self.l_margin + 8)
                self.multi_cell(self.w - self.l_margin - self.r_margin - 8, 6.5, p)
                self.set_x(self.l_margin)
            else:
                self.multi_cell(0, 6.5, p)
            self.ln(0.5)

def make_pdf(volume_key, source_rel, title):
    source_dir = Path(source_rel)
    if not source_dir.is_absolute():
        source_dir = Path.cwd() / source_rel
    
    files = sorted(
        [f for f in source_dir.glob("*.md")],
        key=lambda x: (
            0 if "モノローグ" in x.name else
            int(re.search(r'第(\d+)章', x.name).group(1)) if re.search(r'第(\d+)章', x.name) else 99
        )
    )
    
    if not files:
        print(f"  [SKIP] {volume_key}: no files found in {source_dir}")
        return

    pdf = NovelPDF(title)
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
        text = f.read_text(encoding='utf-8')
        pdf.write_body(text)

    output = OUTPUT_DIR / f"DayTrade_{volume_key}.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output))
    
    # ファイルサイズ
    size_kb = output.stat().st_size // 1024
    print(f"  [OK] {volume_key}: {len(files)}ch -> {output.name} ({size_kb}KB)")

# メイン
print("DayTrade PDF生成")
print(f"フォント: {FONT_PATH}")
print(f"出力先: {OUTPUT_DIR}")
print()

for key, (src, title) in VOLUMES.items():
    make_pdf(key, src, title)

print()
print("完了")
