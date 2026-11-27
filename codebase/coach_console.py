"""Lệnh xem kho và đề xuất cho coach; không đọc secrets, portal hoặc thực thi SQL nhập từ chat."""
import json
from collections import Counter

from knowledge_fields import scope_key
from tools import KHO_RUNTIME, _kho


HELP = """Tra dữ liệu bot (chỉ xem, không gọi AI):
!kb hoặc !kb bang — mở/làm mới bảng kiến thức cố định
!kb help — thống kê và hướng dẫn
!kb ds [trang] — kiến thức đang dùng, 10 mục/trang
!kb tim <từ khóa> — tìm trong toàn bộ kho, gồm lịch sử
!kb xem <mã> — nội dung, phạm vi, nguồn và thông tin duyệt
!kb lichsu <mã> — các phiên bản cùng phạm vi/chuỗi ghi đè
!kb dexuat [trang] — đề xuất chờ duyệt
!kb dexuat <#mã> — xem chi tiết, ví dụ !kb dexuat #7
Thao tác duyệt vẫn thực hiện trong kênh duyệt kiến thức."""


def page(items, number, render):
    number = int(number or '1')
    total = max(1, (len(items) + 9) // 10)
    if number < 1 or number > total:
        raise ValueError(f'Trang hợp lệ: 1–{total}.')
    return f'Trang {number}/{total} · {len(items)} mục\n' + ('\n'.join(render(m) for m in items[(number-1)*10:number*10]) or 'Chưa có dữ liệu.')


def detail(item):
    fields = item.get('pham_vi') or {}
    lines = [f"{item['ma']} · {item.get('bang', '')} · {item['trang_thai']}",
             'Câu hỏi: ' + item['cau_hoi'], 'Trả lời: ' + item['tra_loi'],
             'Nguồn: ' + item['nguon']]
    for label, value in [('Phạm vi', ' · '.join(str(fields.get(k) or '—') for k in ('lop', 'bai_tap', 'ngay', 'gia_tri')) if fields else ''),
                         ('Ghi đè', item.get('ghi_de')), ('Người duyệt', item.get('nguoi_duyet')),
                         ('Ngày duyệt', item.get('ngay_duyet')), ('Thời điểm tin nguồn', item.get('source_created_at')),
                         ('Cảnh báo được duyệt ghi đè', item.get('canh_bao_khi_duyet'))]:
        if value:
            lines.append(label + ': ' + str(value))
    return '\n'.join(lines)


def inspect(store, command, server_id):
    records = [m for m in store.knowledge() if not m.get('pham_vi', {}).get('server_id')
               or str(m['pham_vi']['server_id']) == str(server_id)]
    token = KHO_RUNTIME.set(records)
    try:
        active = _kho()
    finally:
        KHO_RUNTIME.reset(token)
    parts = command.strip().split(maxsplit=2)
    verb = parts[1].casefold() if len(parts) > 1 else ''
    arg = parts[2].strip() if len(parts) > 2 else ''
    summary = lambda m: f"{m['ma']} · {m['trang_thai']} · {m['cau_hoi'][:180]}"
    if not verb or verb == 'help':
        counts = Counter(m['trang_thai'] for m in records)
        pending = store.db.execute("SELECT count(*) FROM proposals WHERE status='pending'").fetchone()[0]
        return f"Kho đang trả lời: {len(active)} mục · lịch sử lỗi thời: {counts['loi_thoi']} · đề xuất chờ duyệt: {pending}\n\n" + HELP
    if verb == 'ds':
        return page(active, arg, summary)
    if verb == 'tim':
        if not arg:
            raise ValueError('Dùng !kb tim <từ khóa>.')
        terms = arg.casefold().split()
        matches = [m for m in records if all(t in (m['cau_hoi']+' '+m['tra_loi']+' '+json.dumps(m.get('pham_vi', {}), ensure_ascii=False)).casefold() for t in terms)]
        return page(matches, '1', summary) + ('\nHãy nhập từ khóa cụ thể hơn để thu hẹp kết quả.' if len(matches) > 10 else '')
    if verb in ('xem', 'lichsu'):
        item = next((m for m in records if m['ma'].casefold() == arg.casefold()), None)
        if not item:
            raise ValueError('Không tìm thấy mã mục trong kho.')
        if verb == 'xem':
            visible = any(m['ma'] == item['ma'] for m in active)
            return detail(item) + ('\nĐang được dùng để trả lời.' if visible else '\nKhông dùng để trả lời (lỗi thời hoặc bị mục khác ghi đè).')
        key = scope_key(item)
        related = {item['ma']}
        while True:
            before = len(related)
            for m in records:
                if m['ma'] in related or m.get('ghi_de') in related or (key and scope_key(m) == key):
                    related.add(m['ma'])
                    if m.get('ghi_de'):
                        related.add(m['ghi_de'])
            if len(related) == before:
                break
        history = [m for m in records if m['ma'] in related]
        return '\n\n'.join(detail(m) for m in history[-20:]) + ('\nChỉ hiển thị 20 phiên bản cuối.' if len(history) > 20 else '')
    if verb == 'dexuat':
        if arg.startswith('#'):
            row = store.db.execute('SELECT id,status,created,body FROM proposals WHERE id=?', (int(arg[1:]),)).fetchone()
            if not row:
                raise ValueError('Không tìm thấy đề xuất.')
            body = json.loads(row[3])
            draft = body.get('ban_nhap') or {}
            return (f"Đề xuất #{row[0]} · {row[1]} · {body.get('loai')}\nNgày nguồn: {row[2]}\n"
                    f"Lý do: {body.get('ly_do', '')}\nMục liên quan: {body.get('muc_lien_quan') or '—'}\n"
                    f"Câu hỏi: {draft.get('cau_hoi', '—')}\nTrả lời: {draft.get('tra_loi', '—')}\nNguồn: {draft.get('nguon', '—')}")
        rows = store.db.execute("SELECT id,body FROM proposals WHERE status='pending' ORDER BY id DESC").fetchall()
        return page(rows, arg, lambda row: f"#{row[0]} · {json.loads(row[1]).get('loai')} · {(json.loads(row[1]).get('ban_nhap') or {}).get('cau_hoi', 'Chưa có bản nháp')[:180]}")
    return HELP
