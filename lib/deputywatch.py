import scrapy
import requests
import json
from tools import normalize,cmdline_args
from scrapy.crawler import CrawlerProcess

debug = cmdline_args.debug

deputywatch = {}

class DeputyWatchSpider(scrapy.Spider):
    name = "candidats"
    base_url = 'https://www.deputywatch.org/'
    def start_requests(self):
        urls = [ self.base_url+'recherches/']

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_main)

    def parse_main(self, response):
        for dep in response.xpath('//select[@id="ListeDepute"]/option/text()'):
            nom = dep.extract()
            request = scrapy.Request(url="%safficherDepute/?nom=%s&prenom=&consulter=" % (self.base_url,nom), callback=self.parse_dep)
            request.meta['nom'] = nom
            yield request

    def parse_dep(self, response):
        nom = response.xpath('(//table)[3]/tr/td[1]/center/b/text()').extract()[0]
        for tr in response.xpath('(//table)[3]/tr'):
            nom = tr.xpath('td[1]/center/b/text()').extract()[0]
            url = self.base_url + 'afficherDepute/'+ tr.xpath('td[5]/center/a/@href').extract()[0]
            deputywatch[normalize(nom)] = {'nom':nom,'url':url}
            request = scrapy.Request(url=url, callback=self.parse_fiche)
            request.meta['nom'] = normalize(nom)
            yield request

    def parse_fiche(self, response):
        if response.status != 404:
            deputywatch[response.meta['nom']]['flag'] = True if (not "Aucun fait notable" in response.text or not "Pas d'Infraction(s)" in response.text) else False



if not debug:
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    })


    process.crawl(DeputyWatchSpider)
    process.start() # the script will block here until the crawling is finished

    with open('json/deputywatch.json','w') as f:
        f.write(json.dumps(deputywatch))
else:
    deputywatch = json.loads(open('json/deputywatch.json','r').read())

deputywatch = dict((k,v) for k,v in deputywatch.iteritems() if v.get('flag',False) == True)
