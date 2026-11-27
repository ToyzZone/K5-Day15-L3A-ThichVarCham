"""Run: python codebase/discord_bot.py. Only for the test server."""
import asyncio
import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path

import discord

import ai
import agent
import tracing
from knowledge_store import KnowledgeStore
from tools import RUNTIME_KB, seed_knowledge
from knowledge_fields import VN_TZ, validate_fields
from coach_console import inspect as inspect_knowledge
from setup_coach_channel import CHANNEL_FILE
from knowledge_board import KnowledgeBoard
from tickets import Tickets

ROOT = Path(__file__).resolve().parent.parent


class CompleteDraft(discord.ui.Modal, title='Hoàn thiện bản nháp để duyệt'):
    def __init__(self, bot, pid, proposal):
        super().__init__(timeout=600)
        self.bot, self.pid, self.previous = bot, pid, proposal
        self.draft = json.loads(json.dumps(proposal['ban_nhap']))
        fields = self.draft.get('pham_vi') or {}
        self.deadline = fields.get('loai_cau_hoi') == 'deadline_bai_tap' or bool(re.search(r'deadline|hạn nộp', self.draft['cau_hoi'], re.I))
        self.question = discord.ui.TextInput(label='Câu hỏi', default=self.draft['cau_hoi'][:1000], max_length=1000)
        self.add_item(self.question)
        if self.deadline:
            self.class_name = discord.ui.TextInput(label='Lớp', default=fields.get('lop', ''), max_length=100)
            self.assignment = discord.ui.TextInput(label='Bài tập', default=fields.get('bai_tap', ''), max_length=100)
            self.day = discord.ui.TextInput(label='Ngày của bài tập (YYYY-MM-DD)', default=fields.get('ngay', ''), max_length=10)
            self.due = discord.ui.TextInput(label='Hạn nộp (YYYY-MM-DD HH:MM, giờ Việt Nam)', placeholder='2026-11-27 10:00', max_length=40)
            for item in (self.class_name, self.assignment, self.day, self.due):
                self.add_item(item)
        else:
            self.answer = discord.ui.TextInput(label='Câu trả lời', default=self.draft['tra_loi'][:2000], style=discord.TextStyle.paragraph, max_length=2000)
            self.add_item(self.answer)

    async def on_submit(self, interaction):
        if not interaction.guild or interaction.guild.id != self.bot.cfg['DISCORD_GUILD_ID'] or interaction.channel_id != self.bot.cfg['DISCORD_REVIEW_CHANNEL_ID'] or not self.bot.coach(interaction.user):
            await interaction.response.send_message('Chỉ Lab Coach trong kênh duyệt được thao tác.', ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        try:
            fields = dict(self.draft.get('pham_vi') or {})
            fields['server_id'] = str(interaction.guild.id)
            self.draft['cau_hoi'] = str(self.question).strip()
            if self.deadline:
                due = datetime.fromisoformat(str(self.due).strip())
                if due.tzinfo is None:
                    due = due.replace(tzinfo=VN_TZ)
                due = due.astimezone(VN_TZ)
                fields.update(loai_cau_hoi='deadline_bai_tap', lop=str(self.class_name).strip(), bai_tap=str(self.assignment).strip(), ngay=str(self.day).strip(), gia_tri=due.isoformat())
                self.draft['tra_loi'] = f"Bài {fields['bai_tap']} lớp {fields['lop']} ngày {fields['ngay']} có hạn nộp lúc {due:%H:%M ngày %d/%m/%Y}."
            else:
                self.draft['tra_loi'] = str(self.answer).strip()
                fields.setdefault('loai_cau_hoi', 'khac')
            self.draft['pham_vi'] = validate_fields(fields, fields['server_id'])
            async with self.bot.lock:
                self.bot.store.revise(self.pid, self.draft, interaction.user.id, self.previous)
            view = discord.ui.View(timeout=None)
            view.add_item(discord.ui.Button(label='Duyệt bản đã hoàn thiện', custom_id=f'kb:override:{self.pid}', style=discord.ButtonStyle.success))
            view.add_item(discord.ui.Button(label='Bỏ qua', custom_id=f'kb:reject:{self.pid}', style=discord.ButtonStyle.secondary))
            # Post the completed draft in the channel so every coach sees it before approving.
            await self.bot.send_text(interaction.channel, f"Bản hoàn thiện đề xuất #{self.pid}\nCâu hỏi: {self.draft['cau_hoi']}\nTrả lời: {self.draft['tra_loi']}\nNguồn: {self.draft['nguon']}\nCảnh báo gốc: {self.previous.get('ly_do', '')}")
            await interaction.channel.send(f'Xác nhận đề xuất #{self.pid}:', view=view)
            await interaction.followup.send('Đã hoàn thiện, chưa cập nhật kho. Hãy đọc bản mới rồi bấm Duyệt.', ephemeral=True)
        except ValueError as exc:
            await interaction.followup.send('Chưa lưu bản nháp: ' + str(exc), ephemeral=True)


def config():
    required = ('DISCORD_BOT_TOKEN', 'DISCORD_GUILD_ID', 'DISCORD_QA_CHANNEL_ID',
                'DISCORD_REVIEW_CHANNEL_ID', 'DISCORD_LEARNER_ROLE_ID', 'DISCORD_LAB_COACH_ROLE_ID')
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise ValueError('Thiếu cấu hình: ' + ', '.join(missing))
    result = {k: os.environ[k] if k.endswith('TOKEN') else int(os.environ[k]) for k in required}
    saved = json.loads(CHANNEL_FILE.read_text(encoding='utf-8')) if CHANNEL_FILE.exists() else {}
    saved_id = saved.get('channel_id', 0) if saved.get('guild_id') == result['DISCORD_GUILD_ID'] else 0
    result['DISCORD_COACH_DATA_CHANNEL_ID'] = int(os.getenv('DISCORD_COACH_DATA_CHANNEL_ID') or saved_id)
    path = ROOT / 'runtime' / 'accounts.json'
    result['accounts'] = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    return result


class Bot(discord.Client):
    def __init__(self, settings):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, allowed_mentions=discord.AllowedMentions.none())
        self.cfg = settings
        self.lock = asyncio.Lock()  # the framework's tracing uses shared state
        seed = seed_knowledge()  # two tables: fixed + course
        self.store = KnowledgeStore(ROOT / 'runtime/knowledge.db', seed)
        self.board = KnowledgeBoard(self, ROOT / 'runtime/knowledge-board.json')
        self.tickets = Tickets(self)

    def coach(self, member):
        return isinstance(member, discord.Member) and any(r.id == self.cfg['DISCORD_LAB_COACH_ROLE_ID'] for r in member.roles)

    def identity(self, member):
        # Account links can be updated while the bot is running.
        path = ROOT / 'runtime' / 'accounts.json'
        try:
            accounts = json.loads(path.read_text(encoding='utf-8-sig'))
            if not isinstance(accounts, dict):
                raise ValueError('Invalid account mapping')
        except FileNotFoundError:
            accounts = {}
        except (OSError, ValueError):
            print('Không đọc được runtime/accounts.json; không dùng hồ sơ mặc định.')
            accounts = {}
        profile = accounts.get(str(member.id))
        if not isinstance(profile, str) or not profile.strip():
            profile = 'unlinked:' + str(member.id)
        if self.coach(member):
            return {'vai_tro': 'lab_coach', 'ma_hoc_vien': profile}
        if not any(r.id == self.cfg['DISCORD_LEARNER_ROLE_ID'] for r in member.roles):
            return None
        # Not linked to a profile yet: general questions work, the portal has no data.
        return {'vai_tro': 'hoc_vien', 'ma_hoc_vien': profile}

    async def on_ready(self):
        print('Kute Pro Max đã trực tuyến. Model:', ai.MODEL_PROVIDER)
        guild = self.get_guild(self.cfg['DISCORD_GUILD_ID'])
        if guild is None:
            print('CẢNH BÁO: Bot không có trong server DISCORD_GUILD_ID đã cấu hình.')
            return
        for key in ('DISCORD_LEARNER_ROLE_ID', 'DISCORD_LAB_COACH_ROLE_ID'):
            role = guild.get_role(self.cfg[key])
            print(key + ':', role.name if role else 'KHÔNG TÌM THẤY — kiểm tra ID vai trò')
        for key in ('DISCORD_QA_CHANNEL_ID', 'DISCORD_REVIEW_CHANNEL_ID', 'DISCORD_COACH_DATA_CHANNEL_ID'):
            channel = guild.get_channel(self.cfg[key])
            if channel is None:
                print(key + ': KHÔNG TÌM THẤY — kiểm tra ID kênh')
                continue
            permissions = channel.permissions_for(guild.me)
            print(key + ': #' + channel.name,
                  '| xem:', permissions.view_channel, '| gửi:', permissions.send_messages,
                  '| lịch sử:', permissions.read_message_history)
        if ai.MODEL_PROVIDER == 'fake':
            print('Chế độ fake chỉ thử kết nối, chưa có trả lời AI thật.')
        await self.board.refresh()

    async def send_text(self, destination, text):
        for start in range(0, len(text), 1900):
            await destination.send(text[start:start + 1900])

    def evaluate(self, event, identity, kb):
        token = RUNTIME_KB.set(kb)
        tracing.begin('discord')
        try:
            return json.loads(agent.answer_event(event, identity)['output'])
        finally:
            tracing.end()
            RUNTIME_KB.reset(token)

    async def on_message(self, message):
        if message.author.bot:
            return
        is_kb = bool(re.match(r'^!kb(?:\s|$)', message.content.strip(), re.I))
        if message.guild and message.guild.id == self.cfg['DISCORD_GUILD_ID'] and message.channel.id == self.cfg.get('DISCORD_COACH_DATA_CHANNEL_ID'):
            if not is_kb:
                return
            if not self.coach(message.author):
                print('Lệnh !kb bị chặn: người gửi chưa có Role ID Lab Coach đã cấu hình.')
                await message.reply('Tài khoản này chưa có role Lab Coach đúng với cấu hình của bot. Hãy gán role Lab Coach hoặc kiểm tra DISCORD_LAB_COACH_ROLE_ID trong .env.', mention_author=False)
                return
            print('Đã nhận !kb trong kênh dữ liệu; bắt đầu đọc SQLite.')
            try:
                if message.content.strip().casefold() in ('!kb', '!kb bang'):
                    url = await self.board.refresh()
                    await message.reply('Bảng kiến thức: ' + url if url else 'Chưa cập nhật được bảng; hãy kiểm tra quyền của bot trong kênh.', mention_author=False)
                    return
                async with self.lock:
                    text = inspect_knowledge(self.store, message.content.strip(), message.guild.id)
                await self.send_text(message.channel, text)
            except ValueError as exc:
                await message.reply(str(exc), mention_author=False)
            except Exception as exc:
                print('Tra dữ liệu coach thất bại:', type(exc).__name__)
                await message.reply('Chưa đọc được dữ liệu, hãy kiểm tra log vận hành.', mention_author=False)
            return
        if is_kb and message.guild and message.guild.id == self.cfg['DISCORD_GUILD_ID']:
            channel_id = self.cfg.get('DISCORD_COACH_DATA_CHANNEL_ID')
            if self.coach(message.author):
                hint = f'Hãy dùng !kb trong kênh <#{channel_id}>.' if channel_id else 'Chưa cấu hình kênh dữ liệu. Hãy chạy setup_coach_channel.py rồi khởi động lại bot.'
                await message.reply(hint, mention_author=False)
            print('Bỏ qua !kb: chưa cấu hình hoặc không đúng kênh dữ liệu.')
            return
        ticket = self.tickets.for_channel(message.channel.id) if message.guild and message.guild.id == self.cfg['DISCORD_GUILD_ID'] else None
        # Nhận câu hỏi trong kênh hỏi đáp hoặc ticket đã xác nhận.
        if not message.guild or message.guild.id != self.cfg['DISCORD_GUILD_ID'] or (message.channel.id != self.cfg['DISCORD_QA_CHANNEL_ID'] and not ticket):
            if message.content.startswith('!hoi'):
                print('Bỏ qua lệnh !hoi: sai server/kênh. Hãy dùng kênh DISCORD_QA_CHANNEL_ID.')
            return
        # A Reply usually adds a mention automatically: do not treat that mention as a coach's question.
        coach_reply = self.coach(message.author) and message.reference and message.reference.message_id and not message.content.startswith('!hoi ')
        has_reply = bool(message.reference and message.reference.message_id)
        is_question = not coach_reply and (self.user in message.mentions or message.content.startswith('!hoi '))
        identity = self.identity(message.author)
        if identity is None:
            if is_question or has_reply:
                print('Từ chối lệnh hỏi: người gửi chưa có Role ID Learner hoặc Lab Coach đã cấu hình.')
                await message.reply('Bạn chưa có vai trò Learner hoặc Lab Coach mà bot được cấu hình nhận diện. Nhờ quản trị viên gán vai trò hoặc kiểm tra ID vai trò trong .env nhé.', mention_author=False)
            return
        event = {'loai': 'cau_hoi', 'kenh': 'hoi-dap', 'noi_dung': message.content, 'nguoi_gui': str(message.author.id), 'ngu_canh': {'server_id': str(message.guild.id), 'thoi_diem_cau_hoi': message.created_at.astimezone(VN_TZ).isoformat(), 'mui_gio': 'Asia/Ho_Chi_Minh'}}
        if ticket and self.coach(message.author) and not message.content.startswith('!hoi '):
            answer_text = await self.tickets.answer_text(message, ticket)
            if answer_text is None:
                return
            if ticket['body']['private']:
                await message.reply('Đã nhận phản hồi cho ticket thông tin riêng. Nội dung ticket này không được đưa vào kho kiến thức chung.', mention_author=False)
                return
            event.update(loai='tra_loi', noi_dung=answer_text, cau_hoi=ticket['body']['question'], link=message.jump_url,
                         coach_chu_dong_tra_loi=True,
                         ngu_canh={'server_id': str(message.guild.id),
                                   'thoi_diem_cau_hoi': ticket['body']['question_at'],
                                   'thoi_diem_tra_loi': message.created_at.astimezone(VN_TZ).isoformat(),
                                   'mui_gio': 'Asia/Ho_Chi_Minh'})
        elif self.coach(message.author) and not is_question:
            if not message.reference or not message.reference.message_id:
                print('Bỏ qua tin coach: chưa dùng Reply vào câu hỏi gốc.')
                if message.content.startswith('!hoc'):
                    await message.reply('Hãy dùng Trả lời (Reply) vào câu hỏi gốc rồi gửi câu trả lời. Không cần lệnh !hoc.', mention_author=False)
                return
            try:
                original = await message.channel.fetch_message(message.reference.message_id)
            except discord.HTTPException:
                await message.reply('Không đọc được câu hỏi gốc. Hãy Reply vào tin còn tồn tại trong kênh này.', mention_author=False)
                return
            if original.author.bot:
                await message.reply('Bạn đang Reply vào tin của bot. Hãy Reply trực tiếp vào câu hỏi gốc của người hỏi.', mention_author=False)
                return
            original_member = original.author
            if not isinstance(original_member, discord.Member):
                try:
                    original_member = await message.guild.fetch_member(original.author.id)
                except discord.HTTPException:
                    await message.reply('Chưa xác minh được người hỏi. Hãy nhờ họ gửi lại câu hỏi trong kênh này.', mention_author=False)
                    return
            if not self.identity(original_member):
                await message.reply('Người hỏi gốc chưa có role Learner hoặc Lab Coach được cấu hình. Hãy kiểm tra role trước.', mention_author=False)
                return
            if self.coach(original_member) and not (original.content.startswith('!hoi ') or self.user in original.mentions):
                await message.reply('Tin gốc là tin của coach, chưa xác định được câu hỏi. Hãy Reply vào câu hỏi bắt đầu bằng !hoi hoặc mention bot.', mention_author=False)
                return
            event.update(loai='tra_loi', cau_hoi=original.content, link=message.jump_url,
                         ngu_canh={'server_id': str(message.guild.id),
                                   'thoi_diem_cau_hoi': original.created_at.astimezone(VN_TZ).isoformat(),
                                   'thoi_diem_tra_loi': message.created_at.astimezone(VN_TZ).isoformat(),
                                   'mui_gio': 'Asia/Ho_Chi_Minh'})
        else:
            if not is_question:
                if has_reply:
                    print('Bỏ qua Reply: người gửi không có Role ID Lab Coach đã cấu hình.')
                    await message.reply('Bot nhận được Reply nhưng tài khoản của bạn chưa có role Lab Coach đúng với DISCORD_LAB_COACH_ROLE_ID. Vì vậy bot chưa tạo đề xuất kiến thức.', mention_author=False)
                return
            if self.coach(message.author):
                # A coach may ask general questions but never borrows a learner's profile.
                identity.setdefault('ma_hoc_vien', 'unlinked:' + str(message.author.id))
            text = message.content.removeprefix('!hoi ')
            for mention in (f'<@{self.user.id}>', f'<@!{self.user.id}>'):
                text = text.replace(mention, '')
            event['noi_dung'] = text.strip()
            if not event['noi_dung']:
                await message.reply('Bạn nhập câu hỏi sau !hoi hoặc sau phần mention bot nhé.', mention_author=False)
                return
        print('Đã nhận:', event['loai'], '| bắt đầu xử lý')
        try:
            async with self.lock:
                result = await asyncio.to_thread(self.evaluate, event, identity, self.store.knowledge())
                if event['loai'] == 'tra_loi':
                    channel = self.get_channel(self.cfg['DISCORD_REVIEW_CHANNEL_ID']) or await self.fetch_channel(self.cfg['DISCORD_REVIEW_CHANNEL_ID'])
                    if channel.guild.id != self.cfg['DISCORD_GUILD_ID']:
                        raise ValueError('Kênh duyệt không thuộc server thử nghiệm.')
                    permissions = channel.permissions_for(message.guild.me)
                    if not permissions.view_channel or not permissions.send_messages:
                        await message.reply('Đã nhận câu trả lời của coach nhưng bot thiếu quyền Xem kênh hoặc Gửi tin nhắn ở kênh duyệt. Hãy cấp quyền rồi Reply lại.', mention_author=False)
                        return
                    pid = self.store.propose(str(message.id), message.created_at.isoformat(), result)
                    if pid is None:
                        return
                    draft = result.get('ban_nhap') or {}
                    text = (f"Đề xuất #{pid}: {result.get('loai')}\nLý do: {result.get('ly_do')}\n"
                            f"Câu hỏi: {draft.get('cau_hoi', event['cau_hoi'])}\n"
                            f"Trả lời: {draft.get('tra_loi', event['noi_dung'])}\nNguồn: {message.jump_url}")
                    fields = draft.get('pham_vi')
                    if fields:
                        text += ('\nLoại: ' + (fields.get('loai_cau_hoi') or 'chưa rõ') + '\nLớp: ' + (fields.get('lop') or 'chưa rõ')
                                 + '\nBài: ' + (fields.get('bai_tap') or '—') + '\nNgày: ' + (fields.get('ngay') or 'chưa rõ')
                                 + '\nGiá trị: ' + (fields.get('gia_tri') or 'cần coach xác nhận'))
                    if result.get('muc_lien_quan'):
                        text += '\nThay mục: ' + result['muc_lien_quan']
                    if result.get('loai') == 'canh_bao':
                        text += '\nThông báo được tra để đối chiếu (coach tự kiểm tra mức liên quan):'
                        for announcement in result.get('thong_bao_doi_chieu', []):
                            text += f"\n{announcement['ma']}: {announcement['noi_dung']} — {announcement['link']}"
                    view = discord.ui.View(timeout=None)
                    if result.get('can_chinh_sua') and draft:
                        view.add_item(discord.ui.Button(label='Hoàn thiện để duyệt', custom_id=f'kb:edit:{pid}', style=discord.ButtonStyle.primary))
                    elif result.get('loai') in ('them', 'sua') and draft:
                        view.add_item(discord.ui.Button(label='Duyệt', custom_id=f'kb:approve:{pid}', style=discord.ButtonStyle.success))
                    elif result.get('can_duyet_ghi_de') and draft:
                        view.add_item(discord.ui.Button(label='Duyệt ghi đè cảnh báo', custom_id=f'kb:override:{pid}', style=discord.ButtonStyle.danger))
                    view.add_item(discord.ui.Button(label='Bỏ qua', custom_id=f'kb:reject:{pid}', style=discord.ButtonStyle.secondary))
                    await self.send_text(channel, text)
                    await channel.send(f'Xử lý đề xuất #{pid} ở trên:', view=view)
                    await message.reply(f'Đã tạo đề xuất #{pid} trong kênh duyệt; chưa đưa vào kho kiến thức.', mention_author=False)
                    await self.board.refresh()
                    return
                text = result.get('noi_dung', 'Chưa có câu trả lời.')
                if result.get('hanh_dong') == 'chuyen_lab_coach':
                    if ticket:
                        # Đã có coach trong ticket, không mở ticket lồng nhau.
                        destination = message.author if result.get('kenh_tra') == 'tin_nhan_rieng' else message.channel
                        await self.send_text(destination, result.get('noi_dung', '').replace('Mình đã soạn một ticket gửi lab coach. Bạn bấm xác nhận để gửi nhé.', 'Câu hỏi này cần Lab Coach hỗ trợ trong ticket hiện tại.'))
                    else:
                        try:
                            await self.tickets.offer(message, event, result)
                        except discord.Forbidden:
                            await message.reply('Không gửi được bản nháp. Nếu cần trả riêng, hãy bật nhận DM rồi hỏi lại; bot chưa mở ticket.', mention_author=False)
                    return
                if result.get('nguon'):
                    text += '\nNguồn: ' + ' · '.join(result['nguon'])
                if result.get('kenh_tra') == 'tin_nhan_rieng':
                    try:
                        await self.send_text(message.author, text)
                        await message.reply('Mình đã gửi câu trả lời qua tin nhắn riêng.', mention_author=False)
                    except discord.Forbidden:
                        await message.reply('Bạn hãy bật nhận tin nhắn riêng từ thành viên máy chủ rồi hỏi lại nhé.', mention_author=False)
                else:
                    await self.send_text(message.channel, text)
        except Exception as exc:
            # Do not print the API response: it may contain private data or keys.
            print('Xử lý thất bại:', type(exc).__name__)
            await message.reply('Chưa xử lý được yêu cầu. Hãy kiểm tra cấu hình model hoặc nhờ người vận hành hỗ trợ.', mention_author=False)

    async def on_interaction(self, interaction):
        data = interaction.data or {}
        custom = data.get('custom_id', '')
        if custom.startswith('ticket:'):
            await self.tickets.interaction(interaction, custom)
            return
        if custom.startswith('kbboard:'):
            if not interaction.guild or interaction.guild.id != self.cfg['DISCORD_GUILD_ID'] or interaction.channel_id != self.cfg.get('DISCORD_COACH_DATA_CHANNEL_ID') or not self.coach(interaction.user):
                await interaction.response.send_message('Chỉ Lab Coach trong kênh dữ liệu được thao tác bảng.', ephemeral=True)
                return
            await interaction.response.defer()
            action = custom.split(':', 1)[1]
            if action in ('prev', 'next', 'refresh'):
                await self.board.refresh(action)
            return
        if not custom.startswith('kb:'):
            return
        if not interaction.guild or interaction.guild.id != self.cfg['DISCORD_GUILD_ID'] or interaction.channel_id != self.cfg['DISCORD_REVIEW_CHANNEL_ID'] or not self.coach(interaction.user):
            await interaction.response.send_message('Chỉ Lab Coach trong kênh duyệt được thao tác.', ephemeral=True)
            return
        if custom.startswith('kb:edit:'):
            try:
                pid = int(custom.split(':')[2])
                proposal = self.store.pending(pid)
                if not proposal.get('ban_nhap'):
                    raise ValueError('Đề xuất cũ chưa giữ bản nháp. Coach hãy Reply lại bằng tin mới.')
                await interaction.response.send_modal(CompleteDraft(self, pid, proposal))
            except ValueError as exc:
                await interaction.response.send_message(str(exc), ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        try:
            _, action, pid = custom.split(':')
            if action not in ('approve', 'reject', 'override'):
                raise ValueError('Thao tác không hợp lệ.')
            async with self.lock:
                self.store.decide(int(pid), interaction.user.id, action in ('approve', 'override'), override=action == 'override')
            await interaction.followup.send('Đã duyệt vào kho.' if action in ('approve', 'override') else 'Đã bỏ qua.', ephemeral=True)
            await interaction.message.edit(view=None)
            await self.board.refresh()
        except ValueError as exc:
            await interaction.followup.send(str(exc), ephemeral=True)


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    settings = config()
    bot = Bot(settings)
    try:
        bot.run(settings['DISCORD_BOT_TOKEN'], log_handler=None)
    finally:
        bot.store.close()


if __name__ == '__main__':
    main()
