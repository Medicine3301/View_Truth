import requests
from bs4 import BeautifulSoup
import aiomysql
import asyncio
import google.generativeai as genai
import json
import re
from datetime import datetime

# 確保 API 金鑰正確無誤
genai.configure(api_key="AIzaSyChZPbwnQY-JPm7cPU8kSDn3PiO1Amfo2Q")

# 建立模型物件
model = genai.GenerativeModel("gemini-1.5-flash")

# 資料庫配置
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456",
    "db": "new_community",
    "charset": "utf8mb4",
}

# 創建數據庫連接池
async def setup_db():
    return await aiomysql.create_pool(**DB_CONFIG, autocommit=True)

# 插入數據函數
async def insert_news_analysis(pool, news_data):
    """
    將新聞分析數據插入資料庫。
    """
    query = """
        INSERT INTO news (newstitle, journ, newsclass, score, newscontent, suggest)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = [
        (item["title"], item["link"], item["class"], item["score"], item["content"], item["suggestions"])
        for item in news_data
    ]
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.executemany(query, params)
            await conn.commit()

# 清理文本函數
def clean_text(text):
    """
    清理特殊字符和多餘的空白。
    """
    return re.sub(r'[^\w\s.,!?]', '', text)

def create_prompt(news_article):
    max_length = 1000  # 限制最大字符數
    truncated_article = news_article[:max_length]
    return f"""
    你是一個新聞分析專家，專注於幫助使用者釐清新聞的真實性。

    請STRICTLY按照以下 JSON 格式返回結果，不要包含任何其他文字：
    {{
      "title": "改進後的標題",
      "link": "原始新聞連結",
      "content": "改寫後的新聞內容",
      "score": 1-5的整數評分,
      "class": "新聞分類",
      "suggestions": "查證建議"
    }}

    分析要求：
    1. 修改新聞標題，使其更準確
    2. 改寫內容，保持語意清晰
    3. 評估新聞真實性
    4. 提供查證建議

    新聞文章：
    {truncated_article}
    """

async def analyze_article(pool, title, article, link):
    """
    使用 Gemini 分析新聞內容，並將結果插入資料庫。
    """
    prompt = create_prompt("網頁連結:" + link + " 標題:" + title + " 內容:" + article)
    try:
        # 調用 AI 生成分析結果
        response = model.generate_content(prompt)

        # 打印完整的原始響應，幫助診斷問題
        print(f"Raw AI Response for {title}: {response.text}")

        # 嘗試更嚴格的 JSON 解析
        try:
            # 使用正則表達式提取 JSON 部分
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group(0))
            else:
                print(f"無法找到 JSON 結構: {title}")
                return

        except json.JSONDecodeError as json_err:
            print(f"JSON 解析失敗: {title}")
            print(f"原始響應: {response.text}")
            print(f"解析錯誤: {json_err}")
            return

        # 驗證返回字段
        required_keys = ["title", "link", "content", "score", "class", "suggestions"]
        if not all(key in analysis for key in required_keys):
            print(f"缺少必要字段，跳過: {title}")
            return

        # 插入資料庫
        await insert_news_analysis(pool, [analysis])
        print(f"完成分析並插入資料庫: {title}")

    except Exception as e:
        print(f"分析失敗: {title}, 錯誤: {e}")

# 爬取新聞標題和網址
def urlgetter():
    urllist = []
    urltitle = []
    url = "https://www.setn.com/ViewAll.aspx?PageGroupID=0&utm_source=setn.com&utm_medium=menu&utm_campaign=hotnews"
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    # 找到所有 h3 標籤符合 class 名稱的
    h3_elements = soup.find_all('h3', class_='view-li-title')
    base_url = "https://www.setn.com"

    for h3 in h3_elements:
        title = h3.text.strip()
        link = h3.find('a')['href'] if h3.find('a') else 'No link found'
        if link.startswith('/'):
            link = base_url + link
        urltitle.append(title)
        urllist.append(link)
    
    return urltitle, urllist

# 爬取新聞內容並分析
async def report_getter(pool):
    urltitle, urllist = urlgetter()
    
    for i in range(len(urltitle)):
        url = urllist[i]
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        content_div = soup.find('div', id='Content1')

        if content_div:
            article_content = ""
            p_tags = content_div.find_all('p')
            for p in p_tags:
                text = p.get_text()
                article_content += text + "\n"

            # 清理文章內容
            article_content = clean_text(article_content)

            # 分析新聞內容
            await analyze_article(pool, urltitle[i], article_content, url)

# 主執行邏輯
async def main():
    pool = await setup_db()
    await report_getter(pool)
    pool.close()
    await pool.wait_closed()

# 執行
if __name__ == "__main__":
    asyncio.run(main())
