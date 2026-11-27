"""Model connection: the ONLY place in the prototype that calls an AI model. The TEAM writes the real model calls.

Contract (keep it so the framework can measure tokens):
    call_model(system: str, user: str) -> dict with 4 keys
        "text":       str   text returned by the model
        "model":      str   name of the model actually called (to look up its price)
        "tokens_in":  int   input tokens, taken from the usage field of the API response, NEVER estimated
        "tokens_out": int   output tokens, including reasoning / thinking tokens if the API counts them separately
    @model_call (from tracing.py) records every call in the trace; agent.py may call call_model any number of
    times, the framework adds up the tokens.
    Model call errors (quota, wrong key, no network): let the exception propagate; the framework writes it to the error column.

Fake mode (default when .env has no MODEL_PROVIDER, or MODEL_PROVIDER=fake):
    returns a fixed fake sentence, model "fake", 0 tokens, so the flow runs end to end before CP2 (guide step 3.2).
    `run.py eval` / `run.py simulate` runs made with the fake model DO NOT count.

Real model: fill in .env (copy .env.example), then write the API branch below following docs/connect-model.md
(examples for OpenAI, Claude, local models, and how to connect other providers). Never paste an API key into this file.
"""
import os
import json
import urllib.request
import urllib.error
import urllib.parse

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env(path=os.path.join(ROOT, ".env")):
    """Read a .env file (one KEY=VALUE per line) into environment variables without overriding variables already set. Framework code, no need to edit."""
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
        # Never put the response or a URL carrying credentials into the trace.
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
