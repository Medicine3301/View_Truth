import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# 確保 API 金鑰正確無誤
genai.configure(api_key="AIzaSyChZPbwnQY-JPm7cPU8kSDn3PiO1Amfo2Q")

# 建立模型物件
model = genai.GenerativeModel("gemini-1.5-flash")

# 核心需求
CORE_NEED = """
你是一個新聞分析專家，專注於幫助使用者釐清新聞的真實性，給予查證建議。
核心目標要修改新聞標題、改寫整體新聞，合乎文章內容不誇大。要好好分段，給予分析真實性的小報告，
要給評分(1-5滿分五分)，還要給使用者查證建議。
請確保避免冗長的背景描述，並直接進入主題。
"""

# Prompt 模版
def create_prompt(news_article):
    return f"""
    核心需求：
    {CORE_NEED}

    新聞文章：
    {news_article}
    """

# 爬取新聞標題和網址
def urlgetter():
    urllist = []
    urltitle = []
    url = "https://www.setn.com/ViewAll.aspx?PageGroupID=0&utm_source=setn.com&utm_medium=menu&utm_campaign=hotnews"
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    # 找到所有h3標籤符合class名稱的
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

# 爬取新聞內容並儲存到檔案
def report_getter():
    urltitle, urllist = urlgetter()
    
    for i in range(len(urltitle)):
        url = urllist[i]
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        content_div = soup.find('div', id='Content1')

        if content_div:
            with open("新聞播報.txt", 'a', encoding='utf-8') as file:
                p_tags = content_div.find_all('p')
                file.write("標題: " + urltitle[i] + "\n")
                
                article_content = ""
                for p in p_tags:
                    text = p.get_text()
                    file.write(text + "\n")
                    article_content += text + "\n"
                
                file.write("\n" + "="*50 + "\n\n")

                # 分析新聞內容
                analyze_article(urltitle[i], article_content)

# 使用 Gemini API 分析新聞內容
def analyze_article(title, article):
    prompt = create_prompt(article)
    try:
        response = model.generate_content(prompt)
        analysis = response.text
        
        # 儲存分析結果
        with open("新聞分析報告.txt", 'a', encoding='utf-8') as file:
            file.write(f"新聞標題: {title}\n")
            file.write(f"分析結果:\n{analysis}\n")
            file.write("\n" + "="*50 + "\n\n")
        print(f"完成分析: {title}")
    except Exception as e:
        print(f"分析失敗: {title}, 錯誤: {e}")

# 執行爬取和分析
report_getter()
