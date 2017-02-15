#!/usr/bin/python

import matplotlib.pyplot as plt
import argparse
import trademodel as model
from trademodel import Company, Asset, SpotMarket
from matplotlib.dates import num2date, date2num
import datetime
import numpy as np
import time

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

current_asset = 0
update_view = False
close_requested = False
ibov_assets = ['VALE3', 'VALE5', 'GOAU4', 'USIM5', 'CSNA3', 'SLED4', 'GOLL4',
               'ITSA4', 'ITUB4', 'SANB11', 'BBAS3', 'BRSR6', 'BBSE3', 'BVMF3',
               'CIEL3', 'WEGE3', 'POMO3', 'TUPY3', 'RAPT4', 'MYPK3', 'RLOG3',
               'RUMO3', 'CSAN3', 'HGTX3', 'VVAR11', 'LREN3', 'LAME4', 'KLBN11',
               'SUZB5', 'FIBR3', 'EMBR3', 'MRFG3', 'ECOR3', 'CCRO3', 'PETR4',
               'PETR3', 'BRKM5', 'KROT3', 'ESTC3', 'ABEV3', 'CESP6', 'CMIG4',
               'ELPL4', 'CSMG3', 'SBSP3', 'HYPE3', 'SMLE3', 'TIMP3', 'OIBR3',
               'VIVR3', 'RENT3', 'JBSS3', 'BRFS3', 'QUAL3', 'NATU3', 'ALSC3',
               'BRPR3', 'CYRE3', 'EZTC3', 'GFSA3', 'TCSA3', 'RSID3', 'IGTA3',
               'BRML3', 'MILS3', 'AGRO3',
               ]

def key_press(event):
    global update_view, current_asset, ibov_assets, close_requested
    if event.key == 'right':
        if current_asset < len(ibov_assets)-1:
            current_asset += 1
        else:
            current_asset = 0
    elif event.key == 'left':
        if current_asset > 0:
            current_asset -= 1
        else:
            current_asset = len(ibov_assets)-1
    elif event.key == 'escape':
        close_requested = True

    update_view = True


fig = None
def plot_with_lines(asset_code, last_days = 0):
    import matplotlib.pyplot as plt
    from datetime import datetime, timedelta
    from matplotlib.finance import candlestick_ochl
    from matplotlib import gridspec
    from sqlalchemy import and_

    global fig, update_view, close_requested

    # Enable interactive mode so that draw() is non-blocking
    plt.ion()

    fig = plt.figure() 
    plt.connect('key_press_event', key_press)

    fig.clf()

    dbsession = model.get_session()

    while not close_requested:
        base_date = datetime.now().date() - timedelta(days=last_days)
        trade_query = dbsession.query(SpotMarket).join(Asset).\
                      order_by(SpotMarket.date.desc()).\
                      filter(and_(Asset.code == asset_code,
                          SpotMarket.date >= base_date))

        trade_days = trade_query.all()[::-1]

        if len(trade_days) == 0:
            return False

        open_prices = [day.opening_price/100.0 for day in trade_days]
        high_data = [day.max_price/100.0 for day in trade_days]
        low_data = [day.min_price/100.0 for day in trade_days]
        close_prices = [day.last_price/100.0 for day in trade_days]
        volumes = [day.volume for day in trade_days]
        dates = [date2num(day.date) for day in trade_days]

        gs = gridspec.GridSpec(3, 1, height_ratios=[3, 3, 1])
        volume_plot = plt.subplot(gs[2])
        plt.xticks(rotation=30)

        line_plot = plt.subplot(gs[1], sharex=volume_plot)
        candle_plot = plt.subplot(gs[0], sharex=volume_plot)

        line_plot.tick_params(axis='x',          # changes apply to the x-axis
                              which='both',      # both major and minor ticks are affected
                              bottom='off',      # ticks along the bottom edge are off
                              top='off',         # ticks along the top edge are off
                              labelbottom='off')

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
        fig.canvas.draw()

        while not update_view:
            fig.canvas.get_tk_widget().update()

        update_view = False
        asset_code = ibov_assets[current_asset]

    return True

arg_parser = argparse.ArgumentParser(description='Plots the historical data for the input asset code')
arg_parser.add_argument('-n', dest='num_days', help='Number of trade days', default=90)

args = arg_parser.parse_args()


if not plot_with_lines(ibov_assets[current_asset], int(args.num_days)):
    print('Could not find any data for the asset '+args.asset_code.upper())
