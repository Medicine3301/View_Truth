import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spider1.spider1.spiders.maybe import SethSpider

def run_spider():
    # 獲取專案設定
    settings = get_project_settings()
    
     # 設定輸出檔案路徑在 back 資料夾
    output_file = os.path.join(os.path.dirname(__file__), 'news_data.json')
    
    # 檢查並清空現有的輸出檔案
    if os.path.exists(output_file):
        with open(output_file, 'w', encoding='utf8') as f:
            f.write('')
    
    # 可以在這裡添加其他設定
    settings['FEEDS'] = {
        output_file: {
            'format': 'json',
            'encoding': 'utf8',
            'indent': 4,
        }
    }
    
    # 創建爬蟲進程
    process = CrawlerProcess(settings)
    
    # 運行爬蟲
    process.crawl(SethSpider)
    process.start()

if __name__ == '__main__':
    run_spider()
