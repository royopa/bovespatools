#!/usr/bin/python

from tradetools import parse_file
import argparse

arg_parser = argparse.ArgumentParser(description='Imports bovespa historical data into a database file.')
arg_parser.add_argument('input_file', help='Text file with historical data to be imported.', nargs='+')

args = arg_parser.parse_args()

for fname in args.input_file:
    fhandle = None

    if fname.lower().endswith('.zip'):
        import zipfile
        ziphandle = zipfile.ZipFile(fname)
        dbase_name = ziphandle.namelist()[0]
        fhandle = ziphandle.open(dbase_name)
    elif fname.lower().endswith('.txt'):
        fhandle = open(fname, 'r')
    else:
        print('Unknown file format: '+fname)
        break

    print('Importing file ' + fname + '...')
    parse_file(fhandle)
    pass
