"""Private stdio MCP bridge: trusted host metadata selects a token, never tool arguments."""
import asyncio
import json
import re

from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from portal_config import PORTAL_ITEMS, read_tokens
from portal_http import read_item, read_timetable

server = Server('kute-fake-portal')


@server.list_tools()
async def list_tools():
    return [types.Tool(name='tra_portal', description='Đọc một mục của chính người hỏi trên portal giả.',
                       inputSchema={'type': 'object', 'properties': {'muc': {'type': 'string', 'enum': list(PORTAL_ITEMS)}},
                                    'required': ['muc'], 'additionalProperties': False}),
            types.Tool(name='tra_tkb', description='Đọc thời khoá biểu của một lớp; bỏ trống lop để đọc lớp của chính người hỏi.',
                       inputSchema={'type': 'object', 'properties': {'lop': {'type': 'string', 'pattern': '^[A-Z0-9]{0,8}$'}},
                                    'additionalProperties': False})]


@server.call_tool()
async def call_tool(name, arguments):
    result = {'loi': 'Yêu cầu portal không hợp lệ.'}
    item = name == 'tra_portal' and isinstance(arguments, dict) and set(arguments) == {'muc'} and arguments['muc'] in PORTAL_ITEMS
    timetable = (name == 'tra_tkb' and isinstance(arguments, dict) and set(arguments) <= {'lop'}
                 and isinstance(arguments.get('lop', ''), str) and re.fullmatch(r'[A-Z0-9]{0,8}', arguments.get('lop', '')))
    if item or timetable:
        metadata = server.request_context.meta
        values = metadata.model_dump() if metadata else {}
        student_id = values.get('kute/student_id')
        try:
            tokens = read_tokens()
            token = tokens.get(student_id) if isinstance(student_id, str) else None
            if token:
                result = (await asyncio.to_thread(read_item, token, arguments['muc']) if item
                          else await asyncio.to_thread(read_timetable, token, arguments.get('lop', '')))
            else:
                result = {'loi': 'Không xác định được hồ sơ của người hỏi.'}
        except (ValueError, OSError):
            result = {'loi': 'Chưa cấu hình token portal hợp lệ.'}
    return types.CallToolResult(content=[types.TextContent(type='text', text=json.dumps(result, ensure_ascii=False))],
                                isError='loi' in result)


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == '__main__':
    asyncio.run(main())
