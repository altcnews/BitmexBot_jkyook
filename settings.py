from os.path import join
import logging

BASE_URL_LIVE = "https://www.bitmex.com/api/v1/"

BASE_URL_TESTING = "https://testnet.bitmex.com/api/v1/"

# The BitMEX API requires permanent API keys. Go to https://testnet.bitmex.com/api/apiKeys to fill these out.
# for TESTING mode
# https://www.bitmex.com/api/apiKeys for LIVE mode
API_KEY = "3_9ozC36G73tuqLP9pEaUg9b"
API_SECRET = "ZwXjgm5bGiQlZBiTgEQRDt7BTQQrHeWPSMnla0JkztydScoG"


# Instrument to market make on BitMEX.
SYMBOL = "XBTUSD"

# tick interval used for mcad data
TICK_INTERVAL = '1m'

STOP_LOSS_FACTOR = 0.007
STOP_PROFIT_FACTOR = 0.01

# There is two mode one is TESTING and other is LIVE
#MODE = "TESTING"
MODE = "LIVE"

INTERVAL = 0.005

DRY_RUN = True

RELIST_INTERVAL = 0.01

CHECK_POSITION_LIMITS = True
MIN_POSITION = -500
MAX_POSITION = 500

LOOP_INTERVAL = 5

# Wait times between orders / errors
API_REST_INTERVAL = 1
API_ERROR_INTERVAL = 10


# Available levels: logging.(DEBUG|INFO|WARN|ERROR)
LOG_LEVEL = logging.INFO
ORDERID_PREFIX = "sam_bitmex_"

# If any of these files (and this file) changes, reload the bot.
WATCHED_FILES = [join("bitmex_bot", f) for f in ["bitmex_bot.py", "bitmex_historical.py", __file__]]


#======================================

########################################################################################################################
# Connection/Auth
########################################################################################################################

# API URL.
BASE_URL = "https://testnet.bitmex.com/api/v1/"
# BASE_URL = "https://www.bitmex.com/api/v1/" # Once you're ready, uncomment this.

# The BitMEX API requires permanent API keys. Go to https://testnet.bitmex.com/api/apiKeys to fill these out.
########################################################################################################################
########################################################################################################################
########################################################################################################################
if MODE == "TESTING":
    API_KEY = "pCc8eZGCheuKP8VGVrD4LwKm"
    API_SECRET = "qzW8kcwJGiHu6dx4HRxy7gtBjiwpzFppHzSlB4NlH_EUL4hq"
if MODE == "LIVE":
    API_KEY = "6gNIGCxr_rKYj-Lh5nhlqH2a"
    API_SECRET = "ZLNid7vLcQjt4VFyG0ZVbLdYFt2TT9kOB5U92bK9jrHqum-g"



########################################################################################################################
########################################################################################################################
########################################################################################################################

########################################################################################################################
# Target
########################################################################################################################

# Instrument to market make on BitMEX.
SYMBOL = "XBTUSD"


########################################################################################################################
# Order Size & Spread
########################################################################################################################

# How many pairs of buy/sell orders to keep open
ORDER_PAIRS = 6

# ORDER_START_SIZE will be the number of contracts submitted on level 1
# Number of contracts from level 1 to ORDER_PAIRS - 1 will follow the function
# [ORDER_START_SIZE + ORDER_STEP_SIZE (Level -1)]
ORDER_START_SIZE = 100
ORDER_STEP_SIZE = 100

# Distance between successive orders, as a percentage (example: 0.005 for 0.5%)
INTERVAL = 0.005

# Minimum spread to maintain, in percent, between asks & bids
MIN_SPREAD = 0.01

# If True, market-maker will place orders just inside the existing spread and work the interval % outwards,
# rather than starting in the middle and killing potentially profitable spreads.
MAINTAIN_SPREADS = True

# This number defines far much the price of an existing order can be from a desired order before it is amended.
# This is useful for avoiding unnecessary calls and maintaining your ratelimits.
#
# Further information:
# Each order is designed to be (INTERVAL*n)% away from the spread.
# If the spread changes and the order has moved outside its bound defined as
# abs((desired_order['price'] / order['price']) - 1) > settings.RELIST_INTERVAL)
# it will be resubmitted.
#
# 0.01 == 1%
RELIST_INTERVAL = 0.01


########################################################################################################################
# Trading Behavior
########################################################################################################################

# Position limits - set to True to activate. Values are in contracts.
# If you exceed a position limit, the bot will log and stop quoting that side.
CHECK_POSITION_LIMITS = False
MIN_POSITION = -500
MAX_POSITION = 500

# If True, will only send orders that rest in the book (ExecInst: ParticipateDoNotInitiate).
# Use to guarantee a maker rebate.
# However -- orders that would have matched immediately will instead cancel, and you may end up with
# unexpected delta. Be careful.
POST_ONLY = False

########################################################################################################################
# Misc Behavior, Technicals
########################################################################################################################

# If true, don't set up any orders, just say what we would do
# DRY_RUN = True
DRY_RUN = False

# How often to re-check and replace orders.
# Generally, it's safe to make this short because we're fetching from websockets. But if too many
# order amend/replaces are done, you may hit a ratelimit. If so, email BitMEX if you feel you need a higher limit.
LOOP_INTERVAL = 0.5

# Wait times between orders / errors
API_REST_INTERVAL = 1
API_ERROR_INTERVAL = 10

# If we're doing a dry run, use these numbers for BTC balances
DRY_BTC = 50

# Available levels: logging.(DEBUG|INFO|WARN|ERROR)
LOG_LEVEL = logging.INFO

# To uniquely identify orders placed by this bot, the bot sends a ClOrdID (Client order ID) that is attached
# to each order so its source can be identified. This keeps the market maker from cancelling orders that are
# manually placed, or orders placed by another bot.
#
# If you are running multiple bots on the same symbol, give them unique ORDERID_PREFIXes - otherwise they will
# cancel each others' orders.
# Max length is 13 characters.
ORDERID_PREFIX = "mm_bitmex_"

# If any of these files (and this file) changes, reload the bot.
WATCHED_FILES = [join("bitmex_bot", f) for f in ["bitmex_bot.py", "bitmex_historical.py", __file__]]


########################################################################################################################
# BitMEX Portfolio
########################################################################################################################

# Specify the contracts that you hold. These will be used in portfolio calculations.
CONTRACTS = ['XBTUSD']

# order amount for bitmex in USD
POSITION = 10