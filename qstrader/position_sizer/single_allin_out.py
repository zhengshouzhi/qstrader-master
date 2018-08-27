# -*- coding: utf-8 -*-
from math import floor

from .base import AbstractPositionSizer
from qstrader.price_parser import PriceParser


class SingleAllInOut(AbstractPositionSizer):
    """
    做单只标的进出时使用的单个
    """
    def __init__(self):
        self.ticker_weight = 1

    def size_order(self, portfolio, initial_order):
        """
        Size the order to reflect the dollar-weighting of the
        current equity account size based on pre-specified
        ticker weights.
        """
        ticker = initial_order.ticker
        if initial_order.action == "EXIT":
            # Obtain current quantity and liquidate
            cur_quantity = portfolio.positions[ticker].quantity
            if cur_quantity > 0:
                initial_order.action = "SLD"
                initial_order.quantity = cur_quantity
            else:
                pass
                #initial_order.action = "BOT"
                #initial_order.quantity = cur_quantity
        else:
            if initial_order.action == 'BOT':
                weight = self.ticker_weight
                # Determine total portfolio value, work out dollar weight
                # and finally determine integer quantity of shares to purchase
                price = portfolio.price_handler.tickers[ticker]["close"]
                price = PriceParser.display(price)
                equity = PriceParser.display(portfolio.equity)
                dollar_weight = weight * equity
                weighted_quantity = int(floor(dollar_weight / price))
                weighted_quantity = (int(weighted_quantity/100)) * 100
                initial_order.quantity = weighted_quantity
            else:
                cur_quantity = portfolio.positions[ticker].quantity
                initial_order.action = "SLD"
                initial_order.quantity = cur_quantity

        return initial_order
