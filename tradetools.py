#!/usr/bin/python

import trademodel as model
from trademodel import Company, Asset, SpotMarket

def parse_date(raw_date):
    import datetime
    return datetime.datetime.strptime(raw_date, '%Y%m%d').date()

def parse_file(fhandle):
    fcontent = fhandle.readlines()

    #ending_line = 10
    ending_line = len(fcontent) - 1

    dbsession = model.get_session()

    for line in range(1, ending_line):
        line = fcontent[line]

        # Extract all relevant fields
        date = parse_date(line[2:10])
        asset_bdi = int(line[10:12])
        asset_code = line[12:24].strip()
        market_type = int(line[24:27])
        short_company_name = line[27:39].strip()
        asset_specification = line[39:49].strip()
        operation_deadline = line[49:52]
        currency = line[52:56]
        opening_price = int(line[56:69])
        max_price = int(line[69:82])
        min_price = int(line[82:95])
        avg_price = int(line[95:108])
        last_price = int(line[108:121])
        best_buy_offer_price = int(line[121:134])
        best_sell_offer_price = int(line[134:147])
        total_negotiations = int(line[147:152]) # ?
        total_asset_negotiations = int(line[152:170]) # ?
        asset_negotiation_volume = int(line[170:188]) # ?

        if market_type != 10:
            # We only deal with spot market
            continue

        # Create company, if it's new
        company = model.get_or_create(
                           dbsession,
                           Company,
                           {'primary_keys': dict(short_name = short_company_name)})

        # Create asset, if it's new
        asset = model.get_or_create(
                         dbsession,
                         Asset,
                         {'primary_keys':
                            dict(code = asset_code,
                            bdi = asset_bdi,
                            company = company)
                         })

        # Create trade day
        spot_market = model.get_or_create(
                             dbsession,
                             SpotMarket,
                             {'primary_keys':
                                dict(date = date,
                                asset = asset),
                             'regular_keys':
                                dict(opening_price = opening_price,
                                max_price = max_price,
                                min_price = min_price,
                                avg_price = avg_price,
                                last_price = last_price,
                                best_buy_offer_price = best_buy_offer_price,
                                best_sell_offer_price = best_sell_offer_price,
                                volume = asset_negotiation_volume,
                                price_factor_quotient=1,
                                price_factor_dividend=1)
                             })
        pass

    dbsession.commit()

    """
    sample_spot_market = dbsession.query(SpotMarket).join(Asset).\
                       filter(Asset.code == 'AAPL34').all()
    print sample_spot_market[0].asset.code
    print sample_spot_market[0].asset.company.short_name
    """
    pass


def close_type(close_prices, current_day):
    if close_prices[current_day] > close_prices[current_day-1]:
        return 'i'
    elif close_prices[current_day] < close_prices[current_day-1]:
        return 'd'
    else:
        return 's'

def probability_recurrence(asset_code):
    dbsession = model.get_session()

    trade_days = dbsession.query(SpotMarket).join(Asset).\
                 filter(Asset.code == asset_code).all()
    open_prices = [day.opening_price/100.0 for day in trade_days]
    close_prices = [day.last_price/100.0 for day in trade_days]
    
    price_events = dict()
    analysis_depth = 3
    analysis_queue = []

    for i in range(1, len(open_prices)):
        analysis_queue.append(close_type(close_prices, i))
        if len(analysis_queue) == analysis_depth:
            queue_event = str().join(analysis_queue)
            event_prefix = queue_event[0:-1]
            event_suffix = queue_event[-1]
            if event_prefix in price_events:
                if event_suffix in price_events[event_prefix]:
                    price_events[event_prefix][event_suffix] += 1.0
                else:
                    price_events[event_prefix][event_suffix] = 1.0
                    pass
            else:
                price_events[event_prefix] = {event_suffix: 1.0}
                pass

            analysis_queue.pop(0)
            pass
        pass

    for key in price_events:
        if 'i' not in price_events[key]:
            price_events[key]['i'] = 0.0
            pass

        if 'd' not in price_events[key]:
            price_events[key]['d'] = 0.0
            pass

        if 's' not in price_events[key]:
            price_events[key]['s'] = 0.0
            pass
        pass

    print price_events
    print analysis_queue
    """
    print 'P(I|I) = ', after_increase[1]/inc_events
    print 'P(D|I) = ', after_increase[0]/inc_events
    print 'P(I|D) = ', after_decrease[1]/dec_events
    print 'P(D|D) = ', after_decrease[0]/dec_events
    """
    after_inc_events=price_events['i']['i']+price_events['i']['d']
    after_dec_events=price_events['d']['i']+price_events['d']['d']
    print 'P(I|I) = ', price_events['i']['i']/after_inc_events
    print 'P(D|I) = ', price_events['i']['d']/after_inc_events
    print 'P(I|D) = ', price_events['d']['i']/after_dec_events
    print 'P(D|D) = ', price_events['d']['d']/after_dec_events
    pass

def probability_whip():
    dbsession = model.get_session()

    assets=['VALE3', 'VALE5', 'PETR4', 'PETR3',
            'GOAU4', 'SLED4', 'JBSS3', 'CMIG4',
            'USIM5', 'GOLL4', 'ITUB4', 'WEGE3',
            'RLOG3', 'RUMO3', 'CSAN3', 'HGTX3',]
    cnt_large_decays = 0
    cnt_whips = 0

    for asset_code in assets:
        days = dbsession.query(SpotMarket).join(Asset).\
                    filter(Asset.code == asset_code).all()
        
        print asset_code,'has nbr of assets:',len(days)
        for i in range(4, len(days)-4):
            if days[i-1].min_price <=  0.95 * days[i-2].last_price\
               and days[i-1].min_price >=  0.90 * days[i-2].last_price:
                cnt_large_decays += 1.0
                if days[i].max_price > 1.03 * days[i-1].last_price:
                    cnt_whips += 1.0
                    pass
                pass
            pass

        pass

    print cnt_whips,cnt_large_decays
    print 'Prob whip:',cnt_whips/cnt_large_decays

    pass

def list_assets():
    dbsession = model.get_session()
    assets = dbsession.query(Asset).all()

    """
    # This is how you use the asset list:
    for asset in assets:
        print(asset.code+' ('+asset.company.short_name+')')
        pass
    print('\n'+str(len(assets))+' assets found.')
    """

    return assets

def variation_since(asset_code, ref_date):
    from sqlalchemy import and_
    dbsession = model.get_session()

    cnt_large_decays = 0
    cnt_whips = 0

    last_day = dbsession.query(SpotMarket).join(Asset).\
                order_by(SpotMarket.date.desc()).\
                filter(Asset.code == asset_code).first()
    
    first_day = dbsession.query(SpotMarket).join(Asset).\
                order_by(SpotMarket.date.asc()).\
                filter(and_(Asset.code == asset_code,
                    SpotMarket.date >= ref_date)).first()

    last_price = float(last_day.last_price)
    first_price = float(first_day.last_price)

    print last_price,first_price

    return (last_price/first_price-1.0)*100.0

    pass

def IRF(asset_code, last_days):
    from datetime import datetime, timedelta
    from sqlalchemy import and_

    dbsession = model.get_session()

    base_date = datetime.now().date() - timedelta(days=2*last_days)
    trade_query = dbsession.query(SpotMarket).join(Asset).\
                  order_by(SpotMarket.date.desc()).\
                  filter(and_(Asset.code == asset_code,
                      SpotMarket.date >= base_date))

    trade_days = trade_query.all()[::-1]

    if len(trade_days) == 0:
        return None

    open_prices = [day.opening_price/100.0 for day in trade_days]
    high_data = [day.max_price/100.0 for day in trade_days]
    low_data = [day.min_price/100.0 for day in trade_days]
    close_prices = [day.last_price/100.0 for day in trade_days]
    volumes = [day.volume for day in trade_days]
    dates = [day.date for day in trade_days]

    n_gains = 0
    s_gain = 0.0
    n_losses = 0
    s_losses = 0.0
    for i in range(len(close_prices)-1, len(close_prices)-1-last_days, -1):
        price_diff = close_prices[i] - close_prices[i-1]
        if price_diff > 0:
            n_gains += 1
            s_gain += price_diff
        elif price_diff < 0:
            n_losses += 1
            s_losses += abs(price_diff)
            pass
        pass

    avg_gain = s_gain #/ max(n_gains,1)
    avg_loss = s_losses #/ max(n_losses,1)

    if avg_loss == 0.0:
        avg_loss = 1

    return 100.0 - (100.0 / (1.0 + avg_gain/avg_loss))

    pass

#probability_recurrence('PETR4')
#probability_whip()
#print variation_since('SUZB5', datetime.datetime.now().date() - datetime.timedelta(days=30)), '%'
#print variation_since('SUZB5', datetime.datetime.strptime('2016 01 01', '%Y %m %d').date()), '%'

#list_assets()

