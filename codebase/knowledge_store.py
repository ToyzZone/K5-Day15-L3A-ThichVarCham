"""SQLite riêng cho Discord; không thay dữ liệu nền của eval."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from knowledge_fields import scope_key, validate_fields


class KnowledgeStore:
    def __init__(self, path, seed):
        self.seed = {m['ma']: m for m in seed}
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY, body TEXT)")
        self.db.execute("CREATE TABLE IF NOT EXISTS proposals (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT UNIQUE, created TEXT, body TEXT, status TEXT DEFAULT 'pending')")
        self.db.execute("INSERT OR IGNORE INTO state VALUES (1, ?)", (json.dumps(seed, ensure_ascii=False),))
        self.db.commit()

    def knowledge(self):
        records = json.loads(self.db.execute("SELECT body FROM state WHERE id=1").fetchone()[0])
        # Tương thích database trước khi tách hai bảng, không làm mất mục coach đã duyệt.
        for item in records:
            default = 'theo_khoa' if item['ma'].startswith('D') else 'co_dinh'
            item.setdefault('bang', self.seed.get(item['ma'], {}).get('bang', default))
        existing = {m['ma'] for m in records}
        records.extend(dict(m) for code, m in self.seed.items() if code not in existing)
        return records

    def propose(self, source, created, body):
        with self.db:
            cur = self.db.execute("INSERT OR IGNORE INTO proposals(source,created,body) VALUES (?,?,?)", (source, created, json.dumps(body, ensure_ascii=False)))
        return cur.lastrowid if cur.rowcount else None

    def pending(self, proposal_id):
        row = self.db.execute('SELECT body,status FROM proposals WHERE id=?', (proposal_id,)).fetchone()
        if not row or row[1] != 'pending':
            raise ValueError('Đề xuất không tồn tại hoặc đã xử lý.')
        return json.loads(row[0])

    def revise(self, proposal_id, draft, reviewer, previous):
        with self.db:
            self.db.execute('UPDATE state SET body=body WHERE id=1')
            proposal = self.pending(proposal_id)
            if proposal != previous:
                raise ValueError('Đề xuất đã thay đổi; hãy mở lại biểu mẫu.')
            if not all(draft.get(k) for k in ('cau_hoi', 'tra_loi', 'nguon')):
                raise ValueError('Cần đủ câu hỏi, câu trả lời và nguồn.')
            fields = draft.get('pham_vi') or {}
            draft['pham_vi'] = validate_fields(fields, fields.get('server_id', ''))
            proposal.update(ban_nhap=draft, can_chinh_sua=False, can_duyet_ghi_de=True,
                            nguoi_chinh_sua=str(reviewer))
            self.db.execute('UPDATE proposals SET body=? WHERE id=?',
                            (json.dumps(proposal, ensure_ascii=False), proposal_id))
            return proposal

    def decide(self, proposal_id, reviewer, approve, override=False):
        with self.db:
            self.db.execute("UPDATE state SET body=body WHERE id=1")  # khóa ghi trước khi đọc
            row = self.db.execute("SELECT created,body,status FROM proposals WHERE id=?", (proposal_id,)).fetchone()
            if not row or row[2] != 'pending':
                raise ValueError("Đề xuất không tồn tại hoặc đã xử lý.")
            created, body, _ = row
            p = json.loads(body)
            if approve:
                if p.get('can_chinh_sua'):
                    raise ValueError('Cần hoàn thiện thông tin trong bản nháp trước khi duyệt.')
                warning_allowed = p.get('loai') == 'canh_bao' and p.get('can_duyet_ghi_de') and override
                if (p.get('loai') not in ('them', 'sua') and not warning_allowed) or not p.get('ban_nhap'):
                    raise ValueError("Cảnh báo/bỏ qua không thể đưa vào kho.")
                draft = p['ban_nhap']
                if not all(draft.get(k) for k in ('cau_hoi', 'tra_loi', 'nguon')):
                    raise ValueError("Bản nháp thiếu câu hỏi, câu trả lời hoặc nguồn.")
                kb = self.knowledge()
                if draft.get('pham_vi'):
                    validate_fields(draft['pham_vi'], draft['pham_vi']['server_id'])
                key = scope_key(draft)
                same_scope = [m for m in kb if m['trang_thai'] == 'hieu_luc'
                              and key and scope_key(m) == key]
                target = next((m for m in kb if m['ma'] == p.get('muc_lien_quan') and m['trang_thai'] == 'hieu_luc'), None)
                if target and key and scope_key(target) and scope_key(target) != key:
                    raise ValueError('Phạm vi bản nháp khác mục cần sửa. Hãy tạo lại đề xuất.')
                if same_scope:
                    target = max(same_scope, key=lambda m: m.get('source_created_at', ''))
                if p['loai'] == 'sua' and target is None:
                    raise ValueError("Mục cũ đã thay đổi; hãy tạo lại đề xuất từ câu trả lời mới.")
                if target and target.get('source_created_at') and datetime.fromisoformat(target['source_created_at']) >= datetime.fromisoformat(created):
                    raise ValueError("Không thể dùng tin cũ ghi đè tin mới.")
                # Preserve fixed records; supersede only learned/course versions.
                for old in same_scope or ([target] if target else []):
                    if old.get('bang') == 'theo_khoa':
                        old['trang_thai'] = 'loi_thoi'
                parent = (target.get('ghi_de') or target['ma']) if target else None
                kb.append(dict(draft, bang='theo_khoa', ghi_de=parent,
                               ma='D' + str(proposal_id), trang_thai='hieu_luc',
                               nguoi_duyet=str(reviewer), ngay_duyet=datetime.now(timezone.utc).isoformat(),
                               source_created_at=created, duyet_ghi_de=bool(warning_allowed),
                               canh_bao_khi_duyet=p.get('ly_do') if warning_allowed else None))
                self.db.execute("UPDATE state SET body=? WHERE id=1", (json.dumps(kb, ensure_ascii=False),))
            self.db.execute("UPDATE proposals SET status=? WHERE id=?", ('approved' if approve else 'rejected', proposal_id))

    def close(self):
        self.db.close()
