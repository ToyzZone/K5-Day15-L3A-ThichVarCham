"""Chạy: python codebase/discord_bot.py. Chỉ dùng trong server thử nghiệm."""
import asyncio
import json
import os
import sys
from pathlib import Path

import discord

import ai
import agent
import tracing
from knowledge_store import KnowledgeStore
from tools import KHO_RUNTIME
from knowledge_fields import VN_TZ

ROOT = Path(__file__).resolve().parent.parent


def config():
    required = ('DISCORD_BOT_TOKEN', 'DISCORD_GUILD_ID', 'DISCORD_QA_CHANNEL_ID',
                'DISCORD_REVIEW_CHANNEL_ID', 'DISCORD_LEARNER_ROLE_ID', 'DISCORD_LAB_COACH_ROLE_ID')
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise ValueError('Thiếu cấu hình: ' + ', '.join(missing))
    result = {k: os.environ[k] if k.endswith('TOKEN') else int(os.environ[k]) for k in required}
    path = ROOT / 'runtime' / 'accounts.json'
    result['accounts'] = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    return result


class Bot(discord.Client):
    def __init__(self, settings):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, allowed_mentions=discord.AllowedMentions.none())
        self.cfg = settings
        self.lock = asyncio.Lock()  # tracing của khung dùng trạng thái chung
        seed = json.loads((ROOT / 'data/kho_kien_thuc.json').read_text(encoding='utf-8'))
        self.store = KnowledgeStore(ROOT / 'runtime/knowledge.db', seed)

    def coach(self, member):
        return isinstance(member, discord.Member) and any(r.id == self.cfg['DISCORD_LAB_COACH_ROLE_ID'] for r in member.roles)

    def identity(self, member):
        if self.coach(member):
            return {'vai_tro': 'lab_coach'}
        if not any(r.id == self.cfg['DISCORD_LEARNER_ROLE_ID'] for r in member.roles):
            return None
        # Chưa liên kết hồ sơ: hỏi kiến thức chung được, portal không có dữ liệu.
        return {'vai_tro': 'hoc_vien', 'ma_hoc_vien': self.cfg['accounts'].get(str(member.id), 'unlinked:' + str(member.id))}

    async def on_ready(self):
        print('Kute Pro Max đã trực tuyến. Model:', ai.MODEL_PROVIDER)
        guild = self.get_guild(self.cfg['DISCORD_GUILD_ID'])
        if guild is None:
            print('CẢNH BÁO: Bot không có trong server DISCORD_GUILD_ID đã cấu hình.')
            return
        for key in ('DISCORD_LEARNER_ROLE_ID', 'DISCORD_LAB_COACH_ROLE_ID'):
            role = guild.get_role(self.cfg[key])
            print(key + ':', role.name if role else 'KHÔNG TÌM THẤY — kiểm tra ID vai trò')
        for key in ('DISCORD_QA_CHANNEL_ID', 'DISCORD_REVIEW_CHANNEL_ID'):
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

    async def send_text(self, destination, text):
        for start in range(0, len(text), 1900):
            await destination.send(text[start:start + 1900])

    def evaluate(self, event, identity, kb):
        token = KHO_RUNTIME.set(kb)
        tracing.begin('discord')
        try:
            return json.loads(agent.answer_event(event, identity)['output'])
        finally:
            tracing.end()
            KHO_RUNTIME.reset(token)

    async def on_message(self, message):
        if message.author.bot:
            return
        # DM không có role; chỉ nhận câu hỏi từ server được cấu hình.
        if not message.guild or message.guild.id != self.cfg['DISCORD_GUILD_ID'] or message.channel.id != self.cfg['DISCORD_QA_CHANNEL_ID']:
            if message.content.startswith('!hoi'):
                print('Bỏ qua lệnh !hoi: sai server/kênh. Hãy dùng kênh DISCORD_QA_CHANNEL_ID.')
            return
        # Reply thường có mention tự động: không coi mention đó là câu hỏi của coach.
        coach_reply = self.coach(message.author) and message.reference and message.reference.message_id and not message.content.startswith('!hoi ')
        is_question = not coach_reply and (self.user in message.mentions or message.content.startswith('!hoi '))
        identity = self.identity(message.author)
        if identity is None:
            if is_question:
                print('Từ chối lệnh hỏi: người gửi chưa có Role ID Learner hoặc Lab Coach đã cấu hình.')
                await message.reply('Bạn chưa có vai trò Learner hoặc Lab Coach mà bot được cấu hình nhận diện. Nhờ quản trị viên gán vai trò hoặc kiểm tra ID vai trò trong .env nhé.', mention_author=False)
            return
        event = {'loai': 'cau_hoi', 'kenh': 'hoi-dap', 'noi_dung': message.content, 'nguoi_gui': str(message.author.id), 'ngu_canh': {'server_id': str(message.guild.id), 'thoi_diem_cau_hoi': message.created_at.astimezone(VN_TZ).isoformat(), 'mui_gio': 'Asia/Ho_Chi_Minh'}}
        if self.coach(message.author) and not is_question:
            if not message.reference or not message.reference.message_id:
                return
            try:
                original = await message.channel.fetch_message(message.reference.message_id)
            except discord.HTTPException:
                await message.reply('Không đọc được câu hỏi gốc. Hãy Reply vào tin còn tồn tại trong kênh này.', mention_author=False)
                return
            if original.author.bot or not isinstance(original.author, discord.Member) or not self.identity(original.author) or self.coach(original.author):
                return
            event.update(loai='tra_loi', cau_hoi=original.content, link=message.jump_url,
                         ngu_canh={'server_id': str(message.guild.id),
                                   'thoi_diem_cau_hoi': original.created_at.astimezone(VN_TZ).isoformat(),
                                   'thoi_diem_tra_loi': message.created_at.astimezone(VN_TZ).isoformat(),
                                   'mui_gio': 'Asia/Ho_Chi_Minh'})
        else:
            if not is_question:
                return
            if self.coach(message.author):
                # Coach được hỏi kiến thức chung, không mượn hồ sơ của learner.
                identity = dict(identity, ma_hoc_vien='unlinked:' + str(message.author.id))
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
                    pid = self.store.propose(str(message.id), message.created_at.isoformat(), result)
                    if pid is None:
                        return
                    draft = result.get('ban_nhap') or {}
                    text = (f"Đề xuất #{pid}: {result.get('loai')}\nLý do: {result.get('ly_do')}\n"
                            f"Câu hỏi: {draft.get('cau_hoi', event['cau_hoi'])}\n"
                            f"Trả lời: {draft.get('tra_loi', event['noi_dung'])}\nNguồn: {message.jump_url}")
                    fields = draft.get('pham_vi')
                    if fields:
                        text += ('\nLoại: ' + fields['loai_cau_hoi'] + '\nLớp: ' + (fields['lop'] or 'chung')
                                 + '\nBài: ' + (fields['bai_tap'] or '—') + '\nNgày: ' + (fields['ngay'] or 'không giới hạn')
                                 + '\nGiá trị: ' + fields['gia_tri'])
                    if result.get('muc_lien_quan'):
                        text += '\nThay mục: ' + result['muc_lien_quan']
                    view = discord.ui.View(timeout=None)
                    if result.get('loai') in ('them', 'sua') and draft:
                        view.add_item(discord.ui.Button(label='Duyệt', custom_id=f'kb:approve:{pid}', style=discord.ButtonStyle.success))
                    view.add_item(discord.ui.Button(label='Bỏ qua', custom_id=f'kb:reject:{pid}', style=discord.ButtonStyle.secondary))
                    await self.send_text(channel, text)
                    await channel.send(f'Xử lý đề xuất #{pid} ở trên:', view=view)
                    await message.reply(f'Đã tạo đề xuất #{pid} trong kênh duyệt; chưa đưa vào kho kiến thức.', mention_author=False)
                    return
                text = result.get('noi_dung', 'Chưa có câu trả lời.')
                if result.get('hanh_dong') == 'chuyen_lab_coach':
                    # Adapter chưa có chức năng mở ticket/xác nhận, tránh chỉ dẫn nút không tồn tại.
                    text = ('Mình chưa có đủ thông tin để trả lời. Cần Lab Coach hỗ trợ. '
                            'Lab Coach hãy dùng Trả lời (Reply) trực tiếp vào câu hỏi gốc của learner; '
                            'mình sẽ tạo đề xuất kiến thức chờ duyệt. Chưa gửi ticket hoặc thông báo cho coach.')
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
            # Không in nội dung phản hồi API vì có thể chứa dữ liệu riêng/key.
            print('Xử lý thất bại:', type(exc).__name__)
            await message.reply('Chưa xử lý được yêu cầu. Hãy kiểm tra cấu hình model hoặc nhờ người vận hành hỗ trợ.', mention_author=False)

    async def on_interaction(self, interaction):
        data = interaction.data or {}
        custom = data.get('custom_id', '')
        if not custom.startswith('kb:'):
            return
        if not interaction.guild or interaction.guild.id != self.cfg['DISCORD_GUILD_ID'] or interaction.channel_id != self.cfg['DISCORD_REVIEW_CHANNEL_ID'] or not self.coach(interaction.user):
            await interaction.response.send_message('Chỉ Lab Coach trong kênh duyệt được thao tác.', ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        try:
            _, action, pid = custom.split(':')
            if action not in ('approve', 'reject'):
                raise ValueError('Thao tác không hợp lệ.')
            async with self.lock:
                self.store.decide(int(pid), interaction.user.id, action == 'approve')
            await interaction.followup.send('Đã duyệt vào kho.' if action == 'approve' else 'Đã bỏ qua.', ephemeral=True)
            await interaction.message.edit(view=None)
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
