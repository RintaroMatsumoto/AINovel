"""
キャラクター設定ファイルに画像生成情報を追記
Usage: py novels/生成/sync_char_image_info.py
"""

import os, re

CHAR_DIR = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラクター"

BASE_MODEL = "yayoi_mix.safetensors (SD1.5)"
LORA = "JapaneseDollLikeness_v15 (0.5) + DetailTweaker (0.2)"
RES = "512×768"
PARAMS = "Steps: 28 / CFG: 7.0 / Sampler: dpmpp_2m / Scheduler: karras"

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character")

# (character_name, display_label, [(base_seed, variant_label, subfolder, prompt), ...])
CHARACTERS = [
    ("橘誠", "橘誠", [
        (3001, "スーツ（会社）", "01_40歳_現在_スーツ勤務",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40 year old japanese man, short two-block haircut, salt and pepper hair, natural finish with light wax, "
         "intelligent serious face, silver glasses, medium build, navy solid suit, white dress shirt, "
         "deep red stripe tie, black oxford shoes, modern japanese salaryman style, corporate office, calm expression, t_makoto_m"),
        (3002, "自宅トレード", "01_40歳_現在_スーツ勤務",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40 year old japanese man, short salt and pepper two-block hair, silver glasses, white shirt no tie, "
         "focused on monitors, stock charts, home office late night, content expression, slight tiredness in eyes, t_makoto_m"),
        (3003, "教育係（24歳）", "02_24歳_回想_教育係時代",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "mid 20s japanese man, short black hair, young serious face, silver glasses, white shirt, "
         "slightly loose tailored navy suit, dark red tie, late 2000s japanese salaryman style, office worker, "
         "teaching new employee, patient expression, bright office, youthful earnestness, t_makoto_m"),
        (3004, "葬儀（29歳）", "02_24歳_回想_教育係時代",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "late 20s japanese man, short black hair, silver glasses, black funeral suit, holding small wooden box, "
         "quiet solemn expression, japanese funeral hall, t_makoto_m"),
        (3005, "崩壊後", "03_40歳_崩壊後",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40 year old japanese man, messy short salt and pepper hair, stubble, silver glasses, wrinkled white shirt, "
         "hollow exhausted eyes, dark circles, broken expression, holding glass of alcohol, dim messy room, t_makoto_m"),
    ]),
    ("橘百合子", "橘百合子", [
        (3011, "現在・主婦", "01_34歳_現在_主婦",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "34 year old japanese woman, mid-length layered blackish brown hair, see-through bangs, gentle oval face, "
         "soft big eyes, slender, fair skin, natural makeup, modern casual elegant style, "
         "loose black one-piece dress, white sneakers, warm living room, soft afternoon light, "
         "gentle smile with hidden sadness, t_yuriko_f"),
        (3012, "新入社員（18歳）", "02_18歳_回想_新入社員",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "18 year old japanese young woman, long straight black hair, simple natural hairstyle, earnest innocent face, "
         "honest modest eyes, no makeup or very minimal natural makeup, slender, fair skin, "
         "plain modest blouse, standard office jacket, knee length skirt, low heel pumps, "
         "diligent hardworking new employee, no dating experience, serious studious vibe, t_yuriko_f"),
        (3013, "レイプ翌朝", "02_18歳_回想_新入社員",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "18 year old japanese young woman, disheveled long black hair, shocked traumatized expression, no makeup, "
         "broken, disheveled office clothes, sitting on unfamiliar room floor, morning light, t_yuriko_f"),
        (3014, "告白直前・憔悴", "03_34歳_告白直前",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "34 year old japanese woman, messy mid-length hair, swollen red eyes, fragile terrified face, "
         "determination mixed with fear, worn cardigan, corner of dark room, t_yuriko_f"),
    ]),
    ("橘栞", "橘栞", [
        (3021, "中学生・日常", "01_14歳_中学生_日常",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "14 year old japanese girl, long straight black hair, cute innocent face, bright intelligent eyes, slender, "
         "private school uniform, blazer with pleated skirt, low ribbon position, "
         "oversized gray cardigan over uniform, knee-high black socks, loafers, "
         "school hallway, bright daylight, mid 2010s japanese middle school girl, t_shiori_f"),
        (3022, "施設・憔悴", "02_14歳_施設_憔悴",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "14 year old japanese girl, long black hair slightly messy, thin face, scared tired eyes, fragile, "
         "plain cheap clothes, institutional room, cold fluorescent light, lonely, t_shiori_f"),
        (3023, "脱走・トー横", "03_14歳_脱走_トー横",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "14 year old japanese girl, long messy black hair, empty closed-off eyes, thin fragile build, "
         "dirty plain clothes, street corner at night, kabukicho alley, survival mode, t_shiori_f"),
        (3024, "地雷系・立ちんぼ", "04_16-17歳_地雷系_立ちんぼ",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "16 year old japanese girl, dark hair face-framing curls (yoshinmori style), thick bangs, twin tail half-up, "
         "heavy pink eye shadow, under-eye blush (yamikawaii), big cautious eyes, "
         "white fake fur coat, frill blouse, pleated mini skirt, patterned tights, platform shoes, "
         "MCM backpack, shinjuku street night, neon light, jirai-kei fashion, defensive forced toughness, t_shiori_f"),
        (3025, "トレード", "05_17歳_トレード",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "17 year old japanese young woman, long black hair tied back, traces of yamikawaii makeup, "
         "sharp focused eyes, thin concentrated face, hoodie, laptop in front, "
         "monitor glow on face, dark room, intense trading atmosphere, t_shiori_f"),
        (3026, "復讐", "06_18歳_復讐",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "18 year old japanese young woman, long black hair, cold sharp eyes, minimal makeup, thin determined face, "
         "black hoodie, dark jeans, sneakers, walking city street at night, cold anger expression, "
         "focused on purpose, t_shiori_f"),
    ]),
    ("橘翼", "橘翼", [
        (3031, "小学生（11歳）", "01_11歳_小学生",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "11 year old japanese boy, short cropped black hair, small thin build, innocent smile, happy child, "
         "graphic t-shirt, slim dark jeans, sneakers, warm home, playing, mid 2010s japanese schoolboy style, t_tsubasa_m"),
        (3032, "少年院・丸刈り", "02_14歳_少年院_丸刈り",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "14 year old japanese boy, shaved head buzz cut, still childish face but hardened eyes, thin, "
         "azuki-red prison tracksuit, defensive closed-off look, juvenile detention center, t_tsubasa_m"),
        (3033, "少年院・伸びかけ", "03_16歳_少年院_伸びかけ",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "16 year old japanese boy, short growing-out hair from buzz cut, not yet styled, "
         "still childish face but hardened eyes, muscular thin build, azuki-red prison tracksuit, "
         "juvenile detention center, t_tsubasa_m"),
        (3034, "ホストデビュー", "04_16-17歳_ホスト",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "16 year old japanese boy, black hair center part, clean straight style, groomed eyebrows, "
         "handsome young face, still some boyishness, athletic build, "
         "korean-style host suit, beige suit set, simple silver necklace, "
         "nervous confident mixed expression, mirror reflection, dressing room, t_tsubasa_m"),
        (3035, "格闘家", "05_17-20歳_格闘家",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "20 year old japanese man, short messy black hair slicked back, sharp intense eyes, arrogant smirk, "
         "muscular athletic build, compression tank top, fight shorts, black and gold, "
         "underground ring, spotlight, tattoos visible, t_tsubasa_m"),
        (3036, "タイトルマッチ後", "06_20歳_タイトルマッチ後",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "20 year old japanese man, messy short black hair, hollow empty eyes, thin pale face, "
         "hospital gown, sitting in wheelchair, despair expression, hospital room, dim light, t_tsubasa_m"),
        (3037, "エピローグ（30歳）", "07_30歳_エピローグ",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "30 year old japanese man, short black hair, calm gentle face, peaceful eyes, muscular upper body, "
         "simple modern shirt and slacks, sitting in wheelchair, surrounded by children, "
         "shy happy smile, facility garden sunny, near future japan, t_tsubasa_m"),
    ]),
    ("金子雅也", "金子雅也", [
        (3041, "同期社員（24歳）", "01_24歳_過去_同期社員",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "mid 20s japanese man, short black hair, sallow thin face, cold dead eyes, "
         "sleazy smirk, faint premature wrinkles around eyes, slightly receding temples, "
         "slightly loose tailored navy suit, white shirt, stripe tie, late 2000s salaryman, "
         "unnaturally charming smile that doesn't reach eyes, kaneko_m_m"),
        (3042, "自宅・レイプ（24歳）", "01_24歳_過去_同期社員",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "mid 20s japanese man, short black hair, sallow thin predatory face, cold dead eyes, "
         "casual home clothes late 2000s style, slight smirk, predatory, "
         "bedroom, dim lamp light, tense atmosphere, kaneko_m_m"),
        (3043, "会社（40歳）", "02_40歳_現在_会社",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40 year old japanese man, short thinning salt and pepper hair, sallow wrinkled skin, "
         "cold dead eyes behind friendly facade, fake smile of a career politician, "
         "prematurely aged, slim build, modern navy business suit, office hallway, "
         "too-friendly demeanor with empty eyes, kaneko_m_m"),
        (3044, "ホテル（40歳）", "03_40歳_現在_ホテル",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40 year old japanese man, short thinning salt and pepper hair, sallow wrinkled skin, "
         "cold dead eyes, casual jacket and shirt, smoking cigarette, sitting on hotel room chair, "
         "staring intently, thin predatory smile, dim room, tense atmosphere, kaneko_m_m"),
        (3045, "コレクションルーム", "04_40歳_現在_コレクションルーム",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40 year old japanese man, short thinning salt and pepper hair, sallow skin, "
         "twisted satisfied smile, predatory dead eyes, casual home clothes, "
         "looking at collection wall, dim room, shelves of files, creepy atmosphere, kaneko_m_m"),
    ]),
    ("神崎大輔", "神崎大輔", [
        (3051, "歌舞伎町・半グレ", "01_20代前半_歌舞伎町_半グレ",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "early 20s japanese man, short black hair, rough scarred skin, cold dead eyes, "
         "thin cruel mouth, not handsome, cheap expensive-looking dark suit, white shirt, "
         "fake luxury watch, silver ring, snake-like eyes, bar interior, dim red light, "
         "young yakuza enforcer, unpleasant vibe, jin_kz_m"),
        (3052, "栞殺害後", "02_20代半ば_栞殺害後",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "mid 20s japanese man, short black hair slightly disheveled, rough scarred skin, "
         "cold emotionless eyes, dark bloodstained suit, loosened white collar, "
         "silver ring with blood, leaning against alley wall, cigarette in mouth, "
         "night rain, no remorse, jin_kz_m"),
        (3053, "地下格闘技", "03_20代後半_地下格闘技",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "late 20s japanese man, short black hair, rough scarred face, broken nose scars, "
         "cold predatory eyes, thin cruel smile, muscular fighter build, "
         "compression tank top, fight shorts, dragon tiger graphic, "
         "sweat and bruises, underground ring, spotlight, crowd roar, fighting pose, jin_kz_m"),
    ]),
    ("黒崎徹", "先輩", [
        (3061, "現在・支援者", "01_30代前半_現在_支援者",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "early 30s japanese man, short black hair, weathered scarred rough face, "
         "deep-set tired eyes, visible acne scars, medium build, simple shirt and jacket, "
         "quiet caring expression, slight awkward smile, standing by wheelchair, "
         "sunny facility, lived-in hard life look, kuro_t_m"),
        (3062, "少年院・丸刈り", "02_少年院_丸刈り",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "16 year old japanese boy, shaved head buzz cut, rough tough face, scarring, "
         "tough but kind eyes, still youthful face, azuki-red prison tracksuit, "
         "juvenile detention center, talking to younger boy, protective older brother vibe, kuro_t_m"),
        (3063, "少年院・伸びかけ", "03_少年院_伸びかけ",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "18 year old japanese young man, short growing-out hair from buzz cut, rough skin, "
         "tough but kind eyes, muscular build, azuki-red prison tracksuit, "
         "about to be released, kuro_t_m"),
        (3064, "ホスト後・先輩", "04_ホスト後_先輩",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "early 20s japanese man, short black hair, rough weathered face, scars, "
         "sharp but kind eyes, not handsome, simple suit, cigarette in mouth, "
         "tough caring aura, nightclub alley, neon lights, kuro_t_m"),
    ]),
    ("施設長", "施設長", [
        (3081, "施設長", "01_50代_施設長",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "50 year old japanese man, gray short balding hair, receding hairline, round sweaty face, "
         "beady piggy eyes, double chin, small glasses, overweight pot belly, disgusting fat man, "
         "gentle facade, institutional clothes, cardigan and shirt, dark office, "
         "predatory hidden eyes behind kindly smile, creepy, childrens home director, shisetsucho_m"),
    ]),
    ("養父", "里親", [
        (3091, "養父・虐待者", "01_40代_養父_虐待者",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "mid 40s japanese man, balding, receding gray-black hair, alcoholic bloated red nose, "
         "ugly stubble, beer belly, ugly gross unattractive face, "
         "cheap t-shirt and track pants, suburban house living room, holding beer can, "
         "aggressive ugly expression, satoya_m"),
    ]),
    ("警察官", "警察官", [
        (3101, "取調べ（40代）", "01_40代_取調べ",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "late 40s japanese man, short graying hair, sallow tired skin, heavy eyebags, "
         "weary paunchy middle-aged face, plain unattractive, "
         "dark navy stand-collar police uniform, cap, interrogation room, holding file, "
         "apathetic expression, seen-it-all attitude, police_officer_m"),
        (3102, "デスク業務（50歳）", "02_50歳_デスク業務",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "50 year old japanese man, short salt-and-pepper hair, sallow wrinkled skin, "
         "heavy eyebags, weary face, paunch, plain unattractive, "
         "dark blue police uniform, messy police station desk, filing paperwork, "
         "tired grim look, police_officer_m"),
    ]),
    ("弁護士", "弁護士", [
        (3111, "弁護士", "01_50代_弁護士",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "late 50s japanese man, thinning gray white hair, deeply wrinkled face, age spots, "
         "plain elderly face, metal frame glasses, formal navy suit, white dress shirt, "
         "bordeaux stripe tie, black leather shoes, classic watch, professional neutral expression, "
         "law office, holding document envelope, not handsome, lawyer_estate_m"),
    ]),
    ("百合子の母", "百合子の母", [
        (3121, "実母", "01_60代_実母",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "60 year old japanese woman, gray streaked black perm hair, deeply wrinkled tired face, "
         "worn elderly country woman, plain unattractive, "
         "simple older clothes, cardigan, wool skirt, small kitchen, "
         "heavy burdens expression, yuriko_mother_f"),
    ]),
    ("誠の祖父", "誠の祖父", [
        (3131, "存命（70代）", "01_70代_存命",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "elderly japanese man in his 70s, short white hair, receding hairline, deeply wrinkled face, "
         "deep-set wise eyes, gentle warm smile, thin build, cardigan and shirt, holding old gold coin, "
         "traditional japanese room, warm nostalgic atmosphere, grandfather_m"),
        (3132, "葬儀", "02_葬儀",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "elderly deceased japanese man in his late 70s, white hair, peaceful expression, "
         "black funeral kimono, lying in coffin, japanese funeral, white flowers, "
         "solemn quiet atmosphere, grandfather_m"),
    ]),
    ("義母", "義母", [
        (3141, "自宅・虐待黙認", "01_40代_自宅_虐待黙認",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40s japanese woman, black hair streaked with gray, gaunt haggard face, thin-lipped, "
         "worn out tired expression, unattractive plain, "
         "plain housewife clothes, apron, suburban kitchen, avoiding eye contact, "
         "complicit silence, stepmother_f"),
        (3142, "警察・偽証", "02_40代_警察_偽証",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "40s japanese woman, gray streaked hair, gaunt haggard face, worn out, "
         "plain clothes, sitting in police station, looking down, "
         "guilty nervous expression, giving false testimony, small trembling voice posture, stepmother_f"),
    ]),
    ("トー横の年上の女", "トー横の年上の女", [
        (3071, "トー横の先輩", "01_20代前半_トー横の先輩",
         "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "early 20s japanese woman, dark hair face-framing curls, thick bangs, "
         "rough hard weathered face, dark circles under eyes, hard life look, not cute, "
         "yamikawaii makeup, pink eyeshadow, plump build, "
         "white fake fur coat, frill blouse, pleated mini skirt, patterned tights, platform shoes, "
         "MCM backpack, shinjuku alley night, cigarette, protective older sister aura, "
         "streets have not been kind, toyoko_girl_f"),
    ]),
]


def build_section(name, variants):
    lines = []
    def a(*args):
        lines.append("".join(args))

    a("\n## 画像生成情報\n")
    a(f"- ベースモデル: {BASE_MODEL}\n")
    a(f"- LoRA: {LORA}\n")
    a(f"- 解像度: {RES} / {PARAMS}\n")
    a("\n### Negative Prompt（全バリアント共通）\n")
    a("```\n")
    a(NEG + "\n")
    a("```\n")
    a("\n### バリアント一覧\n")
    a("\n| バリアント | フォルダ | Seeds |\n")
    a("|-----------|---------|-------|\n")
    for base, label, folder, _ in variants:
        seeds = ",".join(str(base + i) for i in range(4))
        a(f"| {label} | {folder}/ | {seeds} |\n")
    a("\n### English Prompts\n")
    for base, label, folder, prompt in variants:
        a(f"\n**{label}**:\n")
        a("```\n")
        a(prompt + "\n")
        a("```\n")

    return "".join(lines)


# File name mapping: internal_name -> (file_name, file_exists_already)
FILE_MAP = {
    "橘誠": "橘誠.md",
    "橘百合子": "橘百合子.md",
    "橘栞": "橘栞.md",
    "橘翼": "橘翼.md",
    "金子雅也": "金子雅也.md",
    "神崎大輔": "神崎大輔.md",
    "黒崎徹": "先輩.md",     # filename is still 先輩
    "施設長": "施設長.md",
    "養父": "里親.md",         # filename is still 里親
    "警察官": "警察官.md",
    "弁護士": "弁護士.md",
    "百合子の母": "百合子の母.md",
    "誠の祖父": "誠の祖父.md",  # does not exist yet
    "義母": "義母.md",          # does not exist yet
    "トー横の年上の女": "トー横の年上の女.md",
}

# For missing chars, create minimal files with just image info
MINIMAL_TEMPLATE = """# {title}

## 基本情報
- 画像のみ作成済み。ストーリー設定は未記載

{section}
"""


def main():
    for name, display_label, variants in CHARACTERS:
        fname = FILE_MAP[name]
        path = os.path.join(CHAR_DIR, fname)

        section = build_section(name, variants)

        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            # Remove previous image info section if it exists
            content = re.sub(r"\n## 画像生成情報\n.*?(?=\n## |\Z)", "", content, flags=re.DOTALL)
            content = content.rstrip() + section
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  UPDATED {fname}")
        else:
            title = display_label
            minimal = MINIMAL_TEMPLATE.format(title=title, section=section)
            with open(path, "w", encoding="utf-8") as f:
                f.write(minimal)
            print(f"  CREATED {fname}")


if __name__ == "__main__":
    print("Syncing image info to character setting files...")
    print(f"Directory: {CHAR_DIR}")
    main()
    print("Done.")
