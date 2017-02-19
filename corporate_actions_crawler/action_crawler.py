#!/bin/python
import scrapy

# Run as:
# scrapy runspider action_crawler.py -o output.json

class CorporateActionsSpider(scrapy.Spider):
    name = 'corporateactionsspider'
    start_urls = ['http://bvmf.bmfbovespa.com.br/cias-listadas/empresas-listadas/ResumoEventosCorporativos.aspx?codigoCvm=19348&tab=3&idioma=pt-br']

    def parse(self, response):
        
        for tr in response.xpath('//div[contains(@id, "divBonificacao")]//tr')[1:-1]:
            cell = tr.xpath('./td')

            opType = cell[0].xpath('./text()').extract_first()
	    isinCode = cell[1].xpath('./text()').extract_first()
	    deliberationDate = cell[2].xpath('./text()').extract_first()
	    withDate = cell[3].xpath('./text()').extract_first()
	    opFactor = float(cell[4].xpath('./span//text()').extract_first())
	    releasedAsset = cell[5].xpath('./text()').extract_first()
	    observations = cell[6].xpath('./text()').extract_first().strip()

            yield {
                'opType': opType,
		'isinCode': isinCode,
		'deliberationDate': deliberationDate,
		'withDate': withDate,
                'opFactor': opFactor,
		'releasedAsset': releasedAsset,
		'observations': observations
            }

