"""Persist ticket drafts and create a private Discord channel only after owner confirmation."""
import asyncio
import json
import re
from datetime import datetime, timezone

import discord
from knowledge_fields import VN_TZ

OFFER_LIMIT = 1900  # Bot.send_text cuts longer text into a second message, which would carry the member's text with no framing


def quoted(text, room):
    """A member's text as the bot shows it: every line quoted and cut to room characters, so it never reads as the bot's own words."""
    text = '\n'.join('> ' + line for line in text.splitlines())
    return text if len(text) <= room else text[:room - 1] + '…'


def offer_text(question):
    """The public ticket offer; the learner's question is quoted and the whole offer fits one Discord message."""
    head = ('Mình chưa có đủ thông tin để trả lời. Đã soạn bản nháp ticket cho Lab Coach.\n'
            'Bấm **Xác nhận gửi coach** để tạo kênh riêng cho bạn, coach và bot; hoặc **Hủy**.\n'
            'Câu hỏi sẽ gửi:\n')
    return head + quoted(question, OFFER_LIMIT - len(head))


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
        row = self.db.execute("SELECT id FROM tickets WHERE channel_id=? AND status IN ('opening','open')", (str(channel_id),)).fetchone()
        return self.get(row[0]) if row else None

    def save(self, ticket_id, status, body, channel_id=None):
        """Checkpoint each external step so a repeated confirmation can resume it."""
        with self.db:
            self.db.execute('UPDATE tickets SET status=?,body=?,channel_id=COALESCE(?,channel_id) WHERE id=?',
                            (status, json.dumps(body, ensure_ascii=False), str(channel_id) if channel_id else None, ticket_id))

    async def deliver(self, guild, owner, role, ticket):
        """Resume channel creation, question delivery and coach notification independently."""
        body = dict(ticket['body'])
        body.setdefault('confirmed_at', datetime.now(timezone.utc).isoformat())
        body['delivery_complete'] = False
        self.save(ticket['id'], 'opening', body)
        marker = f'kute-ticket:{ticket["id"]}'
        channels = await guild.fetch_channels()
        channel = next((c for c in channels if isinstance(c, discord.TextChannel)
                        and (c.id == ticket['channel_id'] if ticket['channel_id'] else c.topic == marker)), None)
        if channel is None:
            channel = await guild.create_text_channel(f'ticket-{ticket["id"]}', topic=marker,
                overwrites={guild.default_role: discord.PermissionOverwrite(view_channel=False),
                            owner: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                            role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)},
                reason='Người hỏi xác nhận ticket hỗ trợ')
        allowed = {owner.id, role.id, guild.me.id}
        if (channel.topic != marker
                or channel.overwrites_for(guild.default_role).view_channel is not False
                or any(overwrite.view_channel is True and target.id not in allowed
                       for target, overwrite in channel.overwrites.items())
                or not channel.permissions_for(owner).view_channel
                or not channel.permissions_for(role).view_channel):
            raise ValueError('Kênh ticket có quyền truy cập không phù hợp. Nhờ quản trị viên kiểm tra trước khi gửi nội dung.')
        permissions = channel.permissions_for(guild.me)
        if not (permissions.view_channel and permissions.send_messages and permissions.read_message_history):
            raise ValueError('Bot cần quyền Xem kênh, Gửi tin và Đọc lịch sử trong ticket. Cấp quyền rồi bấm Xác nhận lại.')
        self.save(ticket['id'], 'opening', body, channel.id)

        # Recover messages sent just before a process crash, before their IDs were saved.
        prefix = f"Ticket #{ticket['id']} · Câu hỏi gốc:\n"
        notification = f"{role.mention} có ticket #{ticket['id']} mới cần hỗ trợ."
        recent = [m async for m in channel.history(limit=50)]
        opening = next((m for m in recent if m.author.id == self.bot.user.id and m.content.startswith(prefix)), None)
        if body.get('question_message_id') and opening is None:
            try:
                opening = await channel.fetch_message(int(body['question_message_id']))
                if opening.author.id != self.bot.user.id or not opening.content.startswith(prefix):
                    raise ValueError('Tin câu hỏi gốc không khớp ticket; cần người vận hành kiểm tra.')
            except discord.NotFound:
                pass
        if opening is None:
            opening = await channel.send(f"{prefix}{quoted(body['question'], 1300)}\nNguồn: {body['source_url']}\nLab Coach dùng !traloi <nội dung> hoặc Reply vào chính tin câu hỏi này để tạo đề xuất. Chat thường không được học; kiến thức chỉ lưu sau khi duyệt.")
        body['question_message_id'] = opening.id
        self.save(ticket['id'], 'opening', body, channel.id)
        notice = next((m for m in recent if m.author.id == self.bot.user.id and m.content == notification), None)
        if not body.get('notification_message_id'):
            if notice is None:
                notice = await channel.send(notification, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=[role]))
            body['notification_message_id'] = notice.id
        body['delivery_complete'] = True
        self.save(ticket['id'], 'open', body, channel.id)
        return channel

    def view(self, ticket_id):
        view = discord.ui.View(timeout=None)
        view.add_item(discord.ui.Button(label='Xác nhận gửi coach', custom_id=f'ticket:confirm:{ticket_id}', style=discord.ButtonStyle.primary))
        view.add_item(discord.ui.Button(label='Hủy', custom_id=f'ticket:cancel:{ticket_id}', style=discord.ButtonStyle.secondary))
        return view

    async def answer_text(self, message, ticket):
        """Accept explicit coach answers only; casual chat never calls the model."""
        text = message.content.strip()
        command = re.match(r'^!traloi(?:\s+|$)', text, re.I)
        if command:
            text = text[command.end():].strip()
            if not text:
                await message.reply('Dùng !traloi <câu trả lời cho câu hỏi gốc>.', mention_author=False)
                return None
        else:
            reference = message.reference
            if not reference or not reference.message_id:
                return None
            anchor_id = ticket['body'].get('question_message_id')
            if anchor_id:
                if reference.message_id != int(anchor_id):
                    return None
            else:
                # Legacy tickets did not persist the opening message ID.
                try:
                    original = await message.channel.fetch_message(reference.message_id)
                except discord.HTTPException:
                    return None
                if original.author.id != self.bot.user.id or not original.content.startswith(f"Ticket #{ticket['id']} · Câu hỏi gốc:\n"):
                    return None
        normalized = ' '.join(re.findall(r'\w+', text.casefold()))
        if not any(c.isalnum() for c in text) or normalized in {'k', 'ok', 'oke', 'okay', 'alo', 'hi', 'hello', 'haha', 'hihi', 'hú', 'hú hú', 'ừ', 'uh', 'dạ', 'vâng'}:
            return None
        return text

    async def offer(self, message, event, result):
        tid = self.draft(message, event, result)
        ticket = self.get(tid)
        if ticket['status'] == 'cancelled':
            await message.reply('Bản nháp cho câu hỏi này đã hủy. Hãy gửi câu hỏi mới nếu bạn cần hỗ trợ.', mention_author=False)
            return
        text = offer_text(ticket['body']['question'])
        destination = message.author if result.get('kenh_tra') == 'tin_nhan_rieng' else message.channel
        if result.get('kenh_tra') == 'tin_nhan_rieng':
            # Private values remain in DMs; never fall back to the public channel.
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
                if interaction.guild and interaction.guild.id != ticket['guild_id']:
                    raise ValueError('Ticket không thuộc máy chủ này.')
                if ticket['status'] == 'cancelled':
                    raise ValueError('Ticket này đã hủy.')
                if ticket['status'] == 'open' and ticket['body'].get('delivery_complete', True):
                    await interaction.followup.send(f"Ticket đã được tạo: <#{ticket['channel_id']}>.", ephemeral=True)
                    return
                if action == 'cancel':
                    if ticket['status'] == 'opening' or ticket['channel_id']:
                        raise ValueError('Bạn đã xác nhận và ticket đang được tạo. Bấm Xác nhận lại để hoàn tất, không thể hủy như bản nháp chưa gửi.')
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
                    channel = await self.deliver(guild, owner, role, ticket)
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
