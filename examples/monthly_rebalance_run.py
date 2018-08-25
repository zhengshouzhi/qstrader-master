# -*- coding: utf-8 -*-
import datetime
import click

from qstrader import settings
from qstrader.compat import queue
from qstrader.price_parser import PriceParser
from qstrader.price_handler.yahoo_daily_csv_bar import \
YahooDailyCsvBarPriceHandler
from qstrader.strategy.monthly_liquidate_rebalance_strategy import \
MonthlyLiquidateRebalanceStrategy
#from qstrader.strategy import Strategies, DisplayStrategy
from qstrader.position_sizer.rebalance import \
LiquidateRebalancePositionSizer
from qstrader.risk_manager.example import ExampleRiskManager
from qstrader.portfolio_handler import PortfolioHandler
from qstrader.compliance.example import ExampleCompliance
from qstrader.execution_handler.ib_simulated import \
IBSimulatedExecutionHandler
from qstrader.statistics.tearsheet import TearsheetStatistics
from qstrader.trading_session.backtest import Backtest

def run_monthly_rebalance(
    config, testing, filename,
    benchmark, ticker_weights, title_str,
    start_date, end_date, equity
    ):
    config = settings.from_file(config, testing)
    tickers = [t for t in ticker_weights.keys()]

    # Set up variables needed for backtest
    events_queue = queue.Queue()
    csv_dir = config.CSV_DATA_DIR
    initial_equity = PriceParser.parse(equity)

    # Use Yahoo Daily Price Handler
    price_handler = YahooDailyCsvBarPriceHandler(
        csv_dir, events_queue, tickers,
        start_date=start_date, end_date=end_date
    )

    # Use the monthly liquidate and rebalance strategy
    strategy = MonthlyLiquidateRebalanceStrategy(tickers, events_queue)
    #strategy = Strategies(strategy, DisplayStrategy())

    # Use the liquidate and rebalance position sizer
    # with prespecified ticker weights
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
    title = [title_str]
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