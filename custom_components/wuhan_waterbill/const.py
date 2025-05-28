from datetime import timedelta
import logging

DOMAIN = "wh_water"
LOGGER = logging.getLogger(__name__)

API_URL = "http://wsyy.whwater.com:8223/ws/api/account/paidRecord"
SCAN_INTERVAL = timedelta(hours=48)
REQUEST_TIMEOUT = 15

CONF_USER_CODE = "user_code"

ATTR_MAP = {
    "restMoney": "剩余金额",
    "totalFee": "总费用",
    "waterFee": "水费",
    "drainFee": "排水费",
    "useWater": "用水量",
    "payMonth": "缴费月份"
}
