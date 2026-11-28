"""Put the demo runtime state back to its base before every rehearsal, the backup recording and the real demo.

Usage: python codebase/reset_demo.py   (resets <repo>/runtime with tools.seed_knowledge(); no flags)

sqlite_sequence is never touched: old Discord messages still carry buttons and channel markers with
proposal and ticket ids, so ids keep counting up and an old button can never act on a new proposal.
"""
import json
import sqlite3
import sys
from contextlib import closing
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIMEOUT = 10  # seconds to wait while the running bot holds a write lock


def _connect(path):
    return closing(sqlite3.connect(path, timeout=TIMEOUT))


def reset(runtime_dir, seed):
    """Back up knowledge.db (and group-gia.db if present), then reset them. Returns the backup directory."""
    runtime_dir = Path(runtime_dir)
    kb, group = runtime_dir / 'knowledge.db', runtime_dir / 'group-gia.db'
    if not kb.exists():  # checked before connect(), which would create an empty file
        raise FileNotFoundError('Không có %s: chưa có gì để đặt lại.' % kb)
    dbs = [p for p in (kb, group) if p.exists()]
    backup = runtime_dir / datetime.now().strftime('backup-%Y%m%d-%H%M%S')
    backup.mkdir()  # no exist_ok: a second reset in the same second fails instead of overwriting the backup
    for path in dbs:
        with _connect(path) as src, _connect(backup / path.name) as dst:
            src.backup(dst)
    # ponytail: a bot write landing between backup and reset is lost; fine while nobody uses the demo during a reset
    with _connect(kb) as db, db:
        db.execute('UPDATE state SET body=? WHERE id=1', (json.dumps(seed, ensure_ascii=False),))
        db.execute('DELETE FROM proposals')
        if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='tickets'").fetchone():
            db.execute('DELETE FROM tickets')
    if group in dbs:
        with _connect(group) as db, db:  # GroupStore re-seeds its posts on the next start when posts is empty
            for table in ('comments', 'posts', 'public_codes'):
                db.execute('DELETE FROM ' + table)
    return backup


def main(runtime_dir=ROOT / 'runtime'):
    import tools  # here, so reset() itself needs only the standard library
    seed = tools.seed_knowledge()
    try:
        backup = reset(runtime_dir, seed)
    except (OSError, sqlite3.Error) as exc:
        sys.exit('Không đặt lại được: %s' % exc)
    print('Đã đặt lại dữ liệu demo về trạng thái gốc.')
    print('Bản sao lưu: %s' % backup)
    print('Kho kiến thức hiện có %d mục.' % len(seed))
    print('Nhắc: 1) Khởi động lại bot để bot nạp lại kho và xử lý các bài mẫu của group giả.')
    print('      2) Xoá các tin cũ của bot trong kênh duyệt.')


if __name__ == '__main__':
    main()
