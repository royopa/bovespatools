#!/usr/bin/python

import matplotlib.pyplot as plt
import argparse
import trademodel as model
from trademodel import Company, Asset, SpotMarket
from matplotlib.dates import num2date, date2num
import datetime
import numpy as np
import tradetools


arg_parser = argparse.ArgumentParser(description='Show IRF for given asset')
arg_parser.add_argument('asset_code', help='Asset code, regardless of case (e.g. petr4 or PETR4)')

args = arg_parser.parse_args()

print tradetools.IRF(args.asset_code.upper(), 14)
