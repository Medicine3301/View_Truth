import scrapy
from datetime import datetime, timedelta

class SethSpider(scrapy.Spider):
    name = "maybe"
    allowed_domains = ["www.setn.com"]
    pageid=[41,6,4,42,5,50,34,68,97,2,7,12,47,9,52]
    start_urls = [] 
    

    def is_yesterday(self, date_str):
        try:
            # 將 MM/DD HH:MM 格式轉換為日期對象
            today = datetime.now()
            news_date = datetime.strptime(f"{today.year}/{date_str}", "%Y/%m/%d %H:%M")
            
            # 如果日期跨年，調整年份
            if news_date > today:
                news_date = datetime.strptime(f"{today.year-1}/{date_str}", "%Y/%m/%d %H:%M")
            
            # 獲取昨天的日期
            yesterday = today.date() - timedelta(days=1)
            return news_date.date() == yesterday
        except:
            return False

    def start_requests(self):
        for pid in self.pageid:
            url = f"https://www.setn.com/viewall.aspx?pagegroupid={pid}"
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        News = response.xpath('//*[@id="NewsList"]/div')
        
        for article in News: 
            uptime = article.xpath('.//div/time/text()').get()
            # 只處理昨天的新聞
            if uptime and self.is_yesterday(uptime):
                link = article.xpath('.//div/h3/a/@href').get()
                title = article.xpath('.//div/h3/a/text()').get()
                subject = article.xpath('.//div/div/a/text()').get()         
                yield response.follow(url=link, callback=self.parse_page, meta={'title': title, 'subject': subject, 'uptime': uptime})

    def parse_page(self, response):
        title = response.meta['title']
        uptime = response.meta['uptime']
        subject = response.meta['subject']
        link=response.url
        content = response.xpath('//*[@id="Content1"]/p/text()').getall()
        
        yield {
            'link': link,
            'title': title,
            'subject': subject,
            'uptime': uptime,
            'paragraph': content,
           
        }
