#!/bin/python
import scrapy

from favourite_assets import favourite_assets

# Run as:
# scrapy runspider action_crawler.py -o output.json

class CorporateActionsSpider(scrapy.Spider):
    name = 'cvmcodesspider'
    start_urls = ['http://bvmf.bmfbovespa.com.br/cias-listadas/empresas-listadas/ResumoEventosCorporativos.aspx?codigoCvm=%s&tab=3&idioma=pt-br'%asset['cvm_code'] for asset in favourite_assets]

    def parse(self, response):
        
        for company in response.xpath('//table[contains(@id, "dlCiasCdCVM")]//tr'):
            cvm_code = company.xpath('./td//text()')[3].extract()

            yield {
                'cvm_code': cvm_code,
            }

