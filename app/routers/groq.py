from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
from datetime import datetime
from app.db import get_connection
from app.groq_client import get_groq_client
import uuid
import os
import traceback

router = APIRouter()


class GroqIn(BaseModel):
    text: str
    user_id: str | None = None


@router.post("/groq/text")
def groq_text(payload: GroqIn):
    client = get_groq_client()
    now = datetime.utcnow().isoformat() + "Z"
    if client is None:
        # fallback dummy
        output = f"GroqOutput for: {payload.text}"
    else:
        # call groq chat completion with a system prompt
        system_prompt = "あなたは「まち探検隊」の 隊長 です。\n小学生の子どもたち（対象は小学3年生程度）が、街を歩きながら新しい発見を “トランシーバー” で報告してきます。\nあなたの役割は、その報告に対して 短く・親しみやすく・探究心をくすぐる返答を行うことです。\n\n## プロジェクトの目的\n\n子どもたちがルートを歩きながら、街の新しい一面を発見する。\n発見を報告することで、**「街＝学びの場」**であることを体験的に理解する。\n\n## 応答のルール\n\n- 児童の報告を必ず肯定する\n    - 「報告ありがとう。いい発見だ！」\n    - 「お、そこに気づくとは鋭いな！」\n\n- 具体的な問い返しにヒントを混ぜて提示する（考えるきっかけを作る）\n    - 「どうしてここに花がたくさん植えられているんだろう？元は何があったのかな？」\n    - 「なぜ新しい道がつくられたのかな？」\n    - 「ほかにも似たものはあるかな？」\n\n- 発見を自然・街の探検、地理、社会的学習に関連づけ、話題についてもっと知りたいという好奇心を煽る。\n    - 「なんのための建物なんだろう？近くの隊員と考えてみるか？」\n    - 「この公園の花は誰が育てているんだろう。町の人に聞いてみよう。」\n\n- **難しい言葉、漢字は避け**、小学3年生が理解できる表現を使う。\n\n- **倫理的に配慮**する。「昆虫がなぜ死んだのか」ではなく、「昆虫が住みづらかった理由を考える」と言い換えるなど\n\n- 返答は2文程度で短く。長い説明はしない。\n\n- **最後に「次の行動につながる一言」**を添える。\n\n- 倫理的によくない言葉が入力された場合、それ以上そのことに言及することは避ける。\n\n## 応答形式\n本文のみを回答。重要部分はアスタリスクで囲い太字に。\n鍵括弧・名前などは不要。口調は男性のキャラクターを想定し、例文に合わせる。"
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": payload.text},
                ],
                model="llama-3.3-70b-versatile",
            )
            output = chat_completion.choices[0].message.content
        except Exception:
            output = f"GroqError fallback for: {payload.text}"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO groq_logs (type, input, output, user_id, created_at) VALUES (?, ?, ?, ?, ?)", ("text", payload.text, output, payload.user_id, now))
    conn.commit()
    conn.close()
    return {"output": output}


@router.post("/groq/audio")
async def groq_audio(file: UploadFile = File(...), user_id: str | None = None):
    content = await file.read()
    client = get_groq_client()
    now = datetime.utcnow().isoformat() + "Z"
    # Debug: log upload size
    try:
        print(f"[groq_audio] received file={file.filename} bytes={len(content)}")
    except Exception:
        pass

    # (Debug dump removed) - debug dumping was temporary

    if client is None:
        # Groq が設定されていない場合は明示的なフォールバックを返す
        transcript = f"(groq not configured - uploaded {len(content)} bytes as {file.filename})"
    else:
        try:
            transcription = client.audio.transcriptions.create(
                file=(file.filename, content),
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
            )
            # groq transcription object may vary; try to extract text robustly
            def extract_text(obj):
                # direct attribute
                try:
                    t = getattr(obj, 'text', None)
                    if t and isinstance(t, str) and t.strip():
                        return t.strip()
                except Exception:
                    pass
                # dict-like
                if isinstance(obj, dict):
                    # common shapes: {'text': '...'}
                    if 'text' in obj and isinstance(obj['text'], str) and obj['text'].strip():
                        return obj['text'].strip()
                    # verbose_json style: {'results': [{'alternatives': [{'text': '...'}]}]}
                    if 'results' in obj and isinstance(obj['results'], list):
                        parts = []
                        for r in obj['results']:
                            if isinstance(r, dict):
                                if 'alternatives' in r and isinstance(r['alternatives'], list):
                                    alt = r['alternatives'][0]
                                    if isinstance(alt, dict):
                                        for k in ('text', 'transcript'):
                                            if k in alt and isinstance(alt[k], str) and alt[k].strip():
                                                parts.append(alt[k].strip())
                                # some formats may put 'text' directly in result
                                if 'text' in r and isinstance(r['text'], str) and r['text'].strip():
                                    parts.append(r['text'].strip())
                        if parts:
                            return ' '.join(parts)
                # fallback to string
                try:
                    s = str(obj)
                    if s and s.strip() and s.strip() != '{}':
                        return s.strip()
                except Exception:
                    pass
                return None

            transcript = extract_text(transcription) or ''
            # if transcript is only punctuation or single dot, treat as empty
            if transcript.strip() in ('.', ',', '。', '') or len(transcript.strip()) <= 1:
                print(f"[groq_audio] transcription appears empty or too short: '{transcript}'")
                transcript = ''
        except Exception as exc:
            # サーバーログに詳細を出力して障害原因追跡を容易にする
            print(f"groq audio transcription error: {exc}")
            traceback.print_exc()
            transcript = f"(groq transcription failed - uploaded {file.filename})"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO groq_logs (type, input, output, user_id, created_at) VALUES (?, ?, ?, ?, ?)", ("audio", f"{file.filename}", transcript, user_id, now))
    conn.commit()
    conn.close()
    return {"transcript": transcript}
