"""Synchronous adapter for the existing agent; each lookup owns a short stdio session."""
import asyncio
import json
import os
import sys
from datetime import timedelta
from pathlib import Path

from portal_config import PORTAL_ITEMS, api_url, token_file


async def _call(student_id, tool, arguments):
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
                response = await session.call_tool(tool, arguments, meta={'kute/student_id': student_id})
                texts = [part.text for part in response.content if part.type == 'text']
                return json.loads(texts[0]) if texts else {}


def _run(student_id, tool, arguments, well_formed):
    try:
        result = asyncio.run(_call(student_id, tool, arguments))
        if not isinstance(result, dict) or ('loi' not in result and not well_formed(result)):
            return {'loi': 'MCP portal trả dữ liệu không hợp lệ.'}
        return result
    except ImportError:
        return {'loi': 'Chưa cài SDK MCP; chạy pip install -r requirements.txt.'}
    except Exception:
        # Errors may contain transport/process details; never put credentials into model context.
        return {'loi': 'Không gọi được MCP portal; kiểm tra SDK, token và API portal.'}


def _linked(student_id):
    return isinstance(student_id, str) and bool(student_id) and not student_id.startswith('unlinked:')


def lookup(student_id, item):
    if not _linked(student_id):
        return {'loi': 'Tài khoản Discord chưa liên kết với hồ sơ giả.'}
    if item not in PORTAL_ITEMS:
        return {'loi': 'Mục portal không hợp lệ.'}
    return _run(student_id, 'tra_portal', {'muc': item}, lambda result: result.get('muc') == item and 'du_lieu' in result)


def lookup_timetable(student_id, code):
    """Timetable of a class, or of the asker's own class when code is empty. Unlinked accounts (group members) get nothing."""
    if not _linked(student_id):
        return {'loi': 'Tài khoản Discord chưa liên kết với hồ sơ giả.'}
    return _run(student_id, 'tra_tkb', {'lop': code} if code else {},
                lambda result: isinstance(result.get('buoi'), list) and isinstance(result.get('ngay_phu'), dict))
