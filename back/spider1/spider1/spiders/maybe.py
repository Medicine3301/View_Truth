import scrapy


class SethSpider(scrapy.Spider):
    name = "maybe"
    allowed_domains = ["www.setn.com"]
    start_urls = ["https://www.setn.com/viewall.aspx?pagegroupid=41"]

    def parse(self, response):
        News = response.xpath('//*[@id="NewsList"]/div')
        
        for article in News: 
            link = article.xpath('.//div/h3/a/@href').get()
            uptime = article.xpath('.//div/time/text()').get()
            title = article.xpath('.//div/h3/a/text()').get()
            subject = article.xpath('.//div/div/a/text()').get()         
            yield response.follow(url=link, callback=self.parse_page, meta={'title': title, 'subject': subject, 'uptime': uptime})

    def parse_page(self, response):
        title = response.meta['title']
        uptime = response.meta['uptime']
        subject = response.meta['subject']
        
        content = response.xpath('//*[@id="Content1"]/p/text()').getall()
        
        yield {
            'title': title,
            'subject': subject,
            'uptime': uptime,
            'paragraph': content,
        }
