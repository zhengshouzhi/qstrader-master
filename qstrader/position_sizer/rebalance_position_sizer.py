# -*- coding: utf-8 -*-
from math import floor

from .base import AbstractPositionSizer
from qstrader.price_parser import PriceParser

class LiquidateRebalancePositionSizer(AbstractPositionSizer):
    def __init__(self,ticker_weights):
        self.ticker_weights = ticker_weights

    def size_order(self, portfolio, initial_order):
        ticker =initial_order.ticker
        if initial_order.action == 'EXIT':
            # Obtain current quantity and liquidate
            cur_quantity = portfolio.positions[ticker].quantity
            if cur_quantity > 0:
                initial_order.action = "SLD"
                initial_order.quantity = cur_quantity
            elif cur_quantity < 0:
                initial_order.action = "BOT"
                initial_order.quantity = cur_quantity
            else:
                initial_order.quantity = 0
        else:
            weight = self.ticker_weights[ticker]
            # Determine total portfolio value, work out dollar weight
            # and finally determine integer quantity of shares to purchase
            price = portfolio.price_handler.tickers[ticker]["adj_close"]
            price /= PriceParser.PRICE_MULTIPLIER
            equity = portfolio.equity / PriceParser.PRICE_MULTIPLIER
            dollar_weight = weight * equity
            weighted_quantity = int(floor(dollar_weight / price))
            # Update quantity
            initial_order.quantity = weighted_quantity
        return initial_order