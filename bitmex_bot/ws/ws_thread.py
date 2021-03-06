import sys
import websocket
import threading
import traceback
import time
from datetime import datetime
import ssl
from time import sleep
import json
import decimal
import logging
# from bitmex_bot import bitmex_bot
# from . import nprob
from bitmex_bot.settings import settings
from bitmex_bot.auth.APIKeyAuth import generate_nonce, generate_signature
from bitmex_bot.utils.log import setup_custom_logger
from bitmex_bot.utils.math import toNearest
from future.utils import iteritems
from future.standard_library import hooks
with hooks():  # Python 2/3 compat
    from urllib.parse import urlparse, urlunparse

# global last_time

# Connects to BitMEX websocket for streaming realtime data.
# The Marketmaker still interacts with this as if it were a REST Endpoint, but now it can get
# much more realtime data without heavily polling the API.
#
# The Websocket offers a bunch of data as raw properties right on the object.
# On connect, it synchronously asks for a push of all this data then returns.
# Right after, the MM can start using its data. It will be updated in realtime, so the MM can
# poll as often as it wants.
class BitMEXWebsocket():

    # global buy1Prc, buy1Qty, buy2Prc, buy2Qty
    # global sell1Prc, sell1Qty, sell2Prc, sell2Qty
    # global last_tr

    # Don't grow a table larger than this amount. Helps cap memory usage.
    MAX_TABLE_LEN = 200

    def __init__(self):

        global cgubun, cvolume, timestamp, last_time, count
        cgubun='n'
        cvolume=0
        count = 0
        last_time = 0

        self.logger = logging.getLogger('root')
        # self.np = nprob.Nprob()
        self.__reset()

    def __del__(self):
        self.exit()

    def connect(self, endpoint="", symbol="XBTUSD", shouldAuth=False):
        '''Connect to the websocket and initialize data stores.'''

        self.logger.debug("Connecting WebSocket.")
        self.symbol = symbol
        self.shouldAuth = shouldAuth

        # We can subscribe right in the connection querystring, so let's build that.
        # Subscribe to all pertinent endpoints
        subscriptions = [sub + ':' + symbol for sub in ["trade", "orderBook10"]]
        subscriptions += ["instrument"]  # We want all of them
        if self.shouldAuth:
            subscriptions += [sub + ':' + symbol for sub in ["order", "execution"]]
            subscriptions += ["margin", "position"]

        # Get WS URL and connect.
        urlParts = list(urlparse(endpoint))
        urlParts[0] = urlParts[0].replace('http', 'ws')
        urlParts[2] = "/realtime?subscribe=" + ",".join(subscriptions)
        wsURL = urlunparse(urlParts)
        self.logger.info("Connecting to %s" % wsURL)
        self.__connect(wsURL)
        self.logger.info('Connected to WS. Waiting for data images, this may take a moment...')

        # Connected. Wait for partials
        # self.__wait_for_symbol(symbol)
        if self.shouldAuth:
            self.__wait_for_account()
        self.logger.info('Got all market data. Starting.')

    #
    # Data methods
    #
    def get_instrument(self, symbol):
        instruments = self.data['instrument']
        matchingInstruments = [i for i in instruments if i['symbol'] == symbol]
        if len(matchingInstruments) == 0:
            raise Exception("Unable to find instrument or index with symbol: " + symbol)
        instrument = matchingInstruments[0]
        # Turn the 'tickSize' into 'tickLog' for use in rounding
        # http://stackoverflow.com/a/6190291/832202
        instrument['tickLog'] = decimal.Decimal(str(instrument['tickSize'])).as_tuple().exponent * -1
        return instrument

    def get_ticker(self, symbol):
        '''Return a ticker object. Generated from instrument.'''

        instrument = self.get_instrument(symbol)

        # If this is an index, we have to get the data from the last trade.
        if instrument['symbol'][0] == '.':
            ticker = {}
            ticker['mid'] = ticker['buy'] = ticker['sell'] = ticker['last'] = instrument['markPrice']
        # Normal instrument
        else:
            bid = instrument['bidPrice'] or instrument['lastPrice']
            ask = instrument['askPrice'] or instrument['lastPrice']
            ticker = {
                "last": instrument['lastPrice'],
                "buy": bid,
                "sell": ask,
                "mid": (bid + ask) / 2
            }

        # The instrument has a tickSize. Use it to round values.
        # print ticker
        return {k: toNearest(float(v or 0), instrument['tickSize']) for k, v in iteritems(ticker)}

    def orderbook(self):

        # global buy1Prc, buy1Qty, buy2Prc, buy2Qty
        # global sell1Prc, sell1Qty, sell2Prc, sell2Qty
        # global last_tr
        #
        # orderbook={"buy1Prc": buy1Prc,"buy1Qty": buy1Qty,"buy2Prc": buy2Prc,"buy2Qty": buy2Qty,
        #            "sell1Prc": sell1Prc, "sell1Qty": sell1Qty, "sell2Prc": sell2Prc, "sell2Qty": sell2Qty}

        return self.data['orderBook10']

    def funds(self):
        return self.data['margin'][0]

    def market_depth(self, symbol):
        raise NotImplementedError('orderBook is not subscribed; use askPrice and bidPrice on instrument')
        # return self.data['orderBook25'][0]

    def open_orders(self, clOrdIDPrefix):
        orders = self.data['order']
        # Filter to only open orders (leavesQty > 0) and those that we actually placed
        return [o for o in orders if str(o['clOrdID']).startswith(clOrdIDPrefix) and o['leavesQty'] > 0]

    def position(self, symbol):
        positions = self.data['position']
        pos = [p for p in positions if p['symbol'] == symbol]
        if len(pos) == 0:
            # No position found; stub it
            return {'avgCostPrice': 0, 'avgEntryPrice': 0, 'currentQty': 0, 'symbol': symbol}
        return pos[0]

    def recent_trades(self):
        global cgubun, cvolume, timestamp, count, last_time

        cvolume_sum=cvolume
        cgubun = "Buy"
        if cvolume<0:
            cgubun="Sell"
        if cvolume==0:
            cgubun="non"

        # timestamp
        timestamp_u = self.data['trade'][-1]['timestamp'].encode("UTF-8")
        year = timestamp_u[0:4]
        month = timestamp_u[5:7]
        date = timestamp_u[8:10]
        sec = timestamp_u[11:19]
        mil = timestamp_u[20:23]
        time_str = date + '.' + month + '.' + year + ' ' + sec + '.' + mil
        dt_obj = datetime.strptime(time_str, '%d.%m.%Y %H:%M:%S.%f')
        timestamp = (time.mktime(dt_obj.timetuple()) * 1000 + int(mil))/1000
        if count==0:
            count=1
        # mt = (time.time()-last_time)/count
        mt = (timestamp-last_time)/count
        # print timestamp, last_time, mt, count
        last_time = timestamp
        last_trade=self.data['trade']+[cgubun]+[cvolume_sum]+[mt]+[count]

        cvolume=0
        count=0

        return last_trade

    #
    # Lifecycle methods
    #
    def error(self, err):
        self._error = err
        self.logger.error(err)
        self.exit()

    def exit(self):
        self.exited = True
        self.ws.close()

    #
    # Private methods
    #

    def __connect(self, wsURL):
        '''Connect to the websocket in a thread.'''
        self.logger.debug("Starting thread")

        ssl_defaults = ssl.get_default_verify_paths()
        sslopt_ca_certs = {'ca_certs': ssl_defaults.cafile}
        self.ws = websocket.WebSocketApp(wsURL,
                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error,
                                         header=self.__get_auth()
                                         )

        setup_custom_logger('websocket', log_level=settings.LOG_LEVEL)
        self.wst = threading.Thread(target=lambda: self.ws.run_forever(sslopt=sslopt_ca_certs))
        self.wst.daemon = True
        self.wst.start()
        self.logger.info("Started thread")

        # Wait for connect before continuing
        conn_timeout = 5
        while (not self.ws.sock or not self.ws.sock.connected) and conn_timeout and not self._error:
            sleep(1)
            conn_timeout -= 1

        if not conn_timeout or self._error:
            self.logger.error("Couldn't connect to WS! Exiting.")
            self.exit()
            sys.exit(1)

    def __get_auth(self):
        '''Return auth headers. Will use API Keys if present in settings.'''

        if self.shouldAuth is False:
            return []

        self.logger.info("Authenticating with API Key.")
        # To auth to the WS using an API key, we generate a signature of a nonce and
        # the WS API endpoint.
        nonce = generate_nonce()
        return [
            "api-nonce: " + str(nonce),
            "api-signature: " + generate_signature(settings.API_SECRET, 'GET', '/realtime', nonce, ''),
            "api-key:" + settings.API_KEY
        ]

    def __wait_for_account(self):
        '''On subscribe, this data will come down. Wait for it.'''
        # Wait for the keys to show up from the ws
        while not {'margin', 'position', 'order'} <= set(self.data):
            sleep(0.1)

    def __wait_for_symbol(self, symbol):
        '''On subscribe, this data will come down. Wait for it.'''
        while not {'instrument', 'trade', 'quote'} <= set(self.data):
            sleep(0.1)

    def __send_command(self, command, args):
        '''Send a raw command.'''
        self.ws.send(json.dumps({"op": command, "args": args or []}))

    def __on_message(self, ws, message):

        global cgubun, cvolume, timestamp, count, last_time

        '''Handler for parsing WS messages.'''
        message = json.loads(message)
        # self.logger.debug(json.dumps(message))

        table = message['table'] if 'table' in message else None
        action = message['action'] if 'action' in message else None
        # print table, action

        try:
            if 'subscribe' in message:
                if message['success']:
                    self.logger.debug("Subscribed to %s." % message['subscribe'])
                else:
                    self.error("Unable to subscribe to %s. Error: \"%s\" Please check and restart." %
                               (message['request']['args'][0], message['error']))
            elif 'status' in message:
                if message['status'] == 400:
                    self.error(message['error'])
                if message['status'] == 401:
                    self.error("API Key incorrect, please check and restart.")
            elif action:

                if table not in self.data:
                    self.data[table] = []

                if table not in self.keys:
                    self.keys[table] = []

                # print(self.data['orderBook10'])
                # print(self.data.keys())
                # print("----")

                # There are four possible actions from the WS:
                # 'partial' - full table image
                # 'insert'  - new row
                # 'update'  - update row
                # 'delete'  - delete row
                if action == 'partial':
                    # self.logger.debug("%s: partial" % table)
                    self.data[table] += message['data']
                    # print 'partial', message['data']
                    # Keys are communicated on partials to let you know how to uniquely identify
                    # an item. We use it for updates.
                    self.keys[table] = message['keys']
                elif action == 'insert':
                    self.logger.debug('%s: inserting %s' % (table, message['data']))
                    self.data[table] += message['data']

                    # price, cgubun, cvolume, volume, time_str, timestamp
                    if table=="trade":
                        if 1==1:  # bot_out_house mode
                            for i in range(len(message['data'])):

                                ins_cvolume=message['data'][i]['size']
                                if message['data'][i]['side'] == "Sell":
                                    ins_cvolume=ins_cvolume*-1
                                cvolume+=ins_cvolume
                                # last_time=time.time()
                            # price = message['data'][i]['price']
                            count+=1

                        if 1==0:   # ws_in_house mode
                            ##############################################
                            ###                  Main                 ####
                            ##############################################

                            # print message['data']
                            price = message['data'][0]['price']
                            cgubun_sum = message['data'][0]['side']
                            cvolume_sum = message['data'][0]['size']
                            volume = message['data'][0]['grossValue']
                            # timestamp
                            timestamp_u = message['data'][0]['timestamp'].encode("UTF-8")
                            year = timestamp_u[0:4]
                            month = timestamp_u[5:7]
                            date = timestamp_u[8:10]
                            sec = timestamp_u[11:19]
                            mil = timestamp_u[20:23]
                            time_str = date + '.' + month + '.' + year + ' ' + sec + '.' + mil
                            dt_obj = datetime.strptime(time_str, '%d.%m.%Y %H:%M:%S.%f')
                            timestamp = time.mktime(dt_obj.timetuple()) * 1000 + int(mil)
                            print (price, cgubun_sum, cvolume_sum,volume, timestamp)

                            lblSqty2v = self.data['orderBook10'][0]['asks'][1][1]
                            lblShoga2v = self.data['orderBook10'][0]['asks'][1][0]
                            lblSqty1v = self.data['orderBook10'][0]['asks'][0][1]
                            lblShoga1v = self.data['orderBook10'][0]['asks'][0][0]
                            lblBqty1v = self.data['orderBook10'][0]['bids'][0][1]
                            lblBhoga1v = self.data['orderBook10'][0]['bids'][0][0]
                            lblBqty2v = self.data['orderBook10'][0]['bids'][1][1]
                            lblBhoga2v = self.data['orderBook10'][0]['bids'][1][0]
                            self.np.nprob(price, timestamp, cgubun_sum, cvolume_sum, volume, lblSqty2v, lblShoga2v, lblSqty1v, lblShoga1v, lblBqty1v, lblBhoga1v, lblBqty2v, lblBhoga2v)

                    # Limit the max length of the table to avoid excessive memory usage.
                    # Don't trim orders because we'll lose valuable state if we do.
                    if table != 'order' and len(self.data[table]) > BitMEXWebsocket.MAX_TABLE_LEN:
                        self.data[table] = self.data[table][(BitMEXWebsocket.MAX_TABLE_LEN // 2):]

                elif action == 'update':
                    # self.logger.debug('%s: updating %s' % (table, message['data']))
                    # Locate the item in the collection and update it.

                    if table=='orderBook10':
                        buy1Prc = message['data'][0]['bids'][0][0]
                        buy1Qty = message['data'][0]['bids'][0][1]
                        buy2Prc = message['data'][0]['bids'][1][0]
                        buy2Qty = message['data'][0]['bids'][1][1]

                        sell1Prc = message['data'][0]['asks'][0][0]
                        sell1Qty = message['data'][0]['asks'][0][1]
                        sell2Prc = message['data'][0]['asks'][1][0]
                        sell2Qty = message['data'][0]['asks'][1][1]

                    # if table=="orderBookL2":
                    #     if message['data'][0]['side']=="Buy":
                    #         buy = message['data'][0]['size']
                    #     if message['data'][0]['side']=="Sell":
                    #         sell = message['data'][0]['size']
                    #     print 'buy :', buy
                    #     print 'sell :', sell

                    for updateData in message['data']:
                        item = findItemByKeys(self.keys[table], self.data[table], updateData)
                        if not item:
                            continue  # No item found to update. Could happen before push

                        # Log executions
                        if table == 'order':
                            is_canceled = 'ordStatus' in updateData and updateData['ordStatus'] == 'Canceled'
                            if 'cumQty' in updateData and not is_canceled:
                                contExecuted = updateData['cumQty'] - item['cumQty']
                                if contExecuted > 0:
                                    instrument = self.get_instrument(item['symbol'])
                                    self.logger.info("Execution: %s %d Contracts of %s at %.*f" %
                                             (item['side'], contExecuted, item['symbol'],
                                              instrument['tickLog'], item['price']))

                        # Update this item.
                        item.update(updateData)

                        # Remove canceled / filled orders
                        if table == 'order' and item['leavesQty'] <= 0:
                            self.data[table].remove(item)

                elif action == 'delete':
                    # self.logger.debug('%s: deleting %s' % (table, message['data']))
                    # Locate the item in the collection and remove it.
                    for deleteData in message['data']:
                        item = findItemByKeys(self.keys[table], self.data[table], deleteData)
                        self.data[table].remove(item)
                else:
                    raise Exception("Unknown action: %s" % action)
        except:
            self.logger.error(traceback.format_exc())

    def __on_open(self, ws):
        self.logger.debug("Websocket Opened.")

    def __on_close(self, ws):
        self.logger.info('Websocket Closed')
        self.exit()

    def __on_error(self, ws, error):
        if not self.exited:
            self.error(error)

    def __reset(self):
        self.data = {}
        self.keys = {}
        self.exited = False
        self._error = None


def findItemByKeys(keys, table, matchData):
    for item in table:
        matched = True
        for key in keys:
            if item[key] != matchData[key]:
                matched = False
        if matched:
            return item

if __name__ == "__main__":
    # create console handler and set level to debug
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    ws = BitMEXWebsocket()
    ws.logger = logger
    ws.connect("https://www.bitmex.com/api/v1")
    while(ws.ws.sock.connected):
        sleep(1)

