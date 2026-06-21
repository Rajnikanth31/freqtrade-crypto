"""Momentum Crossover DCA Strategy for Freqtrade.
Calculates fast and slow moving averages and generates buy (bullish crossover)
and sell (bearish crossover) signals. Supports hyperparameter optimization.
"""
from __future__ import annotations

import logging
from pandas import DataFrame
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter

log = logging.getLogger(__name__)


class MomentumDCACrossover(IStrategy):
    """
    Momentum DCA Crossover Strategy.
    Buy: Fast MA crosses above Slow MA.
    Sell: Fast MA crosses below Slow MA.
    """
    # Strategy interface version
    INTERFACE_VERSION = 3

    # Define hyperoptable MA window sizes
    fast_ma_len = IntParameter(5, 20, default=10, space='buy', optimize=True)
    slow_ma_len = IntParameter(20, 50, default=30, space='buy', optimize=True)

    # ROI table (Take Profit targets)
    minimal_roi = {
        "0": 0.05  # Default: Take profit at 5% ROI
    }

    # Stop Loss target
    stoploss = -0.02  # Default: Stop loss at -2%

    # Timeframe for the candles
    timeframe = '1h'

    # Run "populate_indicators()" to calculate technical indicators
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Calculate moving averages using pure pandas (prevents dependency errors on systems without TA-Lib)
        dataframe['fast_ma'] = dataframe['close'].rolling(window=self.fast_ma_len.value).mean()
        dataframe['slow_ma'] = dataframe['close'].rolling(window=self.slow_ma_len.value).mean()
        return dataframe

    # Run "populate_entry_trend()" to generate buy signals
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['fast_ma'] > dataframe['slow_ma']) &
                (dataframe['fast_ma'].shift(1) <= dataframe['slow_ma'].shift(1)) &
                (dataframe['volume'] > 0)  # Make sure there is trading volume
            ),
            'enter_long'] = 1
        return dataframe

    # Run "populate_exit_trend()" to generate sell signals
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['fast_ma'] < dataframe['slow_ma']) &
                (dataframe['fast_ma'].shift(1) >= dataframe['slow_ma'].shift(1)) &
                (dataframe['volume'] > 0)
            ),
            'exit_long'] = 1
        return dataframe
