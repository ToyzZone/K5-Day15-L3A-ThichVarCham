"""Một tin nhắn bảng kho kiến thức, cập nhật tại chỗ và giữ ID qua restart."""
import asyncio
import json
from datetime import datetime
from pathlib import Path

import discord

from knowledge_fields import VN_TZ
from tools import KHO_RUNTIME, _kho


class KnowledgeBoard:
    def __init__(self, bot, path):
        self.bot = bot
        self.path = Path(path)
        self.lock = asyncio.Lock()
        self.page = 0

    def render(self):
        server = str(self.bot.cfg['DISCORD_GUILD_ID'])
        records = [m for m in self.bot.store.knowledge() if not m.get('pham_vi', {}).get('server_id')
                   or str(m['pham_vi']['server_id']) == server]
        token = KHO_RUNTIME.set(records)
        try:
            items = _kho()
        finally:
            KHO_RUNTIME.reset(token)
        pages = max(1, (len(items) + 7) // 8)
        self.page = max(0, min(self.page, pages - 1))
        widths = (6, 9, 10, 10, 42)
        def cell(value, width):
            text = ' '.join(str(value or '—').replace('`', "'").split())
            return (text[:width-1] + '…' if len(text) > width else text).ljust(width)
        def row(values):
            return ' | '.join(cell(value, width) for value, width in zip(values, widths))
        lines = [row(('Mã', 'Lớp', 'Bài', 'Ngày', 'Câu trả lời')), '-+-'.join('-' * w for w in widths)]
        for item in items[self.page*8:self.page*8+8]:
            scope = item.get('pham_vi') or {}
            lines.append(row((item['ma'], scope.get('lop'), scope.get('bai_tap'), scope.get('ngay'), item['tra_loi'])))
        if not items:
            lines.append('Chưa có kiến thức đang hiệu lực.')
        pending = self.bot.store.db.execute("SELECT count(*) FROM proposals WHERE status='pending'").fetchone()[0]
        embed = discord.Embed(title='Kho kiến thức của bot', color=discord.Color.blue(),
                              description='```text\n' + '\n'.join(lines) + '\n```')
        embed.add_field(name='Đang sử dụng', value=str(len(items)))
        embed.add_field(name='Chờ duyệt', value=str(pending))
        embed.add_field(name='Trang', value=f'{self.page+1}/{pages}')
        embed.set_footer(text='Cập nhật ' + datetime.now(VN_TZ).strftime('%d/%m/%Y %H:%M:%S')
                         + ' · Xem đầy đủ: !kb xem <mã> · Lịch sử: !kb lichsu <mã>')
        view = discord.ui.View(timeout=None)
        for label, action, disabled in [('Trang trước', 'prev', self.page == 0),
                                        ('Trang sau', 'next', self.page == pages-1),
                                        ('Làm mới', 'refresh', False)]:
            view.add_item(discord.ui.Button(label=label, custom_id='kbboard:' + action,
                                           style=discord.ButtonStyle.secondary, disabled=disabled))
        return embed, view

    async def refresh(self, action=None):
        channel_id = self.bot.cfg.get('DISCORD_COACH_DATA_CHANNEL_ID')
        if not channel_id:
            return None
        async with self.lock:
            try:
                channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
                if not isinstance(channel, discord.TextChannel) or channel.guild.id != self.bot.cfg['DISCORD_GUILD_ID']:
                    print('Không cập nhật bảng: kênh dữ liệu không hợp lệ.')
                    return None
                if action == 'next':
                    self.page += 1
                elif action == 'prev':
                    self.page -= 1
                embed, view = self.render()
                state = json.loads(self.path.read_text(encoding='utf-8')) if self.path.exists() else {}
                message = None
                if state.get('channel_id') == channel_id and state.get('guild_id') == channel.guild.id:
                    try:
                        message = await channel.fetch_message(state['message_id'])
                        if message.author.id != self.bot.user.id:
                            message = None
                    except discord.NotFound:
                        pass
                if message:
                    await message.edit(embed=embed, view=view)
                else:
                    message = await channel.send(embed=embed, view=view)
                    self.path.parent.mkdir(parents=True, exist_ok=True)
                    temporary = self.path.with_suffix('.tmp')
                    temporary.write_text(json.dumps({'guild_id': channel.guild.id, 'channel_id': channel_id,
                                                     'message_id': message.id}), encoding='utf-8')
                    temporary.replace(self.path)
                return message.jump_url
            except discord.HTTPException as exc:
                print('Không cập nhật được bảng:', type(exc).__name__, '· kiểm tra quyền Xem kênh, Đọc lịch sử, Gửi tin và Nhúng liên kết.')
                return None
            except (OSError, ValueError, KeyError) as exc:
                print('Không đọc/lưu được trạng thái bảng:', type(exc).__name__)
                return None
