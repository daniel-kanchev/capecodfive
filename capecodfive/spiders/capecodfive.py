import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from capecodfive.items import Article


class capecodfiveSpider(scrapy.Spider):
    name = 'capecodfive'
    start_urls = ['https://www.capecodfive.com/cape-cod-5-news']

    def parse(self, response):
        articles = response.xpath('//article//div[@class="field__item"]/ul/li/h6')
        for article in articles:
            link = article.xpath('./a/@href').get()
            date = article.xpath('./strong/text()').get()
            if date:
                date = date.strip()[:-1]

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//article//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content[1:-1]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
