"""Read class timetables (thời khoá biểu) that the training board sends to students as HTML files.

Only the class-level schedule (the GROUPS object of the page) is decoded. The same files carry per-student
lookup tables; this module never reads them, so no student code can reach the API, the model or a reply.

    parse(text)                  one page → {class code: {"ten", "buoi": [session]}}
    load(folder)                 every page in a folder, oldest first
    class_schedule(files, code)  one class across files; a newer file replaces older ones on the days it covers
    cut(schedule, now, name)     the part of a class schedule inside a named window, counted from the asker's "now"
    describe(piece)              the Vietnamese answer text; code writes every date, time and room
"""
import json
import re
from datetime import date, timedelta
from pathlib import Path

WINDOWS = ('hom_nay', 'ngay_mai', 'tuan_nay', 'tuan_sau', 'sap_toi')
WEEKDAYS = ('Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật')
CLASS_CODE = re.compile(r'[A-Z0-9]{1,8}')
_TIME = re.compile(r'\d{2}:\d{2}')


def _session(item, kinds):
    """One raw session → our shape, or None when a field is missing or malformed (the file is outside input)."""
    try:
        day, start, end = date.fromisoformat(item['d']).isoformat(), *item['time']
        rooms = [str(room) for room in item['rooms']]
        if not (_TIME.fullmatch(start) and _TIME.fullmatch(end)):
            return None
        return {'ngay': day, 'ten': str(item['name']), 'loai': kinds.get(item['kind'], str(item['kind'])),
                'phong': rooms, 'gio': [start, end]}
    except (KeyError, TypeError, ValueError):
        return None


def parse(text):
    found = re.search(r'const GROUPS\s*=\s*', text)
    if not found:
        raise ValueError('Không thấy lịch theo lớp trong file thời khoá biểu.')
    # raw_decode stops at the end of the GROUPS object, so nothing after it (student tables) is ever decoded.
    groups, _ = json.JSONDecoder().raw_decode(text, found.end())
    kinds = dict(re.findall(r"(\w+)\s*:\s*'([^']*)'", (re.search(r'const KIND\s*=\s*\{(.*?)\}', text, re.S) or ['', ''])[1]))
    classes = {}
    for code, group in groups.items() if isinstance(groups, dict) else ():
        items = group.get('items') if isinstance(group, dict) else None
        sessions = [s for s in (_session(item, kinds) for item in items or ()) if s]
        if sessions and CLASS_CODE.fullmatch(code):
            classes[code] = {'ten': str(group.get('label') or code), 'buoi': sessions}
    return classes


def _weekend_tail(day):
    """The weekend right after a file's last session day: a file that ends on Saturday also speaks for Sunday."""
    day = date.fromisoformat(day)
    while (day + timedelta(days=1)).weekday() >= 5:
        day += timedelta(days=1)
    return day.isoformat()


def load(folder):
    """Oldest first, by modification time: the order the operator received and saved the files."""
    files = []
    for path in sorted(Path(folder).glob('*.htm*'), key=lambda p: (p.stat().st_mtime, p.name)):
        try:
            classes = parse(path.read_text(encoding='utf-8', errors='replace'))
        except (ValueError, OSError):
            continue
        days = sorted({s['ngay'] for group in classes.values() for s in group['buoi']})
        if days:
            files.append({'nguon': path.name, 'tu': days[0], 'den': days[-1], 'duoi': _weekend_tail(days[-1]), 'lop': classes})
    return files


def class_codes(files):
    return sorted({code for f in files for code in f['lop']})


def _days(first, last):
    first, last = date.fromisoformat(first), date.fromisoformat(last)
    return [(first + timedelta(days=n)).isoformat() for n in range((last - first).days + 1)]


def _owner(files, day):
    """The newest file whose first-to-last session range holds the day; failing that, one whose weekend tail does."""
    inside = [f for f in files if f['tu'] <= day <= f['den']] or [f for f in files if f['den'] < day <= f['duoi']]
    return inside[-1] if inside else None


def class_schedule(files, code):
    """{"lop", "ten", "buoi", "ngay_phu": {day: file that owns it}} or None for a class no file knows.
    A day belongs to one file only (see _owner); a class that file lacks has no basis on that day."""
    known = [f for f in files if code in f['lop']]
    if not known:
        return None
    covered = {}
    for day in sorted({d for f in known for d in _days(f['tu'], f['duoi'])}):
        owner = _owner(files, day)
        if code in owner['lop']:
            covered[day] = owner['nguon']
    sessions = [dict(s, nguon=f['nguon']) for f in known for s in f['lop'][code]['buoi'] if covered.get(s['ngay']) == f['nguon']]
    return {'lop': code, 'ten': known[-1]['lop'][code]['ten'], 'buoi': sorted(sessions, key=lambda s: (s['ngay'], s['gio'])), 'ngay_phu': covered}


def window(now, name):
    """First and last day of a named window. Code does the calendar arithmetic, never the model."""
    today = now.date()
    monday = today - timedelta(days=today.weekday())
    first, length = {'hom_nay': (today, 1), 'ngay_mai': (today + timedelta(days=1), 1), 'tuan_nay': (monday, 7),
                     'tuan_sau': (monday + timedelta(days=7), 7), 'sap_toi': (today, 7)}[name]
    return first, first + timedelta(days=length - 1)


def cut(schedule, now, name):
    """The window's slice of a class schedule. "ngoai_pham_vi": no day of the window is covered by any file."""
    first, last = window(now, name)
    covered = [d for d in _days(first.isoformat(), last.isoformat()) if d in schedule['ngay_phu']]
    return {'lop': schedule['lop'], 'ten': schedule['ten'], 'khoang': name, 'tu': first.isoformat(), 'den': last.isoformat(),
            'ngoai_pham_vi': not covered, 'phu': covered[:1] + covered[-1:],
            'buoi': [s for s in schedule['buoi'] if s['ngay'] in covered],
            'nguon': sorted({schedule['ngay_phu'][d] for d in covered})}


def _label(day):
    day = date.fromisoformat(day)
    return '%s %02d/%02d' % (WEEKDAYS[day.weekday()], day.day, day.month)


def describe(piece):
    span = 'vào ' + _label(piece['tu']) if piece['tu'] == piece['den'] else 'từ %s đến %s' % (_label(piece['tu']), _label(piece['den']))
    if not piece['buoi']:
        text = 'Theo thời khoá biểu, lớp %s không có buổi nào %s.' % (piece['lop'], span)
    else:
        lines = []
        for s in piece['buoi']:
            kind = '' if s['ten'].startswith(s['loai']) else ' (%s)' % s['loai']
            rooms = ('phòng ' + s['phong'][0] if len(s['phong']) == 1 else
                     'một trong các phòng ' + ', '.join(s['phong']) if s['phong'] else 'không ghi phòng')
            lines.append('- %s, %s–%s: %s%s, %s' % (_label(s['ngay']), *s['gio'], s['ten'], kind, rooms))
        text = 'Theo thời khoá biểu, lịch lớp %s %s:\n%s' % (piece['lop'], span, '\n'.join(lines))
        if any(len(s['phong']) > 1 for s in piece['buoi']):
            text += '\nBuổi ghi nhiều phòng là lớp chia theo phòng; thời khoá biểu theo lớp không cho biết bạn ở phòng nào.'
    if piece['phu'] and piece['phu'][-1] != piece['den']:
        text += '\nThời khoá biểu hiện có chỉ ghi tới %s.' % _label(piece['phu'][-1])
    if piece['phu'] and piece['phu'][0] != piece['tu']:
        text += '\nThời khoá biểu hiện có chỉ ghi từ %s.' % _label(piece['phu'][0])
    return text
