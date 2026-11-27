"""Token-scoped HTTP access; callers cannot select a student through API arguments."""
import json
import urllib.error
import urllib.request

from portal_config import PORTAL_ITEMS, api_url


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
