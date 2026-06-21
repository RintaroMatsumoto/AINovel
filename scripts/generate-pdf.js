const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const VOLUMES = [
  { key: 'FIRE', dir: 'FIRE', title: 'FIRE', subtitle: 'ゴールデンクロス', cover: 'goldencross_vol1_fire_seed3001_00001_.png' },
  { key: 'DeadCross', dir: 'デッドクロス', title: 'DeadCross', subtitle: 'デッドクロス', cover: 'goldencross_vol2_deadcross_seed3001_00001_.png' },
  { key: 'Breakout', dir: 'ブレイクアウト', title: 'Breakout', subtitle: 'ブレイクアウト', cover: 'goldencross_vol3_breakout_seed3001_00001_.png' },
  { key: 'LossCut', dir: 'ロスカット', title: 'LossCut', subtitle: 'ロスカット', cover: 'goldencross_vol4_losscut_seed3001_00002_.png' },
];

const ROOT = path.resolve(__dirname, '..');
const COVERS_DIR = path.join(ROOT, 'covers', 'ゴールデンクロス');
const NOVELS_DIR = path.join(ROOT, 'novels');
const PDF_DIR = path.join(ROOT, 'pdf');
const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';

function readChapters(volDir) {
  const dir = path.join(NOVELS_DIR, volDir, '本文');
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.md') && !f.startsWith('.'));
  files.sort((a, b) => {
    const na = parseInt(a.match(/(\d+)/)?.[1] || '0', 10);
    const nb = parseInt(b.match(/(\d+)/)?.[1] || '0', 10);
    return na - nb;
  });
  return files.map(f => {
    const content = fs.readFileSync(path.join(dir, f), 'utf-8');
    const titleMatch = content.match(/^# (.+)$/m);
    return { file: f, title: titleMatch?.[1] || f.replace('.md', ''), content };
  });
}

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function mdToHtml(md) {
  const lines = md.split('\n');
  let html = '';
  for (const line of lines) {
    if (line.startsWith('# ')) {
      html += `<h1>${escapeHtml(line.slice(2))}</h1>\n`;
    } else {
      html += `<p>${escapeHtml(line)}</p>\n`;
    }
  }
  return html;
}

function generateHtml(vol) {
  const chapters = readChapters(vol.dir);
  const coverPath = path.join(COVERS_DIR, vol.cover);
  const coverUrl = `file:///${coverPath.replace(/\\/g, '/')}`;

  const chapterTitles = chapters.map((c, i) => `<li>第${i + 1}章 ${escapeHtml(c.title)}</li>`).join('\n');

  let body = '';

  // Cover page
  body += `<div class="page cover-page">
    <img src="${coverUrl}" class="cover-image" />
  </div>\n`;

  // Title page
  body += `<div class="page title-page">
    <div class="title-block">
      <div class="series-title">Golden Cross</div>
      <div class="vol-title">${escapeHtml(vol.title)}</div>
      <div class="vol-subtitle">${escapeHtml(vol.subtitle)}</div>
      <div class="author">Doumin（ドウミン）</div>
    </div>
  </div>\n`;

  // TOC
  body += `<div class="page toc-page">
    <h2>目次</h2>
    <ul class="toc">${chapterTitles}</ul>
  </div>\n`;

  // Chapters
  for (const ch of chapters) {
    body += `<div class="page chapter-page">${mdToHtml(ch.content)}</div>\n`;
  }

  const title = `${vol.title} - Golden Cross`;
  const html = `<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>${escapeHtml(title)}</title>
<style>
  @page {
    size: A4;
    margin: 20mm 15mm;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Yu Gothic', 'YuGothic', sans-serif;
    font-size: 11pt;
    line-height: 2;
    color: #1a1a1a;
  }
  .page { page-break-after: always; }
  .cover-page {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
  }
  .cover-image {
    width: 100%;
    height: 100vh;
    object-fit: contain;
  }
  .title-page {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    text-align: center;
  }
  .title-block { max-width: 80%; }
  .series-title { font-size: 16pt; letter-spacing: 0.3em; margin-bottom: 30px; color: #666; }
  .vol-title { font-size: 32pt; font-weight: bold; letter-spacing: 0.2em; margin-bottom: 10px; }
  .vol-subtitle { font-size: 16pt; color: #888; margin-bottom: 50px; }
  .author { font-size: 13pt; color: #555; margin-top: 60px; }
  .toc-page { padding-top: 40mm; }
  .toc-page h2 { font-size: 18pt; text-align: center; margin-bottom: 30px; letter-spacing: 0.3em; }
  .toc { list-style: none; font-size: 11pt; line-height: 2.5; padding: 0 20mm; }
  .chapter-page h1 {
    font-size: 18pt;
    text-align: center;
    margin-bottom: 2em;
    letter-spacing: 0.2em;
  }
  .chapter-page p {
    text-indent: 0;
    margin: 0;
    line-height: 2;
    min-height: 2em;
  }
</style>
</head>
<body>
${body}
</body>
</html>`;

  return html;
}

function edgePrintToPdf(htmlPath, pdfPath) {
  const absHtml = path.resolve(htmlPath);
  const absPdf = path.resolve(pdfPath);
  const url = `file:///${absHtml.replace(/\\/g, '/')}`;
  const cmd = `& "${EDGE}" --headless --print-to-pdf="${absPdf}" --print-to-pdf-no-header --no-margins "${url}"`;
  console.log(`  Converting to PDF...`);
  execSync(cmd, { timeout: 30000, shell: 'powershell' });
}

// Main
for (const vol of VOLUMES) {
  console.log(`\n=== ${vol.key} ===`);
  const html = generateHtml(vol);

  const htmlFile = path.join(PDF_DIR, `${vol.key}.html`);
  const pdfFile = path.join(PDF_DIR, `${vol.key}.pdf`);
  fs.writeFileSync(htmlFile, html, 'utf-8');
  console.log(`  HTML written: ${htmlFile}`);

  edgePrintToPdf(htmlFile, pdfFile);
  console.log(`  PDF written: ${pdfFile} (${(fs.statSync(pdfFile).size / 1024 / 1024).toFixed(1)} MB)`);

  fs.unlinkSync(htmlFile); // cleanup
}

console.log('\nDone!');
