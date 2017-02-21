#!/bin/python
import scrapy

from favourite_assets import favourite_assets

# Run as:
# scrapy runspider action_crawler.py -o output.json

class CorporateActionsSpider(scrapy.Spider):
    name = 'corporateactionsspider'
    start_urls = ['http://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/CiaAb/ResultBuscaParticCiaAb.aspx?TipoConsult=C']
    custom_settings = {
        'ITEM_PIPELINES': {
            'corporate_actions_crawler.pipelines.CorporateActionsCrawlerPipeline': 300
        }
    }

    def parse(self, response):
        for company in response.xpath('//table[contains(@id, "dlCiasCdCVM")]//tr'):
            cvm_code = company.xpath('./td//text()')[3].extract()
            company_url = 'http://bvmf.bmfbovespa.com.br/cias-listadas/empresas-listadas/ResumoEventosCorporativos.aspx?codigoCvm=%s&tab=3&idioma=pt-br'%cvm_code

            yield scrapy.Request(company_url, self.parse_corporation)

    def parse_corporation(self, response):
        for tr in response.xpath('//div[contains(@id, "divBonificacao")]//tr')[1:-1]:
            cell = tr.xpath('./td')

            action_type = cell[0].xpath('./text()').extract_first()
	    isin = cell[1].xpath('./text()').extract_first()
	    approval_date = cell[2].xpath('./text()').extract_first()
	    ex_date = cell[3].xpath('./text()').extract_first()
	    factor = float(cell[4].xpath('./span//text()').extract_first())
	    issued_asset = cell[5].xpath('./text()').extract_first()
	    remarks = cell[6].xpath('./text()').extract_first().strip()

            yield {
                'action_type': action_type,
		'isin': isin,
		'approval_date': approval_date,
		'ex_date': ex_date,
                'factor': factor,
		'issued_asset': issued_asset,
		'remarks': remarks
            }

