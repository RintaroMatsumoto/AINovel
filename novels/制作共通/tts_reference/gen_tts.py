"""Generate prologue TTS via AivisSpeech + timing data"""
import json, urllib.request, urllib.parse, wave, io, time, os, sys
sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://100.112.59.35:10101"
SPEAKER = 1388823424  # 凛音エル ノーマル
OUT = r"C:\Users\GoldRush\Documents\MyProject\AIvideo\scripts\prologue"
os.makedirs(OUT, exist_ok=True)

text = """俺は書斎で、画面の数字を見ていた。目標を超えていた。
俺は背もたれに凭れて、大きく息を吐いた。いつのまにか詰めていた息だった。肩から力が抜けて、椅子がぎしりと鳴った。何度も聞いてきた音のはずなのに、今夜はその軋みがやけに遠くから聞こえる。
しばらく画面を眺めていた。ただの数字が、ただ並んでいる。それが、やっとここまできた。そう思うと、立ち上がるのが惜しくなった。あと少しだけこの数字を見ていたかった。でもそれより、先に伝えたい人がいた。
書斎を出た。廊下はいつも冷えているのに、今夜は気にならなかった。リビングを通り抜けて、台所の入り口に立つ。
百合子はシンクの前に立って、まな板の上の大根を刻んでいた。包丁のリズムが一定で、速い。俺が立っているのに気づいていない。
「百合子」
彼女の手が止まった。包丁をまな板に置いて、ゆっくりと振り返る。俺の顔を見て、なにかを探るように数秒。それから、口を手で押さえた。彼女はもうわかっていた。確認の言葉はいらなかった。
百合子はしばらく黙っていた。目が潤んでいるのが、キッチンの蛍光灯の下でよく見えた。それから二歩、三歩と近づいてきて、俺の胸に額を押しつけた。そういうことをする人ではなかった。でも今夜は違った。
俺は彼女の背中に手を回した。エプロンの紐が指に触れた。細い肩が、かすかに震えている。
「やったな」
「うん」
階段を降りてくる足音がした。翼の靴下が段を滑る音。そのあとに栞の裸足。ふたりとも台所まで来て、俺たちの様子を見て立ち止まった。
「どうしたの」
栞の声だった。
百合子が顔を上げて、目をこすりながら笑った。「お父さんがね、目標に届いたんだって」
「え、あれ」
栞が俺の顔を見た。それから踵を返して、書斎に向かって走っていった。翼もあとを追う。俺と百合子も、ゆっくりとあとから歩いていった。
書斎では、栞がモニターの前に立って、数字を指さしていた。
「これ、一億ってこと？」
「そういうことだ」
栞はしばらく数字を見つめてから、振り返って俺の顔を見た。にやりとした。
「やるじゃん」
翼は画面を覗き込んで、それから俺を見上げた。よくわかっていない顔だったけれど、みんなが笑っているから、自分も笑った。
「飯にしよう」
食卓につく。今夜は肉じゃがとほうれん草のおひたしと味噌汁。それから出汁巻き卵が一品多い。百合子が朝から気づいていたのかどうかはわからない。でも彼女は、そういうことをなんとなく察する人だった。
「待って」
百合子がスマートフォンを取り出した。食卓の端に立てかけて、タイマーを十秒にセットする。栞の隣に座った。翼があわてて箸を置く。栞が翼の寝ぐせをちょっとだけ直した。画面の数字が五を切った。
フラッシュが光った。
瞼の裏に白い残像が焼きつく。湯気の立つ肉じゃが、四つの箸、翼の笑った顔、栞の口元——そのすべてが光のフレームに閉じ込められて、ゆっくりと消えた。残像のなかで、百合子の目がまだ少し赤いのが見えた。
食卓がいつもより賑やかだった。翼が三回箸を落とした。三回目には栞が先に拾ってやって、翼が「ありがとう」と言った。そんなことでみんなが笑った。
夜になった。
俺はリビングのソファに座っている。テレビも本もつけずに、台所から聞こえてくる音を聞いている。水の流れる音。皿と皿がかすかに触れ合う音。蛇口をひねる音。それから鼻歌。百合子が皿を洗いながら歌っている。今夜の声は、いつもより少しだけ大きい。たぶん、自分でも気づいていないんだろう。
俺はソファの背に頭を預けて、目を閉じた。フラッシュの残像はもう消えている。でも瞼の裏には、さっきの食卓がまだうっすらと残っていた。百合子の潤んだ目。栞のにやりとした顔。翼の笑顔。彼女が俺の胸に額を押しつけてきたときの、エプロンの紐の感触。
もう少しだけ、ここにいようと思った。今夜はまだ、終わりたくなかった。"""

# Save clean text
with open(os.path.join(OUT, "clean.txt"), "w", encoding="utf-8") as f:
    f.write(text)

# Split into chunks (500 chars max)
def split_chunks(text, max_chars=500):
    paragraphs = text.split("\n")
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) + 1 <= max_chars:
            current += para + "\n"
        else:
            if current:
                chunks.append(current.strip())
            while len(para) > max_chars:
                chunks.append(para[:max_chars])
                para = para[max_chars:]
            current = para + "\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks

chunks = split_chunks(text)
print(f"Text: {len(text)} chars -> {len(chunks)} chunks")

# Synthesize each chunk
wav_parts = []
timing = []
for i, chunk in enumerate(chunks):
    print(f"  Chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...", end=" ", flush=True)
    for attempt in range(3):
        try:
            url = f"{BASE}/audio_query?speaker={SPEAKER}&text={urllib.parse.quote(chunk)}"
            req = urllib.request.Request(url, method="POST")
            resp = urllib.request.urlopen(req, timeout=60)
            query = json.loads(resp.read())

            # Set speed
            query["speedScale"] = 0.9  # やや遅め

            url = f"{BASE}/synthesis?speaker={SPEAKER}"
            req = urllib.request.Request(url, data=json.dumps(query).encode(), method="POST")
            req.add_header("Content-Type", "application/json")
            resp = urllib.request.urlopen(req, timeout=120)
            wav_data = resp.read()

            with wave.open(io.BytesIO(wav_data), "rb") as w:
                duration = w.getnframes() / w.getframerate()
            wav_parts.append(wav_data)
            timing.append({"duration": round(duration, 2), "chars": len(chunk)})
            print(f"OK {duration:.1f}s")
            break
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(3)
    time.sleep(0.5)

# Combine WAVs
output_wav = os.path.join(OUT, "audio.wav")
frames = []
total_duration = 0.0
for wav_data in wav_parts:
    with wave.open(io.BytesIO(wav_data), "rb") as w:
        frames.append(w.readframes(w.getnframes()))
        total_duration += w.getnframes() / w.getframerate()

with wave.open(output_wav, "wb") as w:
    with wave.open(io.BytesIO(wav_parts[0]), "rb") as first:
        w.setnchannels(first.getnchannels())
        w.setsampwidth(first.getsampwidth())
        w.setframerate(first.getframerate())
    for f in frames:
        w.writeframes(f)

print(f"\nAudio: {output_wav}")
print(f"  Duration: {total_duration:.1f}s ({total_duration/60:.1f}min)")
print(f"  Size: {os.path.getsize(output_wav)//1024} KB")

# Timing with scroll position
scroll_speed = len(text) / total_duration  # chars per second
current_pos = 0.0
for t in timing:
    t["scroll_start"] = round(current_pos, 2)
    current_pos += t["duration"]
    t["scroll_end"] = round(current_pos, 2)

timing_file = os.path.join(OUT, "timing.json")
with open(timing_file, "w", encoding="utf-8") as f:
    json.dump({"total_chars": len(text), "total_duration": round(total_duration, 2),
               "scroll_speed_cps": round(scroll_speed, 2), "chunks": timing},
              f, ensure_ascii=False, indent=1)
print(f"Timing: {timing_file}")
print(f"  Scroll speed: {scroll_speed:.1f} chars/sec")
print("DONE")
