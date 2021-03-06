# -*- coding: utf-8 -*-
import calendar

from qstrader.strategy.base import AbstractStrategy
from qstrader.event import (SignalEvent, EventType)
import click
from qstrader import settings
from qstrader.compat import queue
from qstrader.price_handler.tushare_data_csv_bar import TushareDailyCsvBarPriceHandler
from qstrader.strategy.monthly_liquidate_rebalance_strategy import  MonthlyLiquidateRebalanceStrategy
#from qstrader.strategy import Strategies, DisplayStrategy
from qstrader.position_sizer.rebalance import LiquidateRebalancePositionSizer
from qstrader.risk_manager.example import ExampleRiskManager
from qstrader.portfolio_handler import PortfolioHandler
from qstrader.compliance.example import ExampleCompliance
from qstrader.execution_handler.ib_simulated import IBSimulatedExecutionHandler
from qstrader.statistics.tearsheet import TearsheetStatistics
from qstrader.trading_session.backtest import Backtest
from qstrader.price_parser import PriceParser

class MonthlyLiquidateRebalanceStrategy(AbstractStrategy):

    def __init__(self,tickers,event_queue):
        self.tickers = tickers
        self.evert_queue = event_queue
        self.tickers_invested = self._create_invested_list()

    def _end_of_month(self,cur_time):
        cur_day = cur_time.day
        end_day = calendar.monthrange(cur_time.year,cur_time.month)[1]
        return cur_day == end_day

    def _create_invested_list(self):
        tickers_invested = {ticker:False for ticker in self.tickers}
        return tickers_invested

    def calculate_signals(self, event):
        if(
            event.type in [EventType.BAR, EventType.TICK] and
            self._end_of_month(event.time)
        ):
            ticker = event.ticker
            if self.tickers_invested[ticker]:
                liquidate_signal = SignalEvent(ticker,"EXIT")
                self.evert_queue.put(liquidate_signal)
            long_signal = SignalEvent(ticker,"BOT")
            self.evert_queue.put(long_signal)
            self.tickers_invested[ticker] = True

def run(config, testing, tickers, filename):

    # Set up variables needed for backtest
    events_queue = queue.Queue()
    csv_dir = config.CSV_DATA_DIR
    initial_equity = PriceParser.parse(500000.00)

    # Use Yahoo Daily Price Handler
    price_handler = TushareDailyCsvBarPriceHandler(
        csv_dir, events_queue, tickers
    )

    # Use the monthly liquidate and rebalance strategy
    strategy = MonthlyLiquidateRebalanceStrategy(tickers, events_queue)
    #strategy = Strategies(strategy, DisplayStrategy())

    # Use the liquidate and rebalance position sizer
    # with prespecified ticker weights
    ticker_weights = {
        "SPY": 0.6,
        "AGG": 0.4,
    }
    position_sizer = LiquidateRebalancePositionSizer(ticker_weights)

    # Use an example Risk Manager
    risk_manager = ExampleRiskManager()

    # Use the default Portfolio Handler
    portfolio_handler = PortfolioHandler(
        initial_equity, events_queue, price_handler,
        position_sizer, risk_manager
    )

    # Use the ExampleCompliance component
    compliance = ExampleCompliance(config)

    # Use a simulated IB Execution Handler
    execution_handler = IBSimulatedExecutionHandler(
        events_queue, price_handler, compliance
    )

    # Use the default Statistics
    title = ["US Equities/Bonds 60/40 ETF Strategy"]
    benchmark = "SPY"
    statistics = TearsheetStatistics(
        config, portfolio_handler, title, benchmark
    )

    # Set up the backtest
    backtest = Backtest(
        price_handler, strategy,
        portfolio_handler, execution_handler,
        position_sizer, risk_manager,
        statistics, initial_equity
    )
    results = backtest.simulate_trading(testing=testing)
    statistics.save(filename)
    return results


@click.command()
@click.option('--config', default=settings.DEFAULT_CONFIG_FILENAME, help='Config filename')
@click.option('--testing/--no-testing', default=False, help='Enable testing mode')
@click.option('--tickers', default='SPY', help='Tickers (use comma)')
@click.option('--filename', default='', help='Pickle (.pkl) statistics filename')

def main(config, testing, tickers, filename):
    tickers = tickers.split(",")
    config = settings.from_file(config, testing)
    run(config, testing, tickers, filename)


if __name__ == "__main__":
    main()

