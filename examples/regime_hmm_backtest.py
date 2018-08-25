# -*- coding: utf-8 -*-
from qstrader.risk_manager.example import ExampleRiskManager


import os
import datetime
from qstrader.price_handler.yahoo_daily_csv_bar import YahooDailyCsvBarPriceHandler
from qstrader.compat import queue
# regime_hmm_backtest.py
import datetime
import pickle
import click
import numpy as np
from qstrader import settings
from qstrader.compat import queue
from qstrader.price_parser import PriceParser
from qstrader.price_handler.yahoo_daily_csv_bar import \
YahooDailyCsvBarPriceHandler
from qstrader.strategy import Strategies, DisplayStrategy
from qstrader.position_sizer.naive import NaivePositionSizer
from qstrader.risk_manager.example import ExampleRiskManager
from qstrader.portfolio_handler import PortfolioHandler
from qstrader.compliance.example import ExampleCompliance
from qstrader.execution_handler.ib_simulated import \
IBSimulatedExecutionHandler
from qstrader.statistics.tearsheet import TearsheetStatistics
from qstrader.trading_session.backtest import Backtest
from .regime_hmm_strategy import MovingAverageCrossStrategy
from qstrader.risk_manager.regime_hmm_risk_manager import RegimeHMMRiskManager