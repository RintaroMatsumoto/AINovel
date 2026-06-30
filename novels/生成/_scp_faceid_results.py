"""
SSH経由でM1 Dockerから画像をglobマッチでコピー（日本語ファイル名問題回避）
"""
import subprocess, os

OUT = r'C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘百合子\02_18歳_回想_新入社員'
os.makedirs(OUT, exist_ok=True)

seeds = {
    '9964889205': 'uniform_bob_front',
    '4953062774': 'uniform_tied_threeq',
    '5837946919': 'uniform_bob_threeq',
    '5195553803': 'cardigan_bob_front',
    '8386608370': 'cardigan_tied_sit',
    '3995583318': 'knitsweater_bob_profile',
    '7434834450': 'knitsweater_tied_front',
    '3348577865': 'turtleneck_bob_threeq',
    '3999481818': 'turtleneck_tied_desk',
    '4534331814': 'vest_bob_read',
    '6007397330': 'vest_tied_front',
    '7034785252': 'cardigan_bob_walk',
}

SSH = ['ssh', '-o', 'StrictHostKeyChecking=no', 'admin@100.112.59.35']

for seed, variant in seeds.items():
    en_name = f'yuriko_18_yayoi_mix_s{seed}_{variant}_00001_.png'
    local_path = os.path.join(OUT, en_name)
    
    if os.path.exists(local_path) and os.path.getsize(local_path) > 500000:
        print(f'SKIP {en_name}')
        continue
    
    # Use shell glob on remote to match the Japanese filename
    cmd = SSH + [f'docker exec comfyui sh -c "cat /opt/ComfyUI/output/百合子*yayoi_mix*{seed}_{variant}*"']
    with open(local_path, 'wb') as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE)
    
    if r.returncode == 0 and os.path.getsize(local_path) > 500000:
        sz = os.path.getsize(local_path) // 1024
        print(f'OK {en_name} ({sz}kb)')
    else:
        print(f'FAIL {en_name} (size={os.path.getsize(local_path)}b rc={r.returncode})')
        if os.path.exists(local_path):
            os.remove(local_path)

print('DONE')
