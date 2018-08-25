# -*- coding: utf-8 -*-
import os

import pandas as pd

from ..price_parser import PriceParser
from .base import AbstractBarPriceHandler
from ..event import BarEvent
import tushare as ts
import datetime


class TushareCsvBarPriceHandler(AbstractBarPriceHandler):
    """
        TushareDailyBarPriceHandler is designed to read CSV files of
        TushareFinance daily Open-High-Low-Close-Volume (OHLCV) data
        for each requested financial instrument and stream those to
        the provided events queue as BarEvents.
        """
    def __init__(
        self, csv_dir, events_queue,
        init_tickers,
        start_date=None, end_date=None,cycle = 'D'
    ):
        self.csv_dir = csv_dir
        self.events_queue = events_queue
        self.continue_backtest = True
        self.tickers = {}
        self.tickers_data = {}
        self.tickers_recent_data = {}
        self.start_date = start_date
        self.end_date = end_date
        self.cycle = cycle
        if init_tickers is not None:
            for ticker in init_tickers:
                self.subscribe_ticker(ticker,cycle = self.cycle)

        self.bar_stream = self._merge_sort_ticker_data()

    def _open_ticker_price_csv(self, ticker,cycle):
        """
        Opens the CSV files containing the equities ticks from
        the specified CSV data directory, converting them into
        them into a pandas DataFrame, stored in a dictionary.
        """
        ticker_path = os.path.join(self.csv_dir, ticker+'-'+cycle+'.csv')

        if(not os.path.exists(ticker_path)):
            startdate = str(self.start_date)[:10]
            enddate = str(self.end_date)[:10]
            df = ts.get_k_data(ticker, index=False, start=startdate, end=enddate,ktype=cycle)


            df.to_csv(ticker_path)
        self.tickers_data[ticker] = pd.io.parsers.read_csv(
            ticker_path, header=0, parse_dates=True,
            index_col=1, names=(
                "date", "open", "high", "low",
                "close", "volume","code"
            )
        )

        self.tickers_data[ticker]["Ticker"] = ticker


    def _merge_sort_ticker_data(self):
        df = pd.concat(self.tickers_data.values()).sort_index()
        df['colFromIndex'] = df.index
        df = df.sort_values(by=["colFromIndex", "Ticker"])

        return df.iterrows()

    def subscribe_ticker(self, ticker,cycle):
        """
        Subscribes the price handler to a new ticker symbol.
        """
        if ticker not in self.tickers:
            try:
                self._open_ticker_price_csv(ticker,cycle)
                dft = self.tickers_data[ticker]
                row0 = dft.iloc[0]

                close = PriceParser.parse(row0["close"])

                ticker_prices = {
                    "close": close,
                    "timestamp": dft.index[0]
                }
                self.tickers[ticker] = ticker_prices
            except OSError:
                print(
                    "Could not subscribe ticker %s "
                    "as no data CSV found for pricing." % ticker
                )
        else:
            print(
                "Could not subscribe ticker %s "
                "as is already subscribed." % ticker
            )


    def _create_event(self, index, period, ticker, row):

        open_price = PriceParser.parse(row["open"])
        high_price = PriceParser.parse(row["high"])
        low_price = PriceParser.parse(row["low"])
        close_price = PriceParser.parse(row["close"])
        volume = int(row["volume"])
        bev = BarEvent(
            ticker, index, period, open_price,
            high_price, low_price, close_price,
            volume
        )

        if self.tickers_recent_data.get(ticker, None) is not None:
            self.tickers_recent_data[ticker].append(pd.DataFrame([row]), ignore_index=True)
        else:
            self.tickers_recent_data[ticker] = pd.DataFrame([row])
        return bev

    def _store_event(self, event):
        """
        Store price event for closing price
        """
        ticker = event.ticker

        self.tickers[ticker]["close"] = event.close_price
        self.tickers[ticker]["timestamp"] = event.time

    def stream_next(self):
        """
        Place the next BarEvent onto the event queue.
        """

        try:
            index, row = next(self.bar_stream)

        except StopIteration:
            self.continue_backtest = False
            return
        ticker = row["Ticker"]
        period = 86400  # Seconds in a day
        bev = self._create_event(index, period, ticker, row)
        self._store_event(bev)
        self.events_queue.put(bev)
