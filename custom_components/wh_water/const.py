from datetime import timedelta
import logging

DOMAIN = "wh_water"
LOGGER = logging.getLogger(__name__)

API_URL = "http://wsyy.whwater.com:8223/ws/api/account/paidRecord"
SCAN_INTERVAL = timedelta(hours=48)  # 每48小时更新一次
REQUEST_TIMEOUT = 20  # 超时时间延长至20秒

CONF_USER_CODE = "user_code"

ATTR_MAP = {
    "restMoney": "剩余金额",
    "totalFee": "总费用",
    "waterFee": "水费",
    "drainFee": "排水费",
    "useWater": "用水量",
    "payMonth": "缴费月份",
    "calculateDate": "计算日期",
    "paymentMode": "缴费方式"
}
