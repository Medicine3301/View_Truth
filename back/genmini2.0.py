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
            model = genai.GenerativeModel('gemini-2.0-flash')
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
    test_content = """
    禁用碳纖維！歐盟最快 2029年上路
2025/04/15 11:15:00
記者鍾釗榛／綜合報導

歐盟最近丟出一顆震撼彈，根據最新草案，計畫把碳纖維列入「危險物質清單」！這項修正案一出，整個汽車產業炸鍋，尤其是靠碳纖維吃飯的跑車、電動車品牌，壓力山大。

碳纖維已經是泛用度很高的輕量化複合材料。（圖／TopCar Design翻攝）

▲碳纖維已經是泛用度很高的輕量化複合材料。（圖／TopCar Design翻攝）

碳纖維是什麼？它是輕量又超強韌的高階材料，跑車、超跑、甚至很多電動車品牌愛不釋手，因為它可以幫助車子「輕一點、跑更快、省能源」。但歐盟現在考慮把它當成危險物質，理由是碳纖維長絲可能會透過空氣飄散，進入人體造成健康風險，比如接觸皮膚或吸入呼吸道。

碳纖維輪圈也成為改裝界的聖品。（圖／翻攝Lamborghini）

▲碳纖維輪圈也成為改裝界的聖品。（圖／翻攝Lamborghini）

這項修正案目前被加進歐盟的《報廢汽車指令》修訂版本裡，一旦通過，最快 2029年上路，到時候各大車廠可能得開始「慢慢減少碳纖維的使用量」。根據統計，光是汽車製造業就吃掉全球碳纖維用量的20%，這變動對產業衝擊有多大可想而知。

Lamborghini採用碳纖維製造車架。（圖／翻攝Lamborghini）

▲Lamborghini採用碳纖維製造車架。（圖／翻攝Lamborghini）

這波消息一出，亞洲廠商反應超激烈。日本三大碳纖維龍頭，帝人、東麗、三菱化學，這幾天股價全受影響。因為他們三家就掌握了全球超過一半的碳纖維產量，如果歐盟市場限制使用，衝擊一定直接命中。

受影響最深的會是誰？當然是那些靠碳纖維撐起車身輕量化的超跑和電動車品牌，還有各種賽車的開發。他們近年來努力透過碳纖維減重、提升效能，這下子不只開發受阻，連製程都可能要大改。

禁止使用碳纖維將對汽車工業造成衝擊。（圖／TopCar Design翻攝）

▲禁止使用碳纖維將對汽車工業造成衝擊。（圖／TopCar Design翻攝）

雖然歐盟這麼做是出於環保與健康考量，但站在產業與車迷角度來看，這無疑是一場大地震。未來跑車還能這麼輕？電動車還能跑這麼遠？都可能被這條新規牽動。接下來幾年，碳纖維會不會從明星材料變成「高風險」素材？車廠怎麼應對、材料商如何轉型，勢必會成為汽車圈關注的焦點。
    """
    
    # 執行驗證
    result = verification_system.verify_information(test_content)
    
    # 輸出結果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()