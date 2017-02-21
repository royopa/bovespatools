# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import trademodel as model
from datetime import datetime
from trademodel import Asset, AssetActions

class CorporateActionsCrawlerPipeline(object):
    def process_item(self, item, spider):
        if 'action_type' in item: # Check if this is a company
            dbsession = model.get_session()

            approval_date = datetime.strptime(item['approval_date'], '%d/%m/%Y').date()
            ex_date = datetime.strptime(item['ex_date'], '%d/%m/%Y').date()

            asset = dbsession.query(Asset).filter_by(isin=item['isin']).first()

            # Some isin codes are too old to be relevant for us
            if asset != None:
                corporate_action = model.get_or_create(
                    dbsession,
                    AssetActions,
                    {'primary_keys':
                        dict(asset = asset,
                             action_type = item['action_type'],
                             ex_date = ex_date,
                       ),
                     'regular_keys':
                        dict(approval_date = approval_date,
                             factor = item['factor'],
                             issued_asset = item['issued_asset'],
                             remarks = item['remarks'])
                    }
                )

                dbsession.commit()

        return item
