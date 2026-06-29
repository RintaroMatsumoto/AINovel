"""
DayTrade 全キャラ画像 M1 一括生成 (v2)
=====================================
Base: yayoi_mix + JapaneseDollLikeness + DetailTweaker
512x768, 各バリアント×4 seeds, サブフォルダ管理, 非メインは劣化プロンプト

Usage:
  py novels/生成/gen_all_chars_m1.py
"""

import requests, json, time, urllib.request, os, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE = "http://100.112.59.35:18188"
CHECKPOINT = "yayoi_mix.safetensors"
LORA1_NAME = "JapaneseDollLikeness_v15.safetensors"
LORA1_STRENGTH = 0.5
LORA2_NAME = "DetailTweaker.safetensors"
LORA2_STRENGTH = 0.2
ROOT_DIR = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像"

WIDTH = 512
HEIGHT = 768
STEPS = 28
CFG = 7.0
SAMPLER = "dpmpp_2m"
SCHEDULER = "karras"
SEED_OFFSETS = [0, 1, 2, 3]

NEG_DEFAULT = (
    "EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
    "cartoon, anime, illustration, painting, 3d render, cgi, "
    "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
    "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
    "watermark, signature, text, logo, existing celebrity, real person, copyrighted character"
)

# CHARACTERS: (character_name, [(seed, variant, subfolder, prompt), ...])
CHARACTERS = [

    # ═══ メイン4：誠・百合子・栞・翼 = 通常品質 ═══

    ("橘誠", [
        (3001, "suit", "01_40歳_現在_スーツ勤務",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40 year old japanese man, short two-block haircut, salt and pepper hair, natural finish with light wax, "
         "intelligent serious face, silver glasses, medium build, navy solid suit, white dress shirt, "
         "deep red stripe tie, black oxford shoes, modern japanese salaryman style, corporate office, calm expression, t_makoto_m"),
        (3002, "home_trade", "01_40歳_現在_スーツ勤務",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40 year old japanese man, short salt and pepper two-block hair, silver glasses, white shirt no tie, "
         "focused on monitors, stock charts, home office late night, content expression, slight tiredness in eyes, t_makoto_m"),
        (3003, "salaryman_2008", "02_24歳_回想_教育係時代",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "mid 20s japanese man, short black hair, young serious face, silver glasses, white shirt, "
         "slightly loose tailored navy suit, dark red tie, late 2000s japanese salaryman style, office worker, "
         "teaching new employee, patient expression, bright office, youthful earnestness, t_makoto_m"),
        (3004, "funeral", "02_24歳_回想_教育係時代",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "late 20s japanese man, short black hair, silver glasses, black funeral suit, holding small wooden box, "
         "quiet solemn expression, japanese funeral hall, t_makoto_m"),
        (3005, "broken", "03_40歳_崩壊後",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40 year old japanese man, messy short salt and pepper hair, stubble, silver glasses, wrinkled white shirt, "
         "hollow exhausted eyes, dark circles, broken expression, holding glass of alcohol, dim messy room, t_makoto_m"),
    ]),

    ("橘百合子", [
        (3011, "modern_housewife", "01_34歳_現在_主婦",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "34 year old japanese woman, mid-length layered blackish brown hair, see-through bangs, gentle oval face, "
         "soft big eyes, slender, fair skin, natural makeup, modern casual elegant style, "
         "loose black one-piece dress, white sneakers, warm living room, soft afternoon light, "
         "gentle smile with hidden sadness, t_yuriko_f"),
        (3012, "office_2008", "02_18歳_回想_新入社員",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "18 year old japanese young woman, long straight black hair, simple natural hairstyle, earnest innocent face, "
         "honest modest eyes, no makeup or very minimal natural makeup, slender, fair skin, "
         "plain modest blouse, standard office jacket, knee length skirt, low heel pumps, "
         "diligent hardworking new employee, no dating experience, serious studious vibe, t_yuriko_f"),
        (3013, "after_rape", "02_18歳_回想_新入社員",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "18 year old japanese young woman, disheveled long black hair, shocked traumatized expression, no makeup, "
         "broken, disheveled office clothes, sitting on unfamiliar room floor, morning light, t_yuriko_f"),
        (3014, "confession", "03_34歳_告白直前",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "34 year old japanese woman, messy mid-length hair, swollen red eyes, fragile terrified face, "
         "determination mixed with fear, worn cardigan, corner of dark room, t_yuriko_f"),
    ]),

    ("橘栞", [
        (3021, "school", "01_14歳_中学生_日常",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "14 year old japanese girl, long straight black hair, cute innocent face, bright intelligent eyes, slender, "
         "private school uniform, blazer with pleated skirt, low ribbon position, "
         "oversized gray cardigan over uniform, knee-high black socks, loafers, "
         "school hallway, bright daylight, mid 2010s japanese middle school girl, t_shiori_f"),
        (3022, "facility", "02_14歳_施設_憔悴",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "14 year old japanese girl, long black hair slightly messy, thin face, scared tired eyes, fragile, "
         "plain cheap clothes, institutional room, cold fluorescent light, lonely, t_shiori_f"),
        (3023, "escape", "03_14歳_脱走_トー横",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "14 year old japanese girl, long messy black hair, empty closed-off eyes, thin fragile build, "
         "dirty plain clothes, street corner at night, kabukicho alley, survival mode, t_shiori_f"),
        (3024, "jirai_stand", "04_16-17歳_地雷系_立ちんぼ",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "16 year old japanese girl, dark hair face-framing curls (yoshinmori style), thick bangs, twin tail half-up, "
         "heavy pink eye shadow, under-eye blush (yamikawaii), big cautious eyes, "
         "white fake fur coat, frill blouse, pleated mini skirt, patterned tights, platform shoes, "
         "MCM backpack, shinjuku street night, neon light, jirai-kei fashion, defensive forced toughness, t_shiori_f"),
        (3025, "trade", "05_17歳_トレード",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "17 year old japanese young woman, long black hair tied back, traces of yamikawaii makeup, "
         "sharp focused eyes, thin concentrated face, hoodie, laptop in front, "
         "monitor glow on face, dark room, intense trading atmosphere, t_shiori_f"),
        (3026, "revenge", "06_18歳_復讐",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "18 year old japanese young woman, long black hair, cold sharp eyes, minimal makeup, thin determined face, "
         "black hoodie, dark jeans, sneakers, walking city street at night, cold anger expression, "
         "focused on purpose, t_shiori_f"),
    ]),

    ("橘翼", [
        (3031, "child", "01_11歳_小学生",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "11 year old japanese boy, short cropped black hair, small thin build, innocent smile, happy child, "
         "graphic t-shirt, slim dark jeans, sneakers, warm home, playing, mid 2010s japanese schoolboy style, t_tsubasa_m"),
        (3032, "buzzcut", "02_14歳_少年院_丸刈り",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "14 year old japanese boy, shaved head buzz cut, still childish face but hardened eyes, thin, "
         "azuki-red prison tracksuit, defensive closed-off look, juvenile detention center, t_tsubasa_m"),
        (3033, "growing", "03_16歳_少年院_伸びかけ",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "16 year old japanese boy, short growing-out hair from buzz cut, not yet styled, "
         "still childish face but hardened eyes, muscular thin build, azuki-red prison tracksuit, "
         "juvenile detention center, t_tsubasa_m"),
        (3034, "host_debut", "04_16-17歳_ホスト",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "16 year old japanese boy, black hair center part, clean straight style, groomed eyebrows, "
         "handsome young face, still some boyishness, athletic build, "
         "korean-style host suit, beige suit set, simple silver necklace, "
         "nervous confident mixed expression, mirror reflection, dressing room, t_tsubasa_m"),
        (3035, "fighter", "05_17-20歳_格闘家",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "20 year old japanese man, short messy black hair slicked back, sharp intense eyes, arrogant smirk, "
         "muscular athletic build, compression tank top, fight shorts, black and gold, "
         "underground ring, spotlight, tattoos visible, t_tsubasa_m"),
        (3036, "hospital", "06_20歳_タイトルマッチ後",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "20 year old japanese man, messy short black hair, hollow empty eyes, thin pale face, "
         "hospital gown, sitting in wheelchair, despair expression, hospital room, dim light, t_tsubasa_m"),
        (3037, "epilogue", "07_30歳_エピローグ",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "30 year old japanese man, short black hair, calm gentle face, peaceful eyes, muscular upper body, "
         "simple modern shirt and slacks, sitting in wheelchair, surrounded by children, "
         "shy happy smile, facility garden sunny, near future japan, t_tsubasa_m"),
    ]),

    # ═══ 非メイン：劣化プロンプト（シワ・ハゲ・デブ・不細工）═══

    ("金子雅也", [
        (3041, "salaryman_2008", "01_24歳_過去_同期社員",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "mid 20s japanese man, short black hair, sallow thin face, cold dead eyes, "
         "sleazy smirk, faint premature wrinkles around eyes, slightly receding temples, "
         "slightly loose tailored navy suit, white shirt, stripe tie, late 2000s salaryman, "
         "unnaturally charming smile that doesn't reach eyes, kaneko_m_m"),
        (3042, "home_rape_2008", "01_24歳_過去_同期社員",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "mid 20s japanese man, short black hair, sallow thin predatory face, cold dead eyes, "
         "casual home clothes late 2000s style, slight smirk, predatory, "
         "bedroom, dim lamp light, tense atmosphere, kaneko_m_m"),
        (3043, "office_2024", "02_40歳_現在_会社",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40 year old japanese man, short thinning salt and pepper hair, sallow wrinkled skin, "
         "cold dead eyes behind friendly facade, fake smile of a career politician, "
         "prematurely aged, slim build, modern navy business suit, office hallway, "
         "too-friendly demeanor with empty eyes, kaneko_m_m"),
        (3044, "hotel", "03_40歳_現在_ホテル",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40 year old japanese man, short thinning salt and pepper hair, sallow wrinkled skin, "
         "cold dead eyes, casual jacket and shirt, smoking cigarette, sitting on hotel room chair, "
         "staring intently, thin predatory smile, dim room, tense atmosphere, kaneko_m_m"),
        (3045, "collection", "04_40歳_現在_コレクションルーム",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40 year old japanese man, short thinning salt and pepper hair, sallow skin, "
         "twisted satisfied smile, predatory dead eyes, casual home clothes, "
         "looking at collection wall, dim room, shelves of files, creepy atmosphere, kaneko_m_m"),
    ]),

    ("神崎大輔", [
        (3051, "kyabakura", "01_20代前半_歌舞伎町_半グレ",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "early 20s japanese man, short black hair, rough scarred skin, cold dead eyes, "
         "thin cruel mouth, not handsome, cheap expensive-looking dark suit, white shirt, "
         "fake luxury watch, silver ring, snake-like eyes, bar interior, dim red light, "
         "young yakuza enforcer, unpleasant vibe, jin_kz_m"),
        (3052, "murder", "02_20代半ば_栞殺害後",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "mid 20s japanese man, short black hair slightly disheveled, rough scarred skin, "
         "cold emotionless eyes, dark bloodstained suit, loosened white collar, "
         "silver ring with blood, leaning against alley wall, cigarette in mouth, "
         "night rain, no remorse, jin_kz_m"),
        (3053, "fighter", "03_20代後半_地下格闘技",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "late 20s japanese man, short black hair, rough scarred face, broken nose scars, "
         "cold predatory eyes, thin cruel smile, muscular fighter build, "
         "compression tank top, fight shorts, dragon tiger graphic, "
         "sweat and bruises, underground ring, spotlight, crowd roar, fighting pose, jin_kz_m"),
    ]),

    ("黒崎徹", [
        (3061, "supporter", "01_30代前半_現在_支援者",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "early 30s japanese man, short black hair, weathered scarred rough face, "
         "deep-set tired eyes, visible acne scars, medium build, simple shirt and jacket, "
         "quiet caring expression, slight awkward smile, standing by wheelchair, "
         "sunny facility, lived-in hard life look, kuro_t_m"),
        (3062, "buzzcut", "02_少年院_丸刈り",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "16 year old japanese boy, shaved head buzz cut, rough tough face, scarring, "
         "tough but kind eyes, still youthful face, azuki-red prison tracksuit, "
         "juvenile detention center, talking to younger boy, protective older brother vibe, kuro_t_m"),
        (3063, "growing", "03_少年院_伸びかけ",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "18 year old japanese young man, short growing-out hair from buzz cut, rough skin, "
         "tough but kind eyes, muscular build, azuki-red prison tracksuit, "
         "about to be released, kuro_t_m"),
        (3064, "host_after", "04_ホスト後_先輩",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "early 20s japanese man, short black hair, rough weathered face, scars, "
         "sharp but kind eyes, not handsome, simple suit, cigarette in mouth, "
         "tough caring aura, nightclub alley, neon lights, kuro_t_m"),
    ]),

    ("施設長", [
        (3081, "director", "01_50代_施設長",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "50 year old japanese man, gray short balding hair, receding hairline, round sweaty face, "
         "beady piggy eyes, double chin, small glasses, overweight pot belly, disgusting fat man, "
         "gentle facade, institutional clothes, cardigan and shirt, dark office, "
         "predatory hidden eyes behind kindly smile, creepy, childrens home director, shisetsucho_m"),
    ]),

    ("養父", [
        (3091, "abusive", "01_40代_養父_虐待者",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "mid 40s japanese man, balding, receding gray-black hair, alcoholic bloated red nose, "
         "ugly stubble, beer belly, ugly gross unattractive face, "
         "cheap t-shirt and track pants, suburban house living room, holding beer can, "
         "aggressive ugly expression, satoya_m"),
    ]),

    ("警察官", [
        (3101, "interrogation", "01_40代_取調べ",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "late 40s japanese man, short graying hair, sallow tired skin, heavy eyebags, "
         "weary paunchy middle-aged face, plain unattractive, "
         "dark navy stand-collar police uniform, cap, interrogation room, holding file, "
         "apathetic expression, seen-it-all attitude, police_officer_m"),
        (3102, "desk", "02_50歳_デスク業務",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "50 year old japanese man, short salt-and-pepper hair, sallow wrinkled skin, "
         "heavy eyebags, weary face, paunch, plain unattractive, "
         "dark blue police uniform, messy police station desk, filing paperwork, "
         "tired grim look, police_officer_m"),
    ]),

    ("弁護士", [
        (3111, "lawyer", "01_50代_弁護士",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "late 50s japanese man, thinning gray white hair, deeply wrinkled face, age spots, "
         "plain elderly face, metal frame glasses, formal navy suit, white dress shirt, "
         "bordeaux stripe tie, black leather shoes, classic watch, professional neutral expression, "
         "law office, holding document envelope, not handsome, lawyer_estate_m"),
    ]),

    ("百合子の母", [
        (3121, "mother", "01_60代_実母",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "60 year old japanese woman, gray streaked black perm hair, deeply wrinkled tired face, "
         "worn elderly country woman, plain unattractive, "
         "simple older clothes, cardigan, wool skirt, small kitchen, "
         "heavy burdens expression, yuriko_mother_f"),
    ]),

    ("誠の祖父", [
        (3131, "alive", "01_70代_存命",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "elderly japanese man in his 70s, short white hair, receding hairline, deeply wrinkled face, "
         "deep-set wise eyes, gentle warm smile, thin build, cardigan and shirt, holding old gold coin, "
         "traditional japanese room, warm nostalgic atmosphere, grandfather_m"),
        (3132, "funeral", "02_葬儀",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "elderly deceased japanese man in his late 70s, white hair, peaceful expression, "
         "black funeral kimono, lying in coffin, japanese funeral, white flowers, "
         "solemn quiet atmosphere, grandfather_m"),
    ]),

    ("義母", [
        (3141, "home", "01_40代_自宅_虐待黙認",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40s japanese woman, black hair streaked with gray, gaunt haggard face, thin-lipped, "
         "worn out tired expression, unattractive plain, "
         "plain housewife clothes, apron, suburban kitchen, avoiding eye contact, "
         "complicit silence, stepmother_f"),
        (3142, "police", "02_40代_警察_偽証",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40s japanese woman, gray streaked hair, gaunt haggard face, worn out, "
         "plain clothes, sitting in police station, looking down, "
         "guilty nervous expression, giving false testimony, small trembling voice posture, stepmother_f"),
    ]),

    ("トー横の年上の女", [
        (3071, "toyoko", "01_20代前半_トー横の先輩",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "early 20s japanese woman, dark hair face-framing curls, thick bangs, "
         "rough hard weathered face, dark circles under eyes, hard life look, not cute, "
         "yamikawaii makeup, pink eyeshadow, plump build, "
         "white fake fur coat, frill blouse, pleated mini skirt, patterned tights, platform shoes, "
         "MCM backpack, shinjuku alley night, cigarette, protective older sister aura, "
         "streets have not been kind, toyoko_girl_f"),
    ]),
]


def generate(character_name, subfolder, variant_name, seed, positive):
    char_map = {"橘誠": "makoto", "橘百合子": "yuriko", "橘栞": "shiori", "橘翼": "tsubasa",
                "金子雅也": "kaneko", "神崎大輔": "jin", "黒崎徹": "kurot",
                "トー横の年上の女": "toyoko", "施設長": "shisetsu", "養父": "satoya",
                "警察官": "police", "弁護士": "lawyer", "百合子の母": "yurimother",
                "誠の祖父": "grandpa", "義母": "stepmother"}
    safe_char = char_map.get(character_name, character_name[:4])
    prefix = f"{variant_name}_s{seed}"
    out_dir = os.path.join(ROOT_DIR, character_name, subfolder)
    os.makedirs(out_dir, exist_ok=True)
    print(f"[{character_name} / {subfolder}] {variant_name} seed={seed} submitting...")

    wf = {
        "1": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": CHECKPOINT}},
        "2": {"class_type": "LoraLoader",
              "inputs": {"model": ["1", 0], "clip": ["1", 1],
                         "lora_name": LORA1_NAME,
                         "strength_model": LORA1_STRENGTH,
                         "strength_clip": LORA1_STRENGTH}},
        "9": {"class_type": "LoraLoader",
              "inputs": {"model": ["2", 0], "clip": ["2", 1],
                         "lora_name": LORA2_NAME,
                         "strength_model": LORA2_STRENGTH,
                         "strength_clip": LORA2_STRENGTH}},
        "3": {"class_type": "CLIPTextEncode",
              "inputs": {"text": positive, "clip": ["9", 1]}},
        "4": {"class_type": "CLIPTextEncode",
              "inputs": {"text": NEG_DEFAULT, "clip": ["9", 1]}},
        "5": {"class_type": "EmptyLatentImage",
              "inputs": {"width": WIDTH, "height": HEIGHT, "batch_size": 1}},
        "6": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": STEPS, "cfg": CFG,
                         "sampler_name": SAMPLER, "scheduler": SCHEDULER,
                         "denoise": 1.0,
                         "model": ["9", 0], "positive": ["3", 0],
                         "negative": ["4", 0], "latent_image": ["5", 0]}},
        "7": {"class_type": "VAEDecode",
              "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "8": {"class_type": "SaveImage",
              "inputs": {"filename_prefix": prefix, "images": ["7", 0]}},
    }

    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt": wf}, timeout=30)
        r.raise_for_status()
        pid = r.json()["prompt_id"]
    except Exception as e:
        print(f"  SUBMIT ERROR: {e}")
        return None

    for j in range(120):
        time.sleep(2)
        try:
            h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
            if pid in h:
                st = h[pid]["status"]["status_str"]
                if st == "success":
                    outputs = h[pid]["outputs"]
                    saved = []
                    for nid, node in outputs.items():
                        for img in node.get("images", []):
                            url = f"{BASE}/view?filename={img['filename']}&subfolder={img['subfolder']}&type={img['type']}"
                            out_path = os.path.join(out_dir, img["filename"])
                            urllib.request.urlretrieve(url, out_path)
                            size_kb = os.path.getsize(out_path) // 1024
                            saved.append((img["filename"], size_kb))
                    print(f"  OK: {saved}")
                    return ("ok", saved)
                elif st == "error":
                    print(f"  JOB ERROR")
                    return ("error", None)
        except Exception as e:
            if j == 119:
                print(f"  TIMEOUT")
                return ("timeout", None)
    return ("timeout", None)


if __name__ == "__main__":
    print(f"Target: {BASE}")
    print(f"Model: {CHECKPOINT}")
    print(f"Output root: {ROOT_DIR}")
    print(f"Seed offsets: {SEED_OFFSETS}")

    total_variants = sum(len(vs) for _, vs in CHARACTERS)
    total_jobs = total_variants * len(SEED_OFFSETS)
    print(f"Characters: {len(CHARACTERS)}")
    print(f"Variants: {total_variants}")
    print(f"Jobs: {total_jobs}")
    print()

    all_results = []
    for character_name, variants in CHARACTERS:
        print(f"\n{'='*60}")
        print(f"CHARACTER: {character_name}")
        print(f"{'='*60}")
        for base_seed, variant_name, subfolder, positive in variants:
            for offset in SEED_OFFSETS:
                seed = base_seed + offset
                result = generate(character_name, subfolder, variant_name, seed, positive)
                all_results.append((character_name, variant_name, seed, result))
                time.sleep(0.5)
            print()

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    ok_count = 0
    for char, var, seed, result in all_results:
        if result and result[0] == "ok":
            ok_count += 1
            n = len(result[1])
            print(f"  {char}/{var} s{seed}: OK ({n} f)")
        elif result and result[0] == "error":
            print(f"  {char}/{var} s{seed}: ERROR")
        else:
            st = result[0] if result else "UNK"
            print(f"  {char}/{var} s{seed}: {st}")
    print(f"\nOK: {ok_count}/{total_jobs}")
    print(f"Root: {ROOT_DIR}")
