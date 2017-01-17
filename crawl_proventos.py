#!/bin/python
import scrapy

# Run as:
# scrapy runspider crawl_proventos.py -o output.json

class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['http://www.guiainvest.com.br/provento/default.aspx?sigla=itub4&proventodinheiropage=24&proventoacaopage=1']

    def parse(self, response):
        for inplit in response.xpath('//tr[td//text()[contains(., "Grupamento")]]'):
            yield {'inplit': inplit.xpath('./td//text()').extract()}

        for split in response.xpath('//tr[td//text()[contains(., "Desdobramento")]]'):
            yield {'split': split.xpath('./td//text()').extract()}

        # Look for next page link
        next_page = response.xpath('//div[contains(@class, "webpart") and descendant::h2//text()[contains(.,"Proventos em A")]]//a[contains(@title, "xima P")]/@href').extract_first()

        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)
