from bitmex_bot.settings import settings
from bitmex_bot.utils import log, constants, errors

logger = log.setup_custom_logger('root')

def sanity_check(self):
    """Perform checks before placing orders."""

    # Check if OB is empty - if so, can't quote.
    self.exchange.check_if_orderbook_empty()

    # Ensure market is still open.
    self.exchange.check_market_open()

    self.get_exchange_price()  # => macd_check = npob()

    logger.info("current BITMEX price is {}".format(self.last_price))

    # self.get_exchange_price()
    logger.info("Current Price is {} MACD signal {}".format(self.last_price, self.macd_signal))

    if not self.is_trade:
        if self.macd_signal:
            if self.macd_signal == self.UP:
                logger.info("Buy Trade Signal {}".format(self.last_price))
                logger.info("-----------------------------------------")
                self.is_trade = True
                self.sequence = self.BUY

                # place order
                if not self.initial_order:
                    order = self.place_orders(side=self.BUY, orderType='Market', quantity=self.amount)
                    self.trade_signal = self.macd_signal
                    self.initial_order = True
                    if settings.STOP_PROFIT_FACTOR != "":
                        self.profit_price = order['price'] + (order['price'] * settings.STOP_PROFIT_FACTOR)
                    if settings.STOP_LOSS_FACTOR != "":
                        self.stop_price = order['price'] - (order['price'] * settings.STOP_LOSS_FACTOR)
                    print("Order price {} \tStop Price {} \tProfit Price {} ".
                          format(order['price'], self.stop_price, self.profit_price))
                    sleep(settings.API_REST_INTERVAL)
                    if settings.STOP_LOSS_FACTOR != "":
                        self.place_orders(side=self.SELL, orderType='StopLimit', quantity=self.amount,
                                          price=int(self.stop_price), stopPx=int(self.stop_price) - 5.0)
                        sleep(settings.API_REST_INTERVAL)
                    if settings.STOP_PROFIT_FACTOR != "":
                        self.place_orders(side=self.SELL, orderType='Limit', quantity=self.amount,
                                          price=int(self.profit_price))
                        sleep(settings.API_REST_INTERVAL)
                    self.close_order = True

            elif self.macd_signal == self.DOWN:
                logger.info("Sell Trade Signal {}".format(self.last_price))
                logger.info("-----------------------------------------")
                self.is_trade = True
                self.sequence = self.SELL

                # place order
                if not self.initial_order:
                    order = self.place_orders(side=self.SELL, orderType='Market', quantity=self.amount)
                    self.trade_signal = self.macd_signal
                    self.initial_order = True
                    if settings.STOP_PROFIT_FACTOR != "":
                        self.profit_price = order['price'] - (order['price'] * settings.STOP_PROFIT_FACTOR)
                    if settings.STOP_LOSS_FACTOR != "":
                        self.stop_price = order['price'] + (order['price'] * settings.STOP_LOSS_FACTOR)

                    print("Order price {} \tStop Price {} \tProfit Price {} ".
                          format(order['price'], self.stop_price, self.profit_price))
                    sleep(settings.API_REST_INTERVAL)
                    if settings.STOP_LOSS_FACTOR != "":
                        self.place_orders(side=self.BUY, orderType='StopLimit', quantity=self.amount,
                                          price=int(self.stop_price), stopPx=int(self.stop_price) - 5.0)
                        sleep(settings.API_REST_INTERVAL)
                    if settings.STOP_PROFIT_FACTOR != "":
                        self.place_orders(side=self.BUY, orderType='Limit', quantity=self.amount,
                                          price=int(self.profit_price))
                        sleep(settings.API_REST_INTERVAL)
                    self.close_order = True
                    # set cross margin for the trade

    else:
        if self.macd_signal and self.macd_signal != self.trade_signal and self.trade_signal:
            # TODO close all positions on market price immediately and cancel ALL open orders(including stops).
            self.exchange.close_position()
            # sleep(settings.API_REST_INTERVAL)
            self.exchange.cancel_all_orders()
            self.is_trade = False
            self.close_order = False
            self.initial_order = False
            self.sequence = ""
            self.profit_price = 0
            self.stop_price = 0
            self.trade_signal = False
            sleep(5)

        elif self.close_order and self.exchange.get_position() == 0 and len(self.exchange.get_orders()) == 0:
            self.is_trade = False
            self.close_order = False
            self.initial_order = False
            self.sequence = ""
            self.profit_price = 0
            self.stop_price = 0
            self.trade_signal = False
        else:
            data = self.exchange.get_orders()
            if len(data) == 1:
                if data[0]['ordType'] == "StopLimit" and data[0]['ordStatus'] == 'New':
                    if data[0]['triggered'] == "":
                        self.exchange.cancel_all_orders()
                        self.is_trade = False
                        self.close_order = False
                        self.initial_order = False
                        self.sequence = ""
                        self.profit_price = 0
                        self.stop_price = 0
                        self.trade_signal = False
