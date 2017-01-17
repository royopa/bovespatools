#!/usr/bin/python

import argparse
import trademodel as model
from trademodel import Company, Asset, SpotMarket
from matplotlib.dates import num2date, date2num
import datetime
import numpy as np

class DataCursor(object):
    text_template = 'x: %s\ny: %0.2f'
    x, y = datetime.datetime.now(), 0.0
    xoffset, yoffset = -20, 20
    text_template = '%s\nrange: %.2f ~ %.2f (%.2f%%)\nopen: R$%0.2f\nclose: R$%0.2f (%.2f%%)'

    def __init__(self, ax, dates, quotes):
        # quotes = tochl
        self.ax = ax
        self.dates = dates
        self.quotes = quotes
        self.annotation = ax.annotate(self.text_template, 
                xy=(self.x.strftime('%d/%m/%y'), self.y), xytext=(self.xoffset, self.yoffset), 
                textcoords='offset points', ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.9),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
                )
        self.annotation.set_visible(False)

    def __call__(self, event):
        return self.pin_cursor(event.mouseevent)

    def pin_cursor(self, event):
        if event.xdata is None:
            return

        indx = np.searchsorted(self.dates, [round(event.xdata)])[0]

        self.x, self.y = num2date(self.dates[indx]),\
                         self.quotes[indx][2]
        self.annotation.xy = self.x, self.y
        self.annotation.set_text(self.text_template %\
                (self.x.strftime('%d/%m/%y'),
                    self.quotes[indx][4], # lowest
                    self.quotes[indx][3], # highest
                    (self.quotes[indx][3]/self.quotes[indx][4]-1.0)*100.0, # % diff between highest and lowest
                    self.quotes[indx][1], # open
                    self.y, # close
                    (self.y/self.quotes[indx][1]-1.0)*100.0)) # % diff between open and close
        self.annotation.set_visible(True)
        event.canvas.draw()
        pass
    pass


def plot(asset_code, last_days = 0):
    import matplotlib.pyplot as plt
    from datetime import datetime
    from matplotlib.finance import candlestick_ochl
    from matplotlib import gridspec

    dbsession = model.get_session()

    trade_query = dbsession.query(SpotMarket).join(Asset).\
                  order_by(SpotMarket.date.desc()).\
                  filter(Asset.code == asset_code)

    if last_days > 0:
        trade_query = trade_query.limit(last_days)
        pass

    trade_days = trade_query.all()[::-1]

    if len(trade_days) == 0:
        return False

    open_prices = [day.opening_price/100.0 for day in trade_days]
    high_data = [day.max_price/100.0 for day in trade_days]
    low_data = [day.min_price/100.0 for day in trade_days]
    close_prices = [day.last_price/100.0 for day in trade_days]
    volumes = [day.volume for day in trade_days]
    dates = [date2num(day.date) for day in trade_days]

    fig = plt.figure() 
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    volume_plot = plt.subplot(gs[1])
    plt.xticks(rotation=30)
    candle_plot = plt.subplot(gs[0], sharex=volume_plot)

    # Adjust xticks
    volume_plot.xaxis_date()
    plt.setp(candle_plot.get_xticklabels(), visible=False)

    plt.subplots_adjust(bottom=0.15)

    quotes = []
    for i in xrange(len(dates)):
        quotes.append((dates[i], open_prices[i], close_prices[i], high_data[i], low_data[i]))
        pass
    candle = candlestick_ochl(candle_plot, quotes)

    # Clickable data points
    plt.connect('pick_event', DataCursor(plt.gca(), dates, quotes))
    for line in candle[0]:
        line.set_picker(5) 

    plt.gcf().canvas.set_window_title(asset_code)

    bars = volume_plot.bar(dates, volumes, width=0.25, align='center')
    plt.margins(x=0.05, y=0.05)

    # TODO: Clickable data points for bars

    # Hoverable data points
    """
    cursor = DataCursor(plt.gca(), dates, quotes)
    plt.connect('motion_notify_event', cursor.pin_cursor)
    """

    plt.show()

    return True

def plot_with_lines(asset_code, last_days = 0):
    import matplotlib.pyplot as plt
    from datetime import datetime
    from matplotlib.finance import candlestick_ochl
    from matplotlib import gridspec

    dbsession = model.get_session()

    trade_query = dbsession.query(SpotMarket).join(Asset).\
                  order_by(SpotMarket.date.desc()).\
                  filter(Asset.code == asset_code)

    if last_days > 0:
        trade_query = trade_query.limit(last_days)
        pass

    trade_days = trade_query.all()[::-1]

    if len(trade_days) == 0:
        return False

    open_prices = [day.opening_price/100.0 for day in trade_days]
    high_data = [day.max_price/100.0 for day in trade_days]
    low_data = [day.min_price/100.0 for day in trade_days]
    close_prices = [day.last_price/100.0 for day in trade_days]
    volumes = [day.volume for day in trade_days]
    dates = [date2num(day.date) for day in trade_days]

    fig = plt.figure() 
    gs = gridspec.GridSpec(3, 1, height_ratios=[3, 3, 1])
    volume_plot = plt.subplot(gs[2])
    plt.xticks(rotation=30)
    line_plot = plt.subplot(gs[1], sharex=volume_plot)

    candle_plot = plt.subplot(gs[0], sharex=volume_plot)

    # Adjust xticks
    volume_plot.xaxis_date()
    plt.setp(candle_plot.get_xticklabels(), visible=False)

    plt.subplots_adjust(bottom=0.15)

    quotes = []
    for i in xrange(len(dates)):
        quotes.append((dates[i], open_prices[i], close_prices[i], high_data[i], low_data[i]))
        pass

    # Plot lines
    line_plot.plot([quote[0] for quote in quotes], [quote[2] for quote in quotes])

    # Plot candlesticks
    candle = candlestick_ochl(candle_plot, quotes)

    # Clickable data points
    plt.connect('pick_event', DataCursor(plt.gca(), dates, quotes))
    for line in candle[0]:
        line.set_picker(5) 

    plt.gcf().canvas.set_window_title(asset_code)

    volume_bars = volume_plot.bar(dates, volumes, width=0.25, align='center')
    plt.margins(x=0.05, y=0.05)

    # TODO: Clickable data points for volume_bars

    # Hoverable data points
    """
    cursor = DataCursor(plt.gca(), dates, quotes)
    plt.connect('motion_notify_event', cursor.pin_cursor)
    """

    plt.show()

    return True

arg_parser = argparse.ArgumentParser(description='Plots the historical data for the input asset code')
arg_parser.add_argument('asset_code', help='Asset code, regardless of case (e.g. petr4 or PETR4)')
arg_parser.add_argument('-n', dest='num_days', help='Number of trade days', default=0)

args = arg_parser.parse_args()

if not plot_with_lines(args.asset_code.upper(), int(args.num_days)):
    print('Could not find any data for the asset '+args.asset_code.upper())
