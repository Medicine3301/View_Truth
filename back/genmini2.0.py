import logging
import statistics
import json
import re
from typing import Dict, List, Any
import google.generativeai as genai

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gemini API 配置
GEMINI_API_KEY = "AIzaSyChZPbwnQY-JPm7cPU8kSDn3PiO1Amfo2Q"

class GeminiVerificationSystem:
    def __init__(self, api_key=GEMINI_API_KEY):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
    
    def verify_information(self, content: str) -> Dict[str, Any]:
        """主要驗證函數，使用多角度查詢策略"""
        logger.info(f"開始驗證信息: {content[:50]}...")
        
        try:
            # 執行多角度查詢
            responses = self.verify_with_gemini(content)
            
            # 執行多輪驗證
            final_result = self.multi_round_verification(content, responses)
            
            return final_result
        
        except Exception as e:
            logger.error(f"驗證過程發生錯誤: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'credibility_score': None
            }
    
    def verify_with_gemini(self, content: str) -> Dict[str, Any]:
        """使用多角度提示詞設計來獲取Gemini的多面向評估"""
        # 設計多角度提示詞
        prompts = {
            'factual': self.generate_factual_prompt(content),
            'critical': self.generate_critical_prompt(content),
            'balanced': self.generate_balanced_prompt(content),
            'source': self.generate_source_checking_prompt(content)
        }
        
        # 獲取多個回應
        responses = {}
        for angle, prompt in prompts.items():
            try:
                response = self.query_gemini_api(prompt)
                parsed_response = self.parse_response(response, angle)
                responses[angle] = parsed_response
                logger.info(f"成功獲取 {angle} 角度的回應")
            except Exception as e:
                logger.error(f"獲取 {angle} 角度回應時發生錯誤: {e}")
                responses[angle] = {
                    'score': 0,
                    'reasoning': f"獲取回應失敗: {str(e)}",
                    'raw_response': None
                }
        
        # 整合多角度回應
        return self.integrate_responses(responses)
    
    def generate_factual_prompt(self, content: str) -> str:
        """生成事實檢查提示詞"""
        return f"""
        以專業事實檢查員的身份，評估以下信息的可信度。請關注事實聲明、數據引用和可驗證的內容,不要質疑評分標準，必須要中文回應。

        信息內容：{content}

        請按以下格式回應：
        1. 關鍵事實聲明：（列出主要事實聲明）
        2. 一致性評估：（評估內部邏輯一致性）
        3. 可驗證性：（評估是否可以被獨立驗證）
        4. 可信度評分：（0-100分）
        5. 評分理由：（解釋評分依據）
        """
    
    def generate_critical_prompt(self, content: str) -> str:
        """生成批判性分析提示詞"""
        return f"""
        請採用批判性思維專家的角度，分析以下信息的可靠性。特別關注可能的錯誤、誤導或邏輯謬誤,必須要中文回應。

        信息內容：{content}

        請按以下格式回應：
        1. 潛在問題點：（列出可能存在的問題）
        2. 邏輯分析：（評估推理過程）
        3. 替代解釋：（提供其他可能的解釋）
        4. 可信度評分：（0-100分）
        5. 批判性評估：（總體評價）
        """
    
    def generate_balanced_prompt(self, content: str) -> str:
        """生成平衡視角提示詞"""
        return f"""
        請以中立的觀察者身份，平衡地評估以下信息的可信度。考慮支持和反對的觀點,必須要中文回應。

        信息內容：{content}

        請按以下格式回應：
        1. 支持觀點：（列出支持信息真實性的因素）
        2. 反對觀點：（列出質疑信息真實性的因素）
        3. 綜合分析：（權衡兩方面因素）
        4. 可信度評分：（0-100分）
        5. 平衡評估：（總體評價）
        """
    
    def generate_source_checking_prompt(self, content: str) -> str:
        """生成來源檢查提示詞"""
        return f"""
        請扮演信息來源專家，評估以下信息的來源可靠性。關注信息來源、引用和權威性,必須要中文回應

        信息內容：{content}

        請按以下格式回應：
        1. 來源分析：（評估信息來源）
        2. 權威性：（評估信息權威性）
        3. 可追溯性：（評估信息是否可追溯）
        4. 來源可信度評分：（0-100分）
        5. 評分理由：（解釋評分依據）
        """
    
    def query_gemini_api(self, prompt: str) -> Dict[str, Any]:
        """向Gemini API發送請求並獲取回應"""
        try:
            # 使用新的API方法
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    top_k=40,
                    top_p=0.95,
                    max_output_tokens=1024
                )
            )
            return response
        
        except Exception as e:
            logger.error(f"API請求錯誤: {e}")
            raise
    
    def parse_response(self, response: Any, angle: str) -> Dict[str, Any]:
        """解析Gemini API的回應，提取關鍵信息"""
        try:
            # 從新版API回應中提取文本
            if hasattr(response, 'text'):
                text = response.text
            elif hasattr(response, 'parts'):
                text = ' '.join([part.text for part in response.parts if hasattr(part, 'text')])
            else:
                # 嘗試以JSON格式獲取回應
                text = str(response)
            
            # 提取可信度評分
            score = self.extract_score(text)
            
            return {
                'angle': angle,
                'score': score,
                'reasoning': text,
                'raw_response': str(response)
            }
        
        except Exception as e:
            logger.error(f"解析回應時發生錯誤: {e}")
            raise
    
    def extract_score(self, text: str) -> float:
        """從回應文本中提取可信度評分"""
        try:
            # 尋找評分模式
            for line in text.split('\n'):
                if '可信度評分' in line or '評分' in line or 'score' in line.lower():
                    # 提取數字
                    import re
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        score = float(numbers[0])
                        if score > 100:  # 防止錯誤的高分
                            score = 100
                        return score
            
            # 如果找不到明確的評分，返回默認值
            return 50.0
        
        except Exception as e:
            logger.error(f"提取評分時發生錯誤: {e}")
            return 50.0  # 默認中等可信度
    
    def integrate_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """整合多角度回應，計算加權評分"""
        try:
            # 計算加權評分
            weighted_score = self.calculate_weighted_score(responses)
            
            # 獲取各角度的理由
            reasoning = {angle: response.get('reasoning', '') 
                        for angle, response in responses.items()}
            
            # 檢查評分一致性
            scores = [response.get('score', 0) for response in responses.values()]
            variance = statistics.variance(scores) if len(scores) > 1 else 0
            
            agreement_level = "高度一致" if variance < 100 else \
                            "部分一致" if variance < 400 else \
                            "不一致"
            
            return {
                'integrated_score': weighted_score,
                'individual_responses': responses,
                'agreement_level': agreement_level,
                'score_variance': variance,
                'reasoning': reasoning
            }
        
        except Exception as e:
            logger.error(f"整合回應時發生錯誤: {e}")
            raise
    
    def calculate_weighted_score(self, responses: Dict[str, Any]) -> float:
        """計算加權評分"""
        # 設定不同角度的權重
        weights = {
            'factual': 0.4,
            'critical': 0.3,
            'balanced': 0.2,
            'source': 0.1
        }
        
        weighted_score = 0
        total_weight = 0
        
        for angle, response in responses.items():
            if angle in weights and 'score' in response:
                weight = weights.get(angle, 0)
                weighted_score += response['score'] * weight
                total_weight += weight
        
        # 防止除以零
        if total_weight == 0:
            return 50.0  # 默認中等可信度
        
        return weighted_score / total_weight
    
    def self_verification(self, gemini_response: Dict[str, Any], content: str) -> Dict[str, Any]:
        """讓Gemini審查自己的回應"""
        verification_prompt = f"""
        請審查以下對信息的評估是否客觀、全面且有根據,必須要中文回應。
        
        原始信息：{content}
        
        評估結果：{json.dumps(gemini_response, ensure_ascii=False)}
        
        請指出評估中的任何問題、偏見或遺漏，並給出改進建議。
        請以JSON格式回應，包含以下字段：
        - verification_score: 對原評估的準確性評分(0-100)
        - issues: 發現的問題列表
        - suggestions: 改進建議列表
        - adjusted_credibility: 調整後的可信度評分(如有必要)
        """
        
        try:
            response = self.query_gemini_api(verification_prompt)
            
            # 解析回應文本
            if hasattr(response, 'text'):
                text = response.text
            elif hasattr(response, 'parts'):
                text = ' '.join([part.text for part in response.parts if hasattr(part, 'text')])
            else:
                text = str(response)
            
            # 嘗試提取JSON部分
            import re
            json_match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = text
            
            try:
                # 清理JSON字符串中可能的非法字符
                json_str = re.sub(r'[\x00-\x1F\x7F]', '', json_str)
                # 嘗試解析JSON
                verification_result = json.loads(json_str)
                return verification_result
            except json.JSONDecodeError:
                # 如果無法解析JSON，使用正則表達式提取關鍵信息
                verification_result = {
                    'verification_score': self.extract_score(text),
                    'issues': self.extract_list_items(text, 'issues'),
                    'suggestions': self.extract_list_items(text, 'suggestions'),
                    'adjusted_credibility': self.extract_adjusted_score(text)
                }
                return verification_result
                
        except Exception as e:
            logger.error(f"自我驗證過程發生錯誤: {e}")
            return {
                'verification_score': 50,
                'issues': ['自我驗證過程失敗'],
                'suggestions': ['重試或人工審核'],
                'adjusted_credibility': None
            }
    
    def extract_list_items(self, text: str, section_name: str) -> List[str]:
        """從文本中提取列表項目"""
        items = []
        section_pattern = rf'{section_name}.*?:(.*?)(?:\n\n|\Z)'
        section_match = re.search(section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if section_match:
            section_text = section_match.group(1)
            # 尋找列表項目
            items = re.findall(r'[-*]\s*(.*?)(?:\n|$)', section_text)
            if not items:  # 如果找不到列表格式，嘗試按行分割
                items = [line.strip() for line in section_text.split('\n') if line.strip()]
        
        return items
    
    def extract_adjusted_score(self, text: str) -> float:
        """從文本中提取調整後的評分"""
        pattern = r'adjusted_credibility.*?:\s*(\d+)'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return float(match.group(1))
        return None
    
    def multi_round_verification(self, content: str, initial_responses: Dict[str, Any]) -> Dict[str, Any]:
        """執行多輪驗證流程"""
        # 第一輪：基本評估
        initial_assessment = initial_responses
        
        # 第二輪：自我檢查
        verification_result = self.self_verification(initial_assessment, content)
        
        # 第三輪：最終評估
        final_assessment = self.generate_final_assessment(initial_assessment, verification_result, content)
        
        return final_assessment
    
    def generate_final_assessment(self, initial_assessment: Dict[str, Any], 
                                 verification_result: Dict[str, Any], 
                                 content: str) -> Dict[str, Any]:
        """生成最終評估報告"""
        # 獲取原始評分
        original_score = initial_assessment.get('integrated_score', 50)
        
        # 獲取調整後評分（如果有）
        adjusted_score = verification_result.get('adjusted_credibility')
        
        # 如果有調整評分，使用調整後的評分；否則使用原始評分
        final_score = adjusted_score if adjusted_score is not None else original_score
        
        # 確定可信度級別
        credibility_level = self.determine_credibility_level(final_score)
        
        # 構建最終報告
        final_report = {
            'content': content[:100] + '...' if len(content) > 100 else content,
            'credibility_score': final_score,
            'credibility_level': credibility_level,
            'verification_summary': {
                'original_assessment': {
                    'score': original_score,
                    'agreement_level': initial_assessment.get('agreement_level')
                },
                'self_verification': {
                    'verification_score': verification_result.get('verification_score'),
                    'issues': verification_result.get('issues', []),
                    'suggestions': verification_result.get('suggestions', [])
                }
            },
            'detailed_analysis': {
                angle: response.get('reasoning', '')
                for angle, response in initial_assessment.get('individual_responses', {}).items()
            },
            'timestamp': self.get_current_timestamp()
        }
        
        return final_report
    
    def determine_credibility_level(self, score: float) -> str:
        """根據評分確定可信度級別"""
        if score >= 90:
            return "高度可信"
        elif score >= 70:
            return "較為可信"
        elif score >= 50:
            return "部分可信"
        elif score >= 30:
            return "較低可信度"
        else:
            return "高度可疑"
    
    def get_current_timestamp(self) -> str:
        """獲取當前時間戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 使用示例
def main():
    # 創建驗證系統實例
    verification_system = GeminiVerificationSystem()
    
    # 測試信息
    test_content = """學者：難道「台積電」只有到中國投資，國民黨才不罵？
    記者李鴻典／台北報導

台積電將對美國再投資至少1000億美元（約新台幣3.3兆元），外界關注如何保留台灣半導體核心競爭力，甚至有聲音質疑台積電會變美積電；台積電董事長魏哲家近日跟總統賴清德共同召開記者會時說，美國投資計畫不會影響台灣投資，在台灣要蓋11條產線還是不夠，已請賴總統幫忙多找土地。學者范世平今（10）天則是表示，難道「台積電」只有到中國投資，國民黨才不罵？

台積電董事長魏哲家(右)近日跟總統賴清德(左)共同召開記者會。（圖／總統府提供）

▲台積電董事長魏哲家(右)近日跟總統賴清德(左)共同召開記者會。（圖／總統府提供）


范世平指出，自從魏哲家與川普在4日宣佈要在美國投資1000億美金後，包括趙少康、藍營名嘴與政治人物等，同一口徑的痛罵。他們說川普是個壞蛋，就是要把台灣的「護國神山」給整個挖走，掏空台灣的高科技；而「台積電」因為資金流向美國，會減少在台灣投資，讓台灣人才流失，造成經濟下滑與失業增加。過去美國稱中國若武力犯台會出兵保護，那是因為台灣有找半導體，現在沒了則美國會放棄台灣。

就像烏克蘭對美國沒有利用價值一樣，「今日烏克蘭就是明日台灣」，而賴清德就是澤倫斯基。何況這次「台積電」送給了美國，台灣沒有換到任何東西，美國並未提供提高防衛台灣的承諾。民進黨更是「喪事當喜事辦」的欺騙台灣人民，一昧美化這次「台積電」的投資美國案。姑且不論「台積電」現在正於美國投資的三個廠，順利的話最快也要在2029年才完工，川普的總統任期快結束，這次「台積電」要新設的3個廠，要到2038年才能完工，所以變數還很多。

更遑論就算「台積電」在美國的6個廠都生產，一年有216萬片的晶片，而去年「台積電」共生產1600萬片，所以美國廠只佔13.5%。如果「台積電」赴美投資就會變成「美積電」，那美商「美光」來台投資不就成了「台光」？「亞馬遜」在台投資不成了「台馬遜」？所以對於「台積電」赴美投資的過度焦慮與批評，恐怕就不是單純的杞人憂天了，背後是否有其他的政治目的？

范世平說，據了解，中共「中央統一戰線工作部」部長兼中央書記處書記石泰峰於2月24日召開特別會議，組建專案小組操作新一波對台的錯假認知攻勢。該小組由中央軍委會政治工作部、網路空間部隊與國家安全部等單位組成，目的是針對烏克蘭情勢與台灣半導體赴美投資等議題進行一系列認知操作。石泰峰在會議中強調，這波訊息操作對北京來說是「重中之重」，特別在中國對川普政策的走向仍高度不確定性時，「務必要讓台灣人『疑美恨川』（懷疑美國，痛恨川普），務必要讓島內裂痕又深又長」。

這次行動的目標是「讓美國人在想利用台灣的時候，台灣已經沒有人相信美國」。石泰峰強調此舉是「為了替國家爭取戰略空間」，「各部委務必全力動起來，當成一場真正的戰役來打！」。此次認知作戰重點放在推動新一波的「疑美論」、「棄台論」及「失敗論」三大敘事。操作方向包括「川普將出賣台灣」、「台積電將變成美積電」與「面對中國台灣終將失敗」等論述；透過中國官方媒體、社群平台與在台灣的協力名嘴、媒體與網路水軍假帳號系統在短時間內大量散佈。

范世平指出，在該會議中，國安部還提議將台灣民眾對川普的批評言論透過AI技術翻譯成英文，在X等英文社群平台上傳散，「讓川普以為台灣人都在罵他」，藉此離間台美關係。事實上，早在去年12月11日國台辦發言人朱鳳蓮就說「台積電」已成為民進黨當局討好美國的「投名狀」，死心塌地的「倚美謀獨」，「台積電」變成「美積電」是遲早的事。如果任由民進黨當局無底線「賣台」，台灣相關產業的優勢勢必遭到削弱，島內企業和民眾的利益勢必受到損害。

朱鳳蓮說，當台灣的利用價值被榨乾時，「棋子」就會淪為「棄子」，島內企業和民眾對此看得越來越清楚；眾多台灣企業通過參與兩岸合作得以快速發展，充分證明兩岸攜手共同壯大中華民族經濟，才是正道。這最後一句才是大實話，「台積電」投資美國是死路一條，只有投資中國，所以國民黨下一步就是要這麼說？完全與中國如出一轍？這當然會增加民眾支持「大罷免」國民黨立委的動力。

范世平拋出疑問，如果今天不是魏哲家與川普見面，而是韓國「三星集團」的會長李在鎔，國民黨又會罵這是台灣半導體不如韓國的象徵，台灣會被美國拋棄，不管如何隨時隨地都在配合中國的操作「疑美、棄台、失敗」論。事實上，美國會保護台灣絕非僅是因為晶片，還包括台灣是美國對抗中國的「第一島鏈」，直接攸關美國的國家安全；加上台灣是亞洲民主化的典範，與美國是價值同盟。所以一再唱衰台灣，對國民黨而言是有害無益。
    """
    
    # 執行驗證
    result = verification_system.verify_information(test_content)
    
    # 輸出結果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()