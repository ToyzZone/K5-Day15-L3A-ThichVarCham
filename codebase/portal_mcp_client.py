"""Synchronous adapter for the existing agent; each lookup owns a short stdio session."""
import asyncio
import json
import os
import sys
from datetime import timedelta
from pathlib import Path

from portal_config import PORTAL_ITEMS, api_url, token_file


async def _lookup(student_id, item):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    params = StdioServerParameters(command=sys.executable,
        args=[str(Path(__file__).with_name('portal_mcp_server.py'))],
        env={'PORTAL_API_URL': api_url(), 'PORTAL_TOKENS_FILE': str(token_file()), 'PYTHONUTF8': '1'})
    # No model key, Discord token or portal bearer token is placed in MCP arguments.
    with open(os.devnull, 'w') as errors:
        async with stdio_client(params, errlog=errors) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream, read_timeout_seconds=timedelta(seconds=20)) as session:
                await session.initialize()
                response = await session.call_tool('tra_portal', {'muc': item}, meta={'kute/student_id': student_id})
                texts = [part.text for part in response.content if part.type == 'text']
                result = json.loads(texts[0]) if texts else {}
                if not isinstance(result, dict) or ('loi' not in result and (result.get('muc') != item or 'du_lieu' not in result)):
                    return {'loi': 'MCP portal trả dữ liệu không hợp lệ.'}
                return result


def lookup(student_id, item):
    if not isinstance(student_id, str) or not student_id or student_id.startswith('unlinked:'):
        return {'loi': 'Tài khoản Discord chưa liên kết với hồ sơ giả.'}
    if item not in PORTAL_ITEMS:
        return {'loi': 'Mục portal không hợp lệ.'}
    try:
        return asyncio.run(_lookup(student_id, item))
    except ImportError:
        return {'loi': 'Chưa cài SDK MCP; chạy pip install -r requirements.txt.'}
    except Exception:
        # Errors may contain transport/process details; never put credentials into model context.
        return {'loi': 'Không gọi được MCP portal; kiểm tra SDK, token và API portal.'}
