from pathlib import Path

base = Path(r'novels\ブレイクアウト\本文')
files = sorted(base.glob('*.md'))

targets = [1800, 1800, 2000, 1800, 1800, 1800, 1800, 1800, 2000, 2000, 2000, 1800, 1800, 1800, 2000]

print('Chapter | Current | 90% Target | Target | Gap')
print('-' * 55)
total_needed = 0
for i, f in enumerate(files):
    text = f.read_text(encoding='utf-8')
    target = targets[i]
    min_req = int(target * 0.9)
    gap = min_req - len(text)
    total_needed += max(0, gap)
    status = 'OK' if gap <= 0 else f'NEED {gap}'
    print(f'Ch{i+1:02d}     | {len(text):7d} | {min_req:10d} | {target:6d} | {status}')

print(f'\nTotal expansion needed: {total_needed} chars')
