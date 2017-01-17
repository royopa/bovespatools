#!/usr/bin/python

from tradetools import list_assets
import argparse

arg_parser = argparse.ArgumentParser(description='Prints all available assets, and their names')

args = arg_parser.parse_args()

assets = list_assets()
for asset in assets:
    print(asset.code+' ('+asset.company.short_name+')')
print('\n'+str(len(assets))+' assets found.')

