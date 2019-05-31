# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.loader import ItemLoader

from rokomari_crawler.items import RokomariCrawlerItem


def book_info_a(response, value):
    try:
        return response.xpath('//td[text()="{}"]/following-sibling::td/a/text()'.format(value)).extract_first().strip()
    except:
        value = ''
        return value

def book_info(response, value):
    try:
        return response.xpath('//td[text()="{}"]/following-sibling::td/text()'.format(value)).extract_first().strip()
    except:
        value = ''
        return value

class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['rokomari.com']
    

    def __init__(self, category):
        self.start_urls = [category]

    def parse(self, response):
        books = response.xpath('//*[starts-with(@class, "book-list-wrapper")]')

        for book in books:
            book_url = book.xpath('.//a/@href').extract_first()
            book_absolute_url = response.urljoin(book_url)

            yield Request(book_absolute_url, callback=self.parse_book, meta={'URL': book_absolute_url,})
        next_page_url = response.xpath('//a[text()="Next"]/@href').extract_first()
        absolute_next_page_url = response.urljoin(next_page_url)

        yield Request(absolute_next_page_url, callback=self.parse)
    
    def parse_book(self, response):
        l = ItemLoader(item=RokomariCrawlerItem(), response=response)
        title = book_info(response, 'Title')
        author = book_info_a(response, 'Author')
        translator = book_info_a(response, 'Translator')
        editor = book_info_a(response, 'Editor')
        publisher = book_info_a(response, 'Publisher')
        isbn = book_info(response, 'ISBN')
        edition = book_info(response, 'Edition')
        no_of_page = book_info(response, 'Number of Pages')
        country = book_info(response, 'Country')
        language = book_info(response, 'Language')

        price = response.xpath('//p[@class="details-book-info__content-book-price"]/text()').extract_first().strip()
        book_url = response.meta.get('URL')
        try:
            image_urls = response.xpath('//div[@class="look-inside-bg"]/following-sibling::img/@src').extract_first()
        except:
            image_urls = response.xpath('//div[@class="col-4 details-book-main-img-wrapper "]/img/@src').extract_first()

        l.add_value('title', title)
        l.add_value('author', author)
        l.add_value('translator', translator)
        l.add_value('editor', editor)
        l.add_value('publisher', publisher)
        l.add_value('isbn', isbn)
        l.add_value('edition', edition)
        l.add_value('no_of_page', no_of_page)
        l.add_value('country', country)
        l.add_value('language', language)
        l.add_value('price', price)
        l.add_value('book_url', book_url)
        l.add_value('image_urls', image_urls)

        return l.load_item()


