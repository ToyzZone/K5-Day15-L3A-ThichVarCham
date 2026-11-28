"""Token-scoped HTTP access; callers cannot select a student through API arguments."""
import json
import urllib.error
import urllib.request

from portal_config import PORTAL_ITEMS, api_url
from tkb import CLASS_CODE


def read_item(token, item):
    if item not in PORTAL_ITEMS:
        return {'loi': 'Mục portal không hợp lệ.'}
    request = urllib.request.Request(api_url() + '/api/me/' + item,
                                     headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        return {'loi': 'Portal từ chối token.' if exc.code == 401 else 'Portal không xử lý được yêu cầu.'}
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return {'loi': 'Không kết nối được portal giả; kiểm tra server API.'}
    if not isinstance(result, dict) or result.get('muc') != item or 'du_lieu' not in result:
        return {'loi': 'Portal trả dữ liệu không hợp lệ.'}
    return {'muc': item, 'du_lieu': result['du_lieu']}


def read_timetable(token, code):
    """Timetable of a class; an empty code means the class of the token owner. The code only ever names a class."""
    if code and not CLASS_CODE.fullmatch(code):
        return {'loi': 'Mã lớp không hợp lệ.'}
    request = urllib.request.Request(api_url() + ('/api/tkb/' + code if code else '/api/me/tkb'),
                                     headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            body = json.load(exc)
        except ValueError:
            body = {}
        if exc.code == 404 and isinstance(body, dict) and isinstance(body.get('loi'), str):
            classes = [c for c in body.get('lop_co') or [] if isinstance(c, str) and CLASS_CODE.fullmatch(c)]
            return {'loi': body['loi'], 'lop_co': classes}
        return {'loi': 'Portal từ chối token.' if exc.code == 401 else 'Portal không xử lý được yêu cầu.'}
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return {'loi': 'Không kết nối được portal giả; kiểm tra server API.'}
    if not isinstance(result, dict) or not isinstance(result.get('buoi'), list) or not isinstance(result.get('ngay_phu'), dict):
        return {'loi': 'Portal trả dữ liệu không hợp lệ.'}
    return result
