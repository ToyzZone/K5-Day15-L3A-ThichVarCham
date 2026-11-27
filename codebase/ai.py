"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI. NHÓM VIẾT phần gọi model thật.

Hợp đồng (giữ nguyên để khung đo được token):
    call_model(system: str, user: str) -> dict với 4 khoá
        "text":       str   chữ model trả về
        "model":      str   tên model đã gọi (để tra giá ở bảng giá model)
        "tokens_in":  int   số token vào, lấy từ trường usage trong phản hồi API — KHÔNG ước lượng
        "tokens_out": int   số token ra, gồm cả token suy luận / suy nghĩ nếu API tính riêng
    @model_call (từ tracing.py) tự ghi mỗi lần gọi vào trace; agent.py gọi call_model bao nhiêu lần
    cũng được, khung tự cộng token.
    Lỗi gọi model (hết lượt, sai key, mất mạng): cứ để exception bay ra — khung ghi lỗi vào cột error.

Chế độ giả (mặc định khi .env chưa có MODEL_PROVIDER, hoặc MODEL_PROVIDER=fake):
    trả một câu giả cố định, model "fake", token 0 — để luồng chạy hết từ trước CP2 (guide bước 3.2).
    Lượt `run.py eval` / `run.py simulate` chạy bằng model giả KHÔNG được tính.

Nối model thật: điền .env (chép từ .env.example), rồi viết nhánh gọi API ở dưới theo docs/connect-model.md
(có ví dụ OpenAI, Claude, model chạy trên máy, và cách nối nhà cung cấp khác). Không dán API key vào file này.
"""
import os
import json
import urllib.request
import urllib.error
import urllib.parse

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env(path=os.path.join(ROOT, ".env")):
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có. Khung — không cần sửa."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
MODEL_PROVIDER = (os.environ.get("MODEL_PROVIDER") or "fake").strip().lower()
MODEL_NAME = (os.environ.get("MODEL_NAME") or "").strip()
API_KEY = (os.environ.get("API_KEY") or "").strip()


def _post(url, headers, body):
    request = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'),
                                     headers={'Content-Type': 'application/json', **headers}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        # Không đưa response hoặc URL chứa thông tin xác thực vào trace.
        raise RuntimeError('API model trả HTTP %s; kiểm tra provider, model, key và hạn mức.' % exc.code) from None
    except urllib.error.URLError:
        raise RuntimeError('Không kết nối được API model; kiểm tra mạng.') from None


@model_call
def call_model(system: str, user: str) -> dict:
    if MODEL_PROVIDER == "fake":
        last = (user.strip().splitlines() or [""])[-1]
        return {"text": "[câu trả lời giả — chưa nối model] " + last[:60], "model": "fake", "tokens_in": 0, "tokens_out": 0}

    if not MODEL_NAME or not API_KEY:
        raise ValueError('Cần điền MODEL_NAME và API_KEY trong .env.')
    actual_model = MODEL_NAME
    if MODEL_PROVIDER in ('openai', 'openrouter'):
        url = ('https://openrouter.ai/api/v1/chat/completions' if MODEL_PROVIDER == 'openrouter'
               else 'https://api.openai.com/v1/chat/completions')
        data = _post(url, {'Authorization': 'Bearer ' + API_KEY},
                     {'model': MODEL_NAME, 'messages': [{'role': 'system', 'content': system},
                                                       {'role': 'user', 'content': user}]})
        if data.get('error'):
            raise RuntimeError('API model trả lỗi; kiểm tra mã model, quyền truy cập và hạn mức.')
        text = data['choices'][0]['message']['content']
        actual_model = data.get('model') or MODEL_NAME
        usage = data['usage']
        tokens_in, tokens_out = usage['prompt_tokens'], usage['completion_tokens']
    elif MODEL_PROVIDER == 'anthropic':
        data = _post('https://api.anthropic.com/v1/messages',
                     {'x-api-key': API_KEY, 'anthropic-version': '2023-06-01'},
                     {'model': MODEL_NAME, 'max_tokens': 2048, 'system': system,
                      'messages': [{'role': 'user', 'content': user}]})
        text = ''.join(part.get('text', '') for part in data['content'] if part['type'] == 'text')
        usage = data['usage']
        tokens_in = usage['input_tokens'] + usage.get('cache_read_input_tokens', 0) + usage.get('cache_creation_input_tokens', 0)
        tokens_out = usage['output_tokens']
    elif MODEL_PROVIDER == 'gemini':
        model = urllib.parse.quote(MODEL_NAME.removeprefix('models/'), safe='')
        data = _post('https://generativelanguage.googleapis.com/v1beta/models/' + model + ':generateContent',
                     {'x-goog-api-key': API_KEY},
                     {'systemInstruction': {'parts': [{'text': system}]},
                      'contents': [{'role': 'user', 'parts': [{'text': user}]}],
                      'generationConfig': {'responseMimeType': 'application/json'}})
        candidates = data.get('candidates', [])
        text = ''.join(part.get('text', '') for part in (candidates[0].get('content', {}).get('parts', []) if candidates else []) if not part.get('thought'))
        usage = data['usageMetadata']
        tokens_in = usage['promptTokenCount']
        tokens_out = usage.get('candidatesTokenCount', 0) + usage.get('thoughtsTokenCount', 0)
    else:
        raise ValueError('Provider được hỗ trợ: openrouter, openai, anthropic, gemini hoặc fake.')
    if not text:
        raise RuntimeError('Model không trả nội dung; kiểm tra giới hạn hoặc bộ lọc của API.')
    return {'text': text, 'model': actual_model, 'tokens_in': int(tokens_in), 'tokens_out': int(tokens_out)}
