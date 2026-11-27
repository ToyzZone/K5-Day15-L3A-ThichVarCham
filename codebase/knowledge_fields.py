"""Chuẩn hóa phạm vi kiến thức để các bài/ngày khác nhau không ghi đè nhau."""
import json
import unicodedata
from datetime import date, datetime, timedelta, timezone

VN_TZ = timezone(timedelta(hours=7))


def scope_key(draft):
    fields = draft.get('pham_vi')
    if not fields or fields.get('loai_cau_hoi') != 'deadline_bai_tap':
        return None
    def norm(value):
        return ' '.join(unicodedata.normalize('NFC', str(value)).casefold().split())
    return json.dumps([norm(fields.get(k, '')) for k in
                       ('server_id', 'lop', 'loai_cau_hoi', 'bai_tap', 'ngay')], ensure_ascii=False)


def validate_fields(raw, server_id):
    if not isinstance(raw, dict):
        raise ValueError('Chưa trích xuất được phạm vi kiến thức.')
    fields = {k: str(raw.get(k) or '').strip() for k in
              ('loai_cau_hoi', 'lop', 'bai_tap', 'ngay', 'gia_tri')}
    fields['server_id'] = str(server_id)
    if not fields['loai_cau_hoi']:
        raise ValueError('Thiếu loại câu hỏi.')
    if fields['ngay']:
        date.fromisoformat(fields['ngay'])
    if fields['loai_cau_hoi'] == 'deadline_bai_tap':
        if not all(fields[k] for k in ('lop', 'bai_tap', 'ngay', 'gia_tri')):
            raise ValueError('Deadline cần lớp, bài tập, ngày áp dụng và giờ cụ thể. Coach hãy trả lời rõ hơn.')
        deadline = datetime.fromisoformat(fields['gia_tri'])
        if deadline.tzinfo is None:
            raise ValueError('Deadline thiếu múi giờ.')
        fields['gia_tri'] = deadline.astimezone(VN_TZ).isoformat()
    return fields
