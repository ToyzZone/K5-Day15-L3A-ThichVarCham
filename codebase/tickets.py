"""Ticket Discord: lưu bản nháp, chỉ tạo kênh sau khi chính người hỏi xác nhận."""
import asyncio
import json

import discord
from knowledge_fields import VN_TZ


class Tickets:
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()
        self.db = bot.store.db
        self.db.execute('''CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT UNIQUE,
            guild_id TEXT, owner_id TEXT, body TEXT, status TEXT DEFAULT 'draft', channel_id TEXT)''')
        self.db.commit()

    def draft(self, message, event, result):
        body = {'question': event['noi_dung'], 'question_at': message.created_at.astimezone(VN_TZ).isoformat(),
                'source_url': message.jump_url, 'summary': (result.get('ticket') or {}).get('tom_tat') or event['noi_dung'],
                'private': result.get('kenh_tra') == 'tin_nhan_rieng'}
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO tickets(source,guild_id,owner_id,body) VALUES (?,?,?,?)',
                            (str(message.id), str(message.guild.id), str(message.author.id), json.dumps(body, ensure_ascii=False)))
        return self.db.execute('SELECT id FROM tickets WHERE source=?', (str(message.id),)).fetchone()[0]

    def get(self, ticket_id):
        row = self.db.execute('SELECT id,guild_id,owner_id,body,status,channel_id FROM tickets WHERE id=?', (ticket_id,)).fetchone()
        if not row:
            raise ValueError('Không tìm thấy ticket.')
        return dict(id=row[0], guild_id=int(row[1]), owner_id=int(row[2]), body=json.loads(row[3]), status=row[4], channel_id=int(row[5]) if row[5] else None)

    def for_channel(self, channel_id):
        row = self.db.execute("SELECT id FROM tickets WHERE channel_id=? AND status='open'", (str(channel_id),)).fetchone()
        return self.get(row[0]) if row else None

    def view(self, ticket_id):
        view = discord.ui.View(timeout=None)
        view.add_item(discord.ui.Button(label='Xác nhận gửi coach', custom_id=f'ticket:confirm:{ticket_id}', style=discord.ButtonStyle.primary))
        view.add_item(discord.ui.Button(label='Hủy', custom_id=f'ticket:cancel:{ticket_id}', style=discord.ButtonStyle.secondary))
        return view

    async def offer(self, message, event, result):
        tid = self.draft(message, event, result)
        text = ('Mình chưa có đủ thông tin để trả lời. Đã soạn bản nháp ticket cho Lab Coach.\n'
                'Bấm **Xác nhận gửi coach** để tạo kênh riêng cho bạn, coach và bot; hoặc **Hủy**.\n'
                'Nội dung cần hỗ trợ: ' + self.get(tid)['body']['summary'])
        destination = message.author if result.get('kenh_tra') == 'tin_nhan_rieng' else message.channel
        if result.get('kenh_tra') == 'tin_nhan_rieng':
            # Các con số riêng vẫn chỉ dùng phần trả lời do code lõi tạo, không đưa ra kênh chung.
            await self.bot.send_text(destination, result.get('noi_dung', '').replace('Bạn bấm xác nhận để gửi nhé.', ''))
        await self.bot.send_text(destination, text)
        await destination.send(f'Bản nháp ticket #{tid}:', view=self.view(tid))
        if destination == message.author:
            await message.reply('Mình đã gửi bản nháp ticket qua tin nhắn riêng.', mention_author=False)

    async def interaction(self, interaction, custom):
        await interaction.response.defer(ephemeral=True)
        try:
            _, action, raw_id = custom.split(':')
            if action not in ('confirm', 'cancel'):
                raise ValueError('Thao tác ticket không hợp lệ.')
            async with self.lock:
                ticket = self.get(int(raw_id))
                if ticket['guild_id'] != self.bot.cfg['DISCORD_GUILD_ID'] or interaction.user.id != ticket['owner_id']:
                    raise ValueError('Chỉ người hỏi gốc được xác nhận hoặc hủy ticket này.')
                if ticket['status'] == 'cancelled':
                    raise ValueError('Ticket này đã hủy.')
                if ticket['status'] == 'open':
                    await interaction.followup.send(f"Ticket đã được tạo: <#{ticket['channel_id']}>.", ephemeral=True)
                    return
                if action == 'cancel':
                    with self.db:
                        self.db.execute("UPDATE tickets SET status='cancelled' WHERE id=?", (ticket['id'],))
                    await interaction.followup.send('Đã hủy bản nháp; chưa tạo kênh hoặc gửi thông báo.', ephemeral=True)
                else:
                    guild = self.bot.get_guild(ticket['guild_id'])
                    if guild is None:
                        raise ValueError('Bot không tìm thấy máy chủ của ticket.')
                    owner = await guild.fetch_member(ticket['owner_id'])
                    if not self.bot.identity(owner):
                        raise ValueError('Bạn chưa có role hợp lệ trong máy chủ.')
                    role = guild.get_role(self.bot.cfg['DISCORD_LAB_COACH_ROLE_ID'])
                    if role is None or role == guild.default_role:
                        raise ValueError('Cấu hình role Lab Coach không hợp lệ.')
                    marker = f'kute-ticket:{ticket["id"]}'
                    # Tìm lại kênh sau restart/lỗi giữa tạo kênh và ghi SQLite, tránh mở trùng.
                    channels = await guild.fetch_channels()
                    channel = next((c for c in channels if isinstance(c, discord.TextChannel) and c.topic == marker), None)
                    if channel is None:
                        channel = await guild.create_text_channel(f'ticket-{ticket["id"]}', topic=marker,
                            overwrites={guild.default_role: discord.PermissionOverwrite(view_channel=False),
                                        owner: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                                        role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                                        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)},
                            reason='Người hỏi xác nhận ticket hỗ trợ')
                    else:
                        allowed = {owner.id, role.id, guild.me.id}
                        if (channel.overwrites_for(guild.default_role).view_channel is not False
                                or any(overwrite.view_channel is True and target.id not in allowed
                                       for target, overwrite in channel.overwrites.items())):
                            raise ValueError('Kênh ticket tìm lại có quyền truy cập không phù hợp. Nhờ quản trị viên kiểm tra trước khi gửi nội dung.')
                    # Ghi nhận kênh ngay; nếu gửi phần giới thiệu thất bại, không mở thêm kênh.
                    with self.db:
                        self.db.execute("UPDATE tickets SET status='open',channel_id=? WHERE id=?", (str(channel.id), ticket['id']))
                    await self.bot.send_text(channel, f"Ticket #{ticket['id']} · Câu hỏi gốc:\n{ticket['body']['question']}\nNguồn: {ticket['body']['source_url']}\nLab Coach trả lời ngay trong kênh này. Kiến thức chung sẽ được soạn thành đề xuất chờ duyệt; thông tin riêng không đưa vào kho.")
                    # Người hỏi đã xác nhận gửi cho coach; chỉ cho phép mention đúng role này.
                    await channel.send(f'{role.mention} có ticket mới cần hỗ trợ.', allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=[role]))
                    await interaction.followup.send(f'Đã tạo ticket riêng: {channel.mention}.', ephemeral=True)
                try:
                    await interaction.message.edit(view=None)
                except discord.HTTPException:
                    pass
        except ValueError as exc:
            await interaction.followup.send(str(exc), ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send('Bot thiếu quyền Quản lý kênh hoặc thiết lập phân quyền. Nhờ quản trị viên cấp quyền rồi bấm Xác nhận lại. Nếu ticket đã tạo, kiểm tra kênh ticket trong server.', ephemeral=True)
        except discord.HTTPException:
            await interaction.followup.send('Discord chưa xử lý được yêu cầu. Hãy bấm Xác nhận lại để kiểm tra ticket đã tạo.', ephemeral=True)
