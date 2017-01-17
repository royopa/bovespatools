#!/usr/bin/python

from tradetools import parse_file, list_assets
import trademodel as model
from trademodel import Company, Asset, SpotMarket
import argparse
import fractions


def adjust_price_factors(asset_code):
    dbsession = model.get_session()
    trade_query = dbsession.query(SpotMarket).join(Asset).\
            order_by(SpotMarket.date.desc()).\
            filter(Asset.code == asset_code)

    trade_days = trade_query.all()

    accum_factor_quotient = 1
    accum_factor_dividend = 1

    for i in xrange(len(trade_days)-1, -1, -1):
        # For all but the last trade days...
        if i > 0:
            # Check if that day represented a significant leap over the previous one
            opening_price_i = trade_days[i].opening_price/100.0
            last_price_before = trade_days[i-1].last_price/100.0

            if opening_price_i/last_price_before > 2.0:
                # Potential grouping found
                grouping_factor = int(round(opening_price_i/last_price_before))

                print asset_code,'found grouping of factor',grouping_factor,trade_days[i-1].last_price,trade_days[i].opening_price,trade_days[i].date

                accum_factor_quotient *= grouping_factor

                # Prevents the factor from exploding by always keeping them as small as possible
                factor_gcd = fractions.gcd(accum_factor_quotient, accum_factor_dividend)
                accum_factor_quotient /= factor_gcd
                accum_factor_dividend /= factor_gcd
            elif opening_price_i/last_price_before < 0.5:
                # Potential split found
                split_factor = int(round(last_price_before/opening_price_i))

                print asset_code,'found split of factor',split_factor,trade_days[i-1].last_price,trade_days[i].opening_price,trade_days[i].date

                accum_factor_dividend *= split_factor

                # Prevents the factor from exploding by always keeping them as small as possible
                factor_gcd = fractions.gcd(accum_factor_quotient, accum_factor_dividend)
                accum_factor_quotient /= factor_gcd
                accum_factor_dividend /= factor_gcd

        trade_days[i].price_factor_dividend = accum_factor_dividend
        trade_days[i].price_factor_quotient = accum_factor_quotient

    dbsession.commit()


for asset in list_assets():
    adjust_price_factors(asset.code)
