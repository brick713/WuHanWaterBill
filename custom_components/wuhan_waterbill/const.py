"""Constants for the Wuhan Water integration."""
from datetime import timedelta
import logging

DOMAIN = "wh_water"
LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(hours=48)
API_URL = "http://wsyy.whwater.com:8223/ws/api/account/paidRecord"

CONF_USER_CODE = "user_code"

ATTR_REST_MONEY = "rest_money"
ATTR_WATER_FEE = "water_fee"
ATTR_DRAIN_FEE = "drain_fee"
ATTR_TOTAL_FEE = "total_fee"
ATTR_USE_WATER = "use_water"
ATTR_LATEST_MONTH = "latest_month"
