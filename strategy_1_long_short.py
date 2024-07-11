import pandas as pd
import math


def simple_moving_avg(df, window=21):
    """Return a simple moving average from a specified window in the 'close' column of DataFrame df."""
    sma = df['close'].rolling(window=window, min_periods=21).mean()
    df['SMA'] = sma
    return df


def bollinger_bands_x2(df, window=21):
    """Return 2 sets of bollinger bands over the specified window with 2 and 3 standard deviations."""
    rolling_avg = df['close'].rolling(window=window, min_periods=21).mean()
    std_dev = df['close'].rolling(window=window).std(ddof=0)
    df['lower_band_2SD'] = rolling_avg - (std_dev * 2)
    df['upper_band_2SD'] = rolling_avg + (std_dev * 2)
    df['lower_band_3SD'] = rolling_avg - (std_dev * 3)
    df['upper_band_3SD'] = rolling_avg + (std_dev * 3)
    return df


def strategy_1(df):
    df['position'] = 0
    df['cost'] = 0
    df['P/L'] = 0
    df['%P/L'] = 0
    df['total_P/L'] = 0
    df['yearly_%P/L'] = 0
    df['signal_type'] = ''
    triggered_5_or_6 = False
    pause = False
    doubled = False
    entry_prices = []
    cost_prices = []
    account_balance = 0
    df['year'] = pd.to_datetime(df['DATE TIME']).dt.year

    for i in range(2, len(df)):
        signal_2sd = 0
        signal_3sd = 0
        buy_signals = 0
        sell_signals = 0
        exit_price_5 = 0
        exit_price_6 = 0
        exit_price_7 = 0
        exit_price_8 = 0
        exit_price_pchange1 = 0
        exit_price_pchange2 = 0
        pl_5 = 0
        pl_6 = 0
        pl_7 = 0
        pl_8 = 0
        pl_pchange1 = 0
        pl_pchange2 = 0
        double = False
        early_7 = False
        trend_change = False

        if df.loc[i - 1, 'TREND'] == 'Long':
            if df.loc[i - 2, 'TREND'] == 'Short':
                trend_change = True
                if df.loc[i - 1, 'position'] > 0:  # close positions when trend changes
                    exit_price_pchange1 = df.loc[i, 'close']
                    triggered_5_or_6 = False
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + 'CHANGE1'
                    df.loc[i, 'position'] = 0
                    pl_pchange1 = (exit_price_pchange1 - df.loc[i - 1, 'cost']) * len(entry_prices)
                    cost_prices.clear()
                    entry_prices = []

            if df.loc[i, 'year'] != df.loc[i - 1, 'year']:
                account_balance = df.loc[i - 1, 'total_P/L'] + account_balance

            # 2SD/3SD buy signal counter
            for tup in entry_prices:
                if tup[1] == '2SD':
                    signal_2sd += 1
                elif tup[1] == '3SD':
                    signal_3sd += 1

            # entry signals
            if df.loc[i - 1, 'position'] < 3 and not pause and not doubled:
                if df.loc[i, 'open'] <= df.loc[i, 'lower_band_2SD'] and signal_2sd < 2 and len(entry_prices) < 3:  # [2]
                    entry_price = df.loc[i, 'open']
                    buy_signals += 1
                    signal_2sd += 1
                    entry_prices.append((entry_price, '2SD'))
                    cost_prices.append(entry_price)
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '2'
                    triggered_5_or_6 = False
                elif df.loc[i, 'low'] <= df.loc[i, 'lower_band_2SD'] and signal_2sd < 2 and len(
                        entry_prices) < 3:  # [1]
                    entry_price = df.loc[i, 'lower_band_2SD']
                    buy_signals += 1
                    signal_2sd += 1
                    entry_prices.append((entry_price, '2SD'))
                    cost_prices.append(entry_price)
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '1'
                    triggered_5_or_6 = False
                if df.loc[i, 'open'] <= df.loc[i, 'lower_band_3SD'] and signal_3sd < 2 and len(entry_prices) < 3:  # [4]
                    entry_price = df.loc[i, 'open']
                    buy_signals += 1
                    signal_3sd += 1
                    entry_prices.append((entry_price, '3SD'))
                    cost_prices.append(entry_price)
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '4'
                    triggered_5_or_6 = False
                elif df.loc[i, 'low'] <= df.loc[i, 'lower_band_3SD'] and signal_3sd < 2 and len(
                        entry_prices) < 3:  # [3]
                    entry_price = df.loc[i, 'lower_band_3SD']
                    buy_signals += 1
                    signal_3sd += 1
                    entry_prices.append((entry_price, '3SD'))
                    cost_prices.append(entry_price)
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '3'
                    triggered_5_or_6 = False
                if buy_signals < 0 and df.loc[i, 'low'] <= df.loc[i, 'cost'] * (1 - 0.00618) and not pause:  # check [7]
                    if entry_prices[-1][0] < df.loc[i, 'cost'] * (1 - 0.00618):
                        early_7 = True
                        exit_price_7 = df.loc[i, 'cost'] * (1 - 0.00618)
                        pause = True
                        triggered_5_or_6 = False
                        doubled = False
                        df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + 'e7'

            # update position with buy signals
            if df.loc[i - 1, 'position'] + buy_signals <= 3:
                df.loc[i, 'position'] = df.loc[i - 1, 'position'] + buy_signals
            else:
                df.loc[i, 'position'] = 3

            # cost calculation
            if cost_prices:
                df.loc[i, 'cost'] = sum(cost_prices) / len(cost_prices)

            if early_7:
                df.loc[i, 'position'] = 0
                pl_7 = (exit_price_7 - df.loc[i, 'cost']) * len(entry_prices)
                cost_prices.clear()
                entry_prices = []

            # unpause debug for position = 0
            if pause and df.loc[i, 'position'] == 0:
                if df.loc[i, 'open'] >= df.loc[i, 'upper_band_2SD']:  # [6]
                    triggered_5_or_6 = True
                    pause = False
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '6'
                elif df.loc[i, 'high'] >= df.loc[i, 'upper_band_2SD']:  # [5]
                    triggered_5_or_6 = True
                    pause = False
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '5'

            # exit signals
            if df.loc[i, 'position'] > 0:
                if df.loc[i, 'open'] >= df.loc[i, 'upper_band_2SD'] and not doubled:  # [6]
                    sell_signals += math.ceil(df.loc[i, 'position'] / 2)
                    exit_price_6 = df.loc[i, 'open']
                    if df.loc[i - 1, 'position'] == 3:
                        double = True
                    if df.loc[i - 1, 'position'] == 2 or df.loc[i - 1, 'position'] == 3:
                        doubled = True
                    triggered_5_or_6 = True
                    pause = False
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '6'
                elif df.loc[i, 'high'] >= df.loc[i, 'upper_band_2SD'] and not doubled:  # [5]
                    sell_signals += math.ceil(df.loc[i, 'position'] / 2)
                    exit_price_5 = df.loc[i, 'upper_band_2SD']
                    if df.loc[i - 1, 'position'] == 3:
                        double = True
                    if df.loc[i - 1, 'position'] == 2 or df.loc[i - 1, 'position'] == 3:
                        doubled = True
                    triggered_5_or_6 = True
                    pause = False
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '5'
                if df.loc[i, 'low'] <= df.loc[i, 'cost'] * (1 - 0.00618) and not pause:  # [7]
                    sell_signals += df.loc[i, 'position']
                    exit_price_7 = df.loc[i, 'cost'] * (1 - 0.00618)
                    pause = True
                    triggered_5_or_6 = False
                    doubled = False
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '7'
                if df.loc[i, 'close'] <= df.loc[i, 'SMA'] and triggered_5_or_6 and not pause:  # [8]
                    sell_signals += 1
                    exit_price_8 = df.loc[i, 'close']
                    triggered_5_or_6 = False
                    doubled = False
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '8'
                if trend_change and buy_signals > sell_signals and not pause:
                    exit_price_pchange2 = df.loc[i, 'close']
                    df.loc[i, 'position'] = 0
                    pl_pchange2 = (exit_price_pchange2 - df.loc[i, 'cost']) * (buy_signals - sell_signals)
                    entry_prices = []

            # update position with sell signals
            if df.loc[i, 'position'] - sell_signals >= 0:
                df.loc[i, 'position'] = df.loc[i, 'position'] - sell_signals
            else:
                df.loc[i, 'position'] = 0

            if df.loc[i, 'position'] == 0:
                cost_prices.clear()

            # update P/L and %P/L
            if exit_price_6 != 0 and double and len(entry_prices) >= 2:
                pl_6 = (exit_price_6 - df.loc[i, 'cost']) + (exit_price_6 - df.loc[i, 'cost'])
                entry_prices.pop()
                entry_prices.pop()
            elif exit_price_6 != 0 and not double and entry_prices:
                pl_6 = (exit_price_6 - df.loc[i, 'cost'])
                entry_prices.pop()
            elif exit_price_5 != 0 and double and len(entry_prices) >= 2:
                pl_5 = (exit_price_5 - df.loc[i, 'cost']) + (exit_price_5 - df.loc[i, 'cost'])
                entry_prices.pop()
                entry_prices.pop()
            elif exit_price_5 != 0 and not double and entry_prices:
                pl_5 = exit_price_5 - df.loc[i, 'cost']
                entry_prices.pop()
            if exit_price_7 != 0 and entry_prices and not early_7:
                pl_7 = (exit_price_7 - df.loc[i, 'cost']) * len(entry_prices)
                entry_prices = []
            if exit_price_8 != 0 and entry_prices:
                pl_8 = exit_price_8 - df.loc[i, 'cost']
                entry_prices.pop()

            df.loc[i, 'P/L'] = pl_5 + pl_6 + pl_7 + pl_8 + pl_pchange1 + pl_pchange2

            if account_balance == 0:
                df.loc[i, '%P/L'] = df.loc[i, 'P/L'] / (df.loc[22, 'open'] * 3) * 100
            else:
                df.loc[i, '%P/L'] = (df.loc[i, 'P/L'] / account_balance) * 100

            if df.loc[i, 'year'] == df.loc[i - 1, 'year']:
                df.loc[i, 'yearly_%P/L'] = df.loc[i - 1, 'yearly_%P/L'] + df.loc[i, '%P/L']
            else:
                df.loc[i, 'yearly_%P/L'] = 0

        elif df.loc[i - 1, 'TREND'] == 'Short':
            if df.loc[i - 2, 'TREND'] == 'Long':
                trend_change = True
                if df.loc[i - 1, 'position'] > 0:  # close positions when trend changes
                    exit_price_pchange1 = df.loc[i, 'close']
                    triggered_5_or_6 = False
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + 'CHANGE'
                    df.loc[i, 'position'] = 0
                    pl_pchange1 = (exit_price_pchange1 - df.loc[i - 1, 'cost']) * len(entry_prices)
                    cost_prices.clear()
                    entry_prices = []

            if df.loc[i, 'year'] != df.loc[i - 1, 'year']:
                account_balance = df.loc[i - 1, 'total_P/L'] + account_balance

            # 2SD/3SD buy signal counter
            for tup in entry_prices:
                if tup[1] == '2SD':
                    signal_2sd += 1
                elif tup[1] == '3SD':
                    signal_3sd += 1

            # entry signals
            if df.loc[i - 1, 'position'] < 3 and not pause and not doubled:
                if df.loc[i, 'open'] >= df.loc[i, 'upper_band_2SD'] and signal_2sd < 2 and len(entry_prices) < 3:  # [2]
                    entry_price = df.loc[i, 'open']
                    buy_signals += 1
                    signal_2sd += 1
                    entry_prices.append((entry_price, '2SD'))
                    cost_prices.append(entry_price)
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '2'
                    triggered_5_or_6 = False
                elif df.loc[i, 'high'] >= df.loc[i, 'upper_band_2SD'] and signal_2sd < 2 and len(
                        entry_prices) < 3:  # [1]
                    entry_price = df.loc[i, 'upper_band_2SD']
                    buy_signals += 1
                    signal_2sd += 1
                    entry_prices.append((entry_price, '2SD'))
                    cost_prices.append(entry_price)
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '1'
                    triggered_5_or_6 = False
                if df.loc[i, 'open'] >= df.loc[i, 'upper_band_3SD'] and signal_3sd < 2 and len(entry_prices) < 3:  # [4]
                    entry_price = df.loc[i, 'open']
                    buy_signals += 1
                    signal_3sd += 1
                    entry_prices.append((entry_price, '3SD'))
                    cost_prices.append(entry_price)
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '4'
                    triggered_5_or_6 = False
                elif df.loc[i, 'high'] >= df.loc[i, 'upper_band_3SD'] and signal_3sd < 2 and len(
                        entry_prices) < 3:  # [3]
                    entry_price = df.loc[i, 'upper_band_3SD']
                    buy_signals += 1
                    signal_3sd += 1
                    entry_prices.append((entry_price, '3SD'))
                    cost_prices.append(entry_price)
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '3'
                    triggered_5_or_6 = False
                if buy_signals < 0 and df.loc[i, 'low'] >= df.loc[i, 'cost'] * (1 + 0.00618):  # check [7]
                    if entry_prices[-1][0] < df.loc[i, 'cost'] * (1 + 0.00618):
                        early_7 = True
                        exit_price_7 = df.loc[i, 'cost'] * (1 + 0.00618)
                        pause = True
                        triggered_5_or_6 = False
                        doubled = False
                        df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + 'e7'

            # update position with buy signals
            if df.loc[i - 1, 'position'] + buy_signals <= 3:
                df.loc[i, 'position'] = df.loc[i - 1, 'position'] + buy_signals
            else:
                df.loc[i, 'position'] = 3

            # cost calculation
            if cost_prices:
                df.loc[i, 'cost'] = sum(cost_prices) / len(cost_prices)

            if early_7:
                df.loc[i, 'position'] = 0
                pl_7 = (exit_price_7 - df.loc[i, 'cost']) * len(entry_prices)
                cost_prices.clear()
                entry_prices = []

            # unpause debug for position = 0
            if pause and df.loc[i, 'position'] == 0:
                if df.loc[i, 'open'] <= df.loc[i, 'lower_band_2SD']:  # [6]
                    triggered_5_or_6 = True
                    pause = False
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '6'
                elif df.loc[i, 'low'] <= df.loc[i, 'lower_band_2SD']:  # [5]
                    triggered_5_or_6 = True
                    pause = False
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '5'

            # exit signals
            if df.loc[i, 'position'] > 0:
                if df.loc[i, 'open'] <= df.loc[i, 'lower_band_2SD'] and not doubled:  # [6]
                    sell_signals += math.ceil(df.loc[i, 'position'] / 2)
                    exit_price_6 = df.loc[i, 'open']
                    if df.loc[i - 1, 'position'] == 3:
                        double = True
                    if df.loc[i - 1, 'position'] == 2 or df.loc[i - 1, 'position'] == 3:
                        doubled = True
                    triggered_5_or_6 = True
                    pause = False
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '6'
                elif df.loc[i, 'low'] <= df.loc[i, 'lower_band_2SD'] and not doubled:  # [5]
                    sell_signals += math.ceil(df.loc[i, 'position'] / 2)
                    exit_price_5 = df.loc[i, 'lower_band_2SD']
                    if df.loc[i - 1, 'position'] == 3:
                        double = True
                    if df.loc[i - 1, 'position'] == 2 or df.loc[i - 1, 'position'] == 3:
                        doubled = True
                    triggered_5_or_6 = True
                    pause = False
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '5'
                if df.loc[i, 'high'] >= df.loc[i, 'cost'] * (1 + 0.00618) and not pause:  # [7]
                    sell_signals += df.loc[i, 'position']
                    exit_price_7 = df.loc[i, 'cost'] * (1 + 0.00618)
                    pause = True
                    triggered_5_or_6 = False
                    doubled = False
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '7'
                if df.loc[i, 'close'] >= df.loc[i, 'SMA'] and triggered_5_or_6 and not pause:  # [8]
                    sell_signals += 1
                    exit_price_8 = df.loc[i, 'close']
                    triggered_5_or_6 = False
                    doubled = False
                    df.loc[i, 'signal_type'] = df.loc[i, 'signal_type'] + '8'
                if trend_change and buy_signals > sell_signals and not pause:
                    exit_price_pchange2 = df.loc[i, 'close']
                    df.loc[i, 'position'] = 0
                    pl_pchange2 = (exit_price_pchange2 - df.loc[i, 'cost']) * (buy_signals - sell_signals)
                    entry_prices = []

            # update position with sell signals
            if df.loc[i, 'position'] - sell_signals >= 0:
                df.loc[i, 'position'] = df.loc[i, 'position'] - sell_signals
            else:
                df.loc[i, 'position'] = 0

            if df.loc[i, 'position'] == 0:
                cost_prices.clear()

            # update P/L and %P/L
            if exit_price_6 != 0 and double and len(entry_prices) >= 2:
                pl_6 = (exit_price_6 - df.loc[i, 'cost']) + (exit_price_6 - df.loc[i, 'cost'])
                entry_prices.pop()
                entry_prices.pop()
            elif exit_price_6 != 0 and not double and entry_prices:
                pl_6 = (exit_price_6 - df.loc[i, 'cost'])
                entry_prices.pop()
            elif exit_price_5 != 0 and double and len(entry_prices) >= 2:
                pl_5 = (exit_price_5 - df.loc[i, 'cost']) + (exit_price_5 - df.loc[i, 'cost'])
                entry_prices.pop()
                entry_prices.pop()
            elif exit_price_5 != 0 and not double and entry_prices:
                pl_5 = exit_price_5 - df.loc[i, 'cost']
                entry_prices.pop()
            if exit_price_7 != 0 and entry_prices and not early_7:
                pl_7 = (exit_price_7 - df.loc[i, 'cost']) * len(entry_prices)
                entry_prices = []
            if exit_price_8 != 0 and entry_prices:
                pl_8 = exit_price_8 - df.loc[i, 'cost']
                entry_prices.pop()

            df.loc[i, 'P/L'] = -(pl_5 + pl_6 + pl_7 + pl_8 + pl_pchange1 + pl_pchange2)

            if account_balance == 0:
                df.loc[i, '%P/L'] = df.loc[i, 'P/L'] / (df.loc[22, 'open'] * 3) * 100
            else:
                df.loc[i, '%P/L'] = df.loc[i, 'P/L'] / account_balance

            if df.loc[i, 'year'] == df.loc[i - 1, 'year']:
                df.loc[i, 'yearly_%P/L'] = df.loc[i - 1, 'yearly_%P/L'] + df.loc[i, '%P/L']
            else:
                df.loc[i, 'yearly_%P/L'] = 0

    # total P/L calculation
    for i in range(1, len(df)):
        df.loc[i, 'total_P/L'] = df.loc[i - 1, 'total_P/L'] + df.loc[i, 'P/L']

    return df


cont_data = 'C:/Users/Austin/Downloads/15-min futures/continuous_15min_trend_data.csv'
data = pd.read_csv(cont_data)
data = simple_moving_avg(data)
data = bollinger_bands_x2(data)
data = strategy_1(data)
data.to_csv('C:/Users/Austin/Downloads/15-min futures/continuous_15min_data_strategy1_long_short.csv')
