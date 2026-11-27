"""Tạo kênh chỉ cho coach: python codebase/setup_coach_channel.py."""
import asyncio
import json
import sys
from pathlib import Path

import discord
from ai import load_env
import os

ROOT = Path(__file__).resolve().parent.parent
CHANNEL_FILE = ROOT / 'runtime' / 'coach-channel.json'


def private_for_coaches(channel, coach_role, bot_member):
    if not isinstance(channel, discord.TextChannel):
        return False
    if channel.overwrites_for(channel.guild.default_role).view_channel is not False:
        return False
    if not channel.permissions_for(coach_role).view_channel:
        return False
    for target, overwrite in channel.overwrites.items():
        if overwrite.view_channel is True and target.id not in (coach_role.id, bot_member.id):
            return False
    return channel.permissions_for(bot_member).send_messages


async def provision():
    load_env()
    guild_id = int(os.environ['DISCORD_GUILD_ID'])
    role_id = int(os.environ['DISCORD_LAB_COACH_ROLE_ID'])
    client = discord.Client(intents=discord.Intents(guilds=True))
    outcome = {'error': False}

    @client.event
    async def on_ready():
        try:
            guild = client.get_guild(guild_id)
            if guild is None:
                raise ValueError('Bot chưa có trong máy chủ đã cấu hình.')
            coach_role = guild.get_role(role_id)
            saved = json.loads(CHANNEL_FILE.read_text(encoding='utf-8')) if CHANNEL_FILE.exists() else {}
            configured = os.getenv('DISCORD_COACH_DATA_CHANNEL_ID') or (saved.get('channel_id') if saved.get('guild_id') == guild_id else None)
            channel = guild.get_channel(int(configured)) if configured else None
            if channel is None and not configured:
                channel = next((c for c in guild.text_channels if c.name == 'coach-du-lieu'), None)
            if channel:
                if not isinstance(channel, discord.TextChannel):
                    raise ValueError('Kênh dữ liệu phải là kênh văn bản.')
                permissions = channel.permissions_for(guild.me)
                if not permissions.view_channel or not permissions.send_messages:
                    raise ValueError('Bot cần quyền Xem kênh và Gửi tin nhắn trong kênh dữ liệu.')
            elif configured:
                raise ValueError('ID kênh dữ liệu không tồn tại trong server đã cấu hình.')
            else:
                if coach_role is None or coach_role == guild.default_role:
                    raise ValueError('Cần role Lab Coach hợp lệ để tạo kênh mới.')
                channel = await guild.create_text_channel('coach-du-lieu',
                    topic='Coach kiểm tra kho: !kb, !kb ds, !kb xem D5, !kb dexuat. Chỉ xem dữ liệu.',
                    overwrites={guild.default_role: discord.PermissionOverwrite(view_channel=False),
                                coach_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)},
                    reason='Tạo kênh dữ liệu riêng cho Lab Coach theo yêu cầu chủ dự án')
            CHANNEL_FILE.parent.mkdir(parents=True, exist_ok=True)
            CHANNEL_FILE.write_text(json.dumps({'guild_id': guild_id, 'channel_id': channel.id}), encoding='utf-8')
            print('Đã cấu hình #' + channel.name + ' · ID: ' + str(channel.id))
            print('Khởi động lại bot rồi dùng !kb trong kênh này.')
        except discord.Forbidden:
            outcome['error'] = True
            print('Bot thiếu quyền Quản lý kênh hoặc quyền đặt phân quyền. Cấp quyền này rồi chạy lại, hoặc tạo kênh riêng thủ công và đặt DISCORD_COACH_DATA_CHANNEL_ID trong .env.')
        except (ValueError, discord.HTTPException) as exc:
            outcome['error'] = True
            print(str(exc) if isinstance(exc, ValueError) else 'Discord từ chối thao tác: ' + type(exc).__name__)
        finally:
            await client.close()

    async with client:
        await client.start(os.environ['DISCORD_BOT_TOKEN'])
    return 1 if outcome['error'] else 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    raise SystemExit(asyncio.run(provision()))
