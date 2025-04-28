import logging
import statistics
import json
import re
from typing import Dict, List, Any, Tuple
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
        以專業事實檢查員的身份，評估以下信息的可信度。請關注事實聲明、數據引用和可驗證的內容，必須要中文回應。

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
        請扮演信息評估專家，針對以下信息進行評估。如果是常識性陳述，請給予較高的可信度分數。必須要中文回應。

        信息內容：{content}

        評估指南：
        - 如果是普遍常識或基本事實，直接給予90分以上
        - 如果是科學常識且容易驗證，給予85分以上
        - 如果需要專業驗證，則根據具體情況評分

        請按以下格式回應：
        1. 信息性質：（說明是常識/科學事實/個人觀點/需要佐證的聲明等）
        2. 可驗證程度：（解釋這個信息多容易被驗證）
        3. 評估結果：（根據信息性質給出相應評估）
        4. 可信度評分：（0-100分，常識類信息如能自我驗證可給予較高分數）
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
        """從回應文本中提取可信度評分，改進版"""
        try:
            # 匹配更精確的評分模式
            patterns = [
                r'可信度評分[：:]\s*(\d+(?:\.\d+)?)',
                r'評分[：:]\s*(\d+(?:\.\d+)?)',
                r'score[：:]\s*(\d+(?:\.\d+)?)',
                r'(\d+(?:\.\d+)?)\s*分'
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                scores = []
                for match in matches:
                    try:
                        score = float(match.group(1))
                        if 0 <= score <= 100:  # 確保分數在有效範圍內
                            scores.append(score)
                    except ValueError:
                        continue
                
                if scores:
                    # 如果找到多個分數，取中位數避免極端值
                    return statistics.median(scores)
            
            # 如果沒有找到有效分數，進行文本分析
            text_lower = text.lower()
            if "高度可信" in text_lower or "非常可靠" in text_lower:
                return 90.0
            elif "較為可信" in text_lower or "比較可靠" in text_lower:
                return 75.0
            elif "一般" in text_lower or "中等" in text_lower:
                return 60.0
            elif "較不可信" in text_lower or "不太可靠" in text_lower:
                return 40.0
            elif "不可信" in text_lower or "不可靠" in text_lower:
                return 20.0
            
            return 50.0  # 默認中等可信度
            
        except Exception as e:
            logger.error(f"提取評分時發生錯誤: {e}")
            return 50.0

    def calculate_weighted_score(self, responses: Dict[str, Any]) -> float:
        """計算加權評分，改進版"""
        try:
            # 設定不同角度的權重
            weights = {
                'factual': 0.35,    # 重視事實檢查
                'critical': 0.30,   # 重視批判性分析
                'balanced': 0.20,   # 平衡視角
                'source': 0.15      # 來源可靠性
            }
            
            scores = {}
            total_weight = 0
            weighted_sum = 0
            
            # 收集所有有效分數
            for angle, response in responses.items():
                if angle in weights and 'score' in response:
                    score = float(response['score'])
                    if 0 <= score <= 100:  # 驗證分數範圍
                        scores[angle] = score
                        weight = weights[angle]
                        weighted_sum += score * weight
                        total_weight += weight
            
            # 檢查是否有足夠的有效分數
            if not scores:
                logger.warning("沒有找到有效的評分")
                return 50.0
            
            if total_weight == 0:
                logger.warning("總權重為零")
                return statistics.mean(scores.values())
            
            # 計算加權平均
            final_score = weighted_sum / total_weight
            
            # 加入分數調整邏輯
            if any(score < 20 for score in scores.values()):
                # 如果任何角度的分數特別低，降低最終分數
                final_score *= 0.8
            elif all(score > 80 for score in scores.values()):
                # 如果所有角度都很高分，稍微提升最終分數
                final_score = min(100, final_score * 1.1)
            
            return round(final_score, 1)
            
        except Exception as e:
            logger.error(f"計算加權分數時發生錯誤: {e}")
            return 50.0
    
    def self_verification(self, gemini_response: Dict[str, Any], content: str) -> Dict[str, Any]:
        """讓Gemini審查自己的回應，並生成使用者友善的建議"""
        verification_prompt = f"""
        請審查以下信息的評估結果，並提供對一般讀者有幫助的建議。必須要以中文回應。
        
        原始信息：{content}
        
        評估結果：{json.dumps(gemini_response, ensure_ascii=False)}
        
        請提供以下內容：
        1. 閱讀建議：
           - 提供3-5點具體的查證建議
           - 使用日常用語
           - 避免專業術語
           - 重點提示需要特別注意的地方
        
        2. 注意事項：
           - 列出閱讀此新聞時需要注意的重點
           - 提醒可能存在的偏見或誤導
           - 建議如何分辨真實性
           - 提供實用的驗證方法
        
        請以JSON格式回應，包含以下字段：
        - verification_score: 對原評估的準確性評分(0-100)
        - suggestions: 實用的閱讀建議列表（用一般民眾能理解的語言）
        - issues: 需要注意的重點列表（簡單易懂的提醒）
        - adjusted_credibility: 調整後的可信度評分
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
    
    def extract_date(self, content: str) -> str:
        """從內容中提取日期"""
        try:
            # 使用正則表達式匹配常見的日期格式
            date_patterns = [
                r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日號]?',  # 2023-01-01 or 2023年01月01日
                r'\d{1,2}[-/月]\d{1,2}[日號]?, \d{4}',      # 01-01, 2023
                r'\d{4}[-/.]\d{2}[-/.]\d{2}'                # 2023.01.01
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, content)
                if match:
                    return match.group(0)
            
            return None
        except Exception:
            return None

    def extract_location(self, content: str) -> str:
        """從內容中提取地點信息"""
        try:
            # 常見地點標記詞
            location_markers = ['在', '於', '地點', '位於', '發生於']
            
            for marker in location_markers:
                pattern = f"{marker}([^，。；,;\n]+)"
                match = re.search(pattern, content)
                if match:
                    return match.group(1).strip()
            
            return None
        except Exception:
            return None

    def extract_involved_parties(self, content: str) -> List[str]:
        """從內容中提取當事人信息"""
        try:
            parties = []
            # 尋找可能的當事人標記
            party_patterns = [
                r'([\u4e00-\u9fff]{2,4})(?:先生|小姐|女士)',
                r'([\u4e00-\u9fff]+)(?:表示|說|稱|指出)',
                r'當事人([\u4e00-\u9fff]+)',
                r'([\u4e00-\u9fff]+)方面'
            ]
            
            for pattern in party_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    party = match.group(1).strip()
                    if party and party not in parties:
                        parties.append(party)
            
            return parties if parties else None
        except Exception:
            return None

    def determine_credibility_level(self, score: float) -> str:
        """根據分數確定可信度級別"""
        if score >= 90:
            return "高度可信"
        elif score >= 70:
            return "較為可信"
        elif score >= 50:
            return "中等可信"
        elif score >= 30:
            return "較不可信"
        else:
            return "低度可信"

    def determine_event_type(self, content: str) -> str:
        """自動判斷事件類型"""
        prompt = f"""
        請分析以下內容的事件類型，從以下類別中選擇最相符的一個：
        社會事件、政治事件、經濟財經、科技新知、教育文化、醫療衛生、
        生活消費、環境生態、體育運動、娛樂新聞、國際新聞、其他
        
        如果是常識性陳述，請標記為"常識性內容"。

        內容：{content}

        請直接回覆單一類型，無需解釋。
        """
        
        try:
            response = self.query_gemini_api(prompt)
            event_type = response.text.strip() if hasattr(response, 'text') else str(response).strip()
            return event_type
        except Exception as e:
            logger.error(f"判斷事件類型時發生錯誤: {e}")
            return "其他"

    def extract_basic_info(self, content: str) -> Tuple[str, str, Dict[str, Any]]:
        """從內容中提取標題、摘要和基本信息"""
        lines = content.strip().split('\n')
        title = next((line.strip() for line in lines if line.strip()), "無標題")
        
        summary_lines = [line.strip() for line in lines if line.strip() 
                        and not line.startswith('Q') 
                        and not line.startswith('A')
                        and not line.startswith('PR')
                        and not line.startswith('Recommended')]
        summary = ' '.join(summary_lines[:2])
        
        # 使用新的自動判斷事件類型方法
        event_type = self.determine_event_type(content)
        
        basic_info = {
            "發生時間": self.extract_date(content) or "未知",
            "地點": self.extract_location(content) or "未知",
            "當事人": self.extract_involved_parties(content) or [],
            "事件類型": event_type
        }
        
        return title, summary, basic_info

    def improve_title_and_content(self, title: str, content: str) -> Tuple[str, str]:
        """改進標題和內容的呈現品質"""
        prompt = f"""
        請分析並改進以下新聞的標題和內容。保持原意的前提下，提供更客觀、準確的表達方式。必須要中文回應。

        原標題：{title}
        原內容：{content}

        請提供：
        1. 改進後的標題：（更客觀、清晰的標題）
        2. 改進後的內容：（去除誇張、偏見的描述，保持事實陳述）

        回覆格式：
        標題：改進後的標題
        內容：改進後的內容
        """

        try:
            response = self.query_gemini_api(prompt)
            text = response.text if hasattr(response, 'text') else str(response)

            # 提取改進後的標題
            title_match = re.search(r'標題：(.+?)(?:\n|$)', text)
            improved_title = title_match.group(1).strip() if title_match else title

            # 提取改進後的內容
            content_match = re.search(r'內容：(.+?)(?=\Z)', text, re.DOTALL)
            improved_content = content_match.group(1).strip() if content_match else content

            return improved_title, improved_content
        except Exception as e:
            logger.error(f"改進標題和內容時發生錯誤: {e}")
            return title, content

    def generate_final_assessment(self, initial_assessment: Dict[str, Any],
                                verification_result: Dict[str, Any],
                                content: str) -> Dict[str, Any]:
        """生成最終評估報告，符合資料庫結構"""
        try:
            # 提取基本信息
            title, summary, basic_info = self.extract_basic_info(content)
            
            # 改進標題和內容
            improved_title, improved_content = self.improve_title_and_content(title, content)
            
            final_score = initial_assessment.get('integrated_score', 50)
            analyses = initial_assessment.get('individual_responses', {})
            
            # 構建符合資料庫結構的報告
            final_report = {
                "title": improved_title,
                "content": improved_content,
                "publish_date": basic_info["發生時間"],
                "location": basic_info["地點"],
                "event_type": basic_info["事件類型"],
                
                "credibility_score": float(final_score),
                "credibility_level": self.determine_credibility_level(final_score),
                "factual_score": float(analyses.get('factual', {}).get('score', 0)),
                "critical_score": float(analyses.get('critical', {}).get('score', 0)),
                "balanced_score": float(analyses.get('balanced', {}).get('score', 0)),
                "source_score": float(analyses.get('source', {}).get('score', 0)),
                
                "factual_analysis": {
                    "findings": self.extract_key_findings(analyses.get('factual', {}).get('reasoning', '')),
                    "basis": self.extract_main_basis(analyses.get('factual', {}).get('reasoning', ''))
                },
                
                "critical_analysis": {
                    "problems": self.extract_problems(analyses.get('critical', {}).get('reasoning', '')),
                    "logical_fallacies": self.extract_logical_fallacies(analyses.get('critical', {}).get('reasoning', ''))
                },
                
                "balanced_analysis": {
                    "supporting_points": self.extract_supporting_points(analyses.get('balanced', {}).get('reasoning', '')),
                    "opposing_points": self.extract_opposing_points(analyses.get('balanced', {}).get('reasoning', ''))
                },
                
                "source_analysis": {
                    "reliability": self.extract_source_reliability(analyses.get('source', {}).get('reasoning', '')),
                    "requirements": self.extract_verification_requirements(analyses.get('source', {}).get('reasoning', ''))
                },
                
                "verification_guide": {
                    "suggestions": verification_result.get('suggestions', []),
                    "issues": verification_result.get('issues', [])
                },
                
                "involved_parties": basic_info["當事人"],
                "version": "1.0",
                "system_info": {
                    "name": "Gemini Verification System",
                    "timestamp": self.get_current_timestamp()
                }
            }
            
            return final_report
            
        except Exception as e:
            logger.error(f"生成最終報告時發生錯誤: {e}")
            raise

    def extract_key_findings(self, text: str) -> List[str]:
        """提取關鍵發現"""
        findings = []
        # 尋找關鍵事實聲明部分
        pattern = r'關鍵事實聲明[：:](.*?)(?=\d\.|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # 分割並清理每個發現
            raw_findings = match.group(1).split('\n')
            findings = [f.strip('- *').strip() for f in raw_findings if f.strip()]
        return findings or ["無法提取關鍵發現"]

    def extract_main_basis(self, text: str) -> List[str]:
        """提取主要依據"""
        basis = []
        # 尋找評分理由部分
        pattern = r'評分理由[：:](.*?)(?=\Z)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # 分割並清理每個依據
            raw_basis = match.group(1).split('\n')
            basis = [b.strip('- *').strip() for b in raw_basis if b.strip()]
        return basis or ["無法提取評分依據"]

    def extract_problems(self, text: str) -> List[str]:
        """提取問題點 - 對應資料庫 critical_analysis 欄位
        
        從批判性分析中提取潛在問題清單。這些問題將被存儲在資料庫的 critical_analysis JSON欄位中。
        
        資料庫對應：
        - critical_analysis (JSON): {
            "problems": [...提取的問題列表...],
            "logical_fallacies": [...邏輯謬誤列表...]
        }
        
        Returns:
            List[str]: 提取出的問題列表，每個問題為一個字符串
        """
        problems = []
        # 使用中文冒號匹配，避免遺漏
        pattern = r'潛在問題點[：:](.*?)(?=\d\.|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # 分割並清理每個問題，移除標點符號和特殊字符
            raw_problems = match.group(1).split('\n')
            problems = [p.strip('- *。，：').strip() for p in raw_problems if p.strip()]
            
            # 確保每個問題都有意義且長度合適
            problems = [p for p in problems if len(p) > 5 and len(p) < 500]
            
        # 如果沒有找到有效的問題，返回預設值
        return problems or ["無法提取問題點，需要人工覆核"]

    def extract_logical_fallacies(self, text: str) -> List[str]:
        """提取邏輯謬誤 - 對應資料庫 critical_analysis 欄位
        
        從批判性分析中提取邏輯謬誤。這些謬誤將被存儲在資料庫的 critical_analysis JSON欄位中。
        
        資料庫對應：
        - critical_analysis (JSON): {
            "problems": [...問題列表...],
            "logical_fallacies": [...提取的邏輯謬誤列表...]
        }
        
        Returns:
            List[str]: 提取出的邏輯謬誤列表，每個謬誤為一個字符串
        """
        fallacies = []
        # 使用更精確的模式匹配邏輯分析部分
        pattern = r'邏輯分析[：:](.*?)(?=\d\.|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # 分割並清理每個謬誤，確保資料品質
            raw_fallacies = match.group(1).split('\n')
            fallacies = [f.strip('- *。，：').strip() for f in raw_fallacies if f.strip()]
            
            # 過濾無效或過短的謬誤描述
            fallacies = [f for f in fallacies if len(f) > 5 and len(f) < 500]
        
        # 如果沒有找到有效的邏輯謬誤，返回預設值
        return fallacies or ["需要進一步分析邏輯謬誤"]

    def extract_supporting_points(self, text: str) -> List[str]:
        """提取支持論點"""
        points = []
        # 尋找支持觀點部分
        pattern = r'支持觀點[：:](.*?)(?=\d\.|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # 分割並清理每個論點
            raw_points = match.group(1).split('\n')
            points = [p.strip('- *').strip() for p in raw_points if p.strip()]
        return points or ["無法提取支持論點"]

    def extract_opposing_points(self, text: str) -> List[str]:
        """提取反對論點"""
        points = []
        # 尋找反對觀點部分
        pattern = r'反對觀點[：:](.*?)(?=\d\.|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # 分割並清理每個論點
            raw_points = match.group(1).split('\n')
            points = [p.strip('- *').strip() for p in raw_points if p.strip()]
        return points or ["無法提取反對論點"]

    def extract_source_reliability(self, text: str) -> Dict[str, Any]:
        """提取來源可靠性分析"""
        reliability = {
            "level": "未知",
            "reason": "無法確定來源可靠性"
        }
        # 尋找信息性質部分
        pattern = r'信息性質[：:](.*?)(?=\d\.|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            reliability["level"] = "可靠" if "可靠" in content else "部分可靠" if "部分" in content else "不可靠"
            reliability["reason"] = content
        return reliability

    def extract_verification_requirements(self, text: str) -> List[str]:
        """提取驗證要求"""
        requirements = []
        # 尋找來源必要性部分
        pattern = r'來源必要性[：:](.*?)(?=\d\.|\Z)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # 分割並清理每個要求
            raw_requirements = match.group(1).split('\n')
            requirements = [r.strip('- *').strip() for r in raw_requirements if r.strip()]
        return requirements or ["需要進一步驗證"]

    def get_current_timestamp(self) -> str:
        """獲取當前時間戳"""
        from datetime import datetime
        return datetime.now().isoformat()

    def integrate_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """整合多角度回應並計算最終評分
        
        Args:
            responses: 包含不同角度評估結果的字典。包括：
                - factual: 事實查核角度的評估
                - critical: 批判性思考角度的評估
                - balanced: 平衡觀點角度的評估
                - source: 來源可靠性角度的評估
            
        Returns:
            Dict[str, Any]: 整合後的結果，包含：
                - integrated_score: 最終綜合評分
                - agreement_level: 各角度評分的一致性程度
                - score_variance: 評分的變異數
                - standard_deviation: 評分的標準差
                - individual_responses: 各角度的原始回應
                - reasoning_summary: 各角度的評分理由摘要
                - analysis: 整體分析結果，包含可信度和共識度
        """
        try:
            logger.info("開始整合多角度回應...")
            
            # 步驟1: 計算加權評分 - 使用預設權重計算最終分數
            final_score = self.calculate_weighted_score(responses)
            logger.info(f"計算出的加權評分: {final_score}")
            
            # 步驟2: 收集所有有效的評分，用於統計分析
            scores = [response.get('score', 0) for response in responses.values() 
                     if isinstance(response, dict)]
            
            # 步驟3: 計算統計指標
            # - variance: 評分的離散程度，數值越大表示評分差異越大
            # - std_dev: 標準差，用於評估評分的一致性
            variance = statistics.variance(scores) if len(scores) > 1 else 0
            std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
            
            # 步驟4: 根據標準差判定評分的一致性水平
            # 標準差越小表示評分越一致
            agreement_level = self._determine_agreement_level(std_dev)
            
            # 步驟5: 收集各角度的具體分析理由
            reasoning = {}
            for angle, response in responses.items():
                if isinstance(response, dict):
                    reasoning[angle] = {
                        'score': response.get('score', 0),  # 該角度的評分
                        'explanation': response.get('reasoning', '無分析說明')  # 評分理由
                    }
            
            # 步驟6: 組織最終的整合結果
            integrated_result = {
                'integrated_score': final_score,  # 最終加權評分
                'agreement_level': agreement_level,  # 評分一致性程度
                'score_variance': variance,  # 評分變異數
                'standard_deviation': std_dev,  # 評分標準差
                'individual_responses': responses,  # 原始回應
                'reasoning_summary': reasoning,  # 各角度評分理由
                'analysis': {
                    # 根據標準差和評分數量計算的置信水平
                    'confidence': self._calculate_confidence_level(std_dev, len(scores)),
                    # 根據回應完整性和評分水平判斷的可靠性
                    'reliability': self._assess_reliability(responses),
                    # 各角度評分的一致程度
                    'consensus': agreement_level
                }
            }
            
            logger.info("多角度回應整合完成")
            return integrated_result
            
        except Exception as e:
            logger.error(f"整合回應時發生錯誤: {str(e)}")
            # 發生錯誤時返回基本的錯誤響應
            return {
                'integrated_score': 50.0,  # 出錯時給予中等評分
                'error': str(e),  # 錯誤信息
                'status': 'error',  # 錯誤狀態標記
                'individual_responses': responses  # 原始回應
            }
    
    def _determine_agreement_level(self, std_dev: float) -> str:
        """根據標準差確定評分一致性水平"""
        if std_dev < 5:
            return "高度一致"
        elif std_dev < 10:
            return "較為一致"
        elif std_dev < 15:
            return "部分一致"
        else:
            return "意見分歧"
    
    def _calculate_confidence_level(self, std_dev: float, num_scores: int) -> str:
        """計算評估結果的置信水平"""
        if num_scores < 2:
            return "低度置信"
        elif std_dev > 20:
            return "低度置信"
        elif std_dev > 10:
            return "中度置信"
        else:
            return "高度置信"
    
    def _assess_reliability(self, responses: Dict[str, Any]) -> str:
        """評估整體可靠性
        
        基於多個評估角度的回應來判斷整體可信度，通過檢查必要評估角度的完整性
        以及評分的平均值來確定可靠性等級。
        
        Args:
            responses (Dict[str, Any]): 包含各個評估角度的回應結果
                - factual: 事實檢查的評估結果
                - critical: 批判性分析的評估結果
                - balanced: 平衡性分析的評估結果
                - source: 來源可靠性的評估結果
        
        Returns:
            str: 返回可靠性評級，可能的值包括：
                - "可靠性待確認": 缺少必要的評估角度
                - "可靠性無法評估": 沒有有效的評分數據
                - "高度可靠": 平均評分 >= 80
                - "較為可靠": 平均評分 >= 60
                - "一般可靠": 平均評分 >= 40
                - "可靠性存疑": 平均評分 < 40
        """
        try:
            # 定義系統要求的所有必要評估角度
            required_angles = {'factual', 'critical', 'balanced', 'source'}
            # 獲取實際可用的評估角度
            available_angles = set(responses.keys())
            
            # 檢查是否所有必要的評估角度都存在
            if not required_angles.issubset(available_angles):
                return "可靠性待確認"
            
            # 從所有有效的回應中提取評分
            # 使用列表推導式，只收集字典類型的回應中的評分
            scores = [response.get('score', 0) 
                     for response in responses.values() 
                     if isinstance(response, dict)]
            
            # 如果沒有收集到任何評分，返回無法評估
            if not scores:
                return "可靠性無法評估"
            
            # 計算所有評分的平均值
            avg_score = statistics.mean(scores)
            
            # 根據平均分數返回對應的可靠性等級
            if avg_score >= 80:
                return "高度可靠"
            elif avg_score >= 60:
                return "較為可靠"
            elif avg_score >= 40:
                return "一般可靠"
            else:
                return "可靠性存疑"
                
        except Exception:
            return "可靠性評估失敗"


# 使用示例
def main():
    # 創建驗證系統實例
    verification_system = GeminiVerificationSystem()
    
    # 測試信息
    test_content = """
今年「第1波梅雨鋒面」要來了！雨彈恐連炸6天　氣象專家示警了
2025/04/27 05:26:00
早知道「除斑」這麼簡單就好，我還做什麼雷射！屈臣氏爆賣中
PR
中國歷史有1500年「空白期」，沒有任何史料記載，究竟發生了什麼？
鋒面到！「梅雨訊號」提早一個月出現　鄭明典驚：太早了
輕食、運動，辛苦健康未必有感？這瓶複方多效97%讚
PR
Recommended by 
生活中心／張家寧報導

氣象專家預告即將告別春雨、迎接梅雨。（圖／翻攝自臉書）

▲氣象專家預告即將告別春雨、迎接梅雨。（圖／翻攝自臉書）

氣象署指出，今（２７）日東北季風減弱，北部、東北部及東部氣溫回升；基隆北海岸、臺灣東北部及東部地區有局部短暫陣雨，東北部地區仍有局部較大雨勢發生的機率。有氣象專家透過臉書發文預告「告別春雨、迎接梅雨！」

氣象專家林得恩今早透過臉書粉專「林老師氣象站」發文表示，在每年5、6月的春夏季節更迭，冬季北方大陸冷高壓逐漸減弱，而夏天盛行的太平洋高壓則逐漸增強，並進一步影響到我們，天氣也開始轉為酷熱。

林得恩指出，當這2股冷氣團與暖氣團勢力相當，互相增長、衰退與推擠，在中國大陸南方的長江流域、江淮地區、臺灣、日本中南部和韓國南部等地上空形成一條滯留界面，我們就稱為「梅雨鋒面」；由於伴隨梅雨鋒面上常有組織性的中尺度對流系統發展，當它們從海上移入到臺灣陸地時，常會帶來局部強降雨以及雷暴、強陣風或冰雹等劇烈天氣現象。 

林得恩提到，根據中央氣象署系集模式最新模擬結果顯示，5/5至5/10期間，出現日降雨量指標有較強且持續的降雨訊號，「有可能就是今年第1波梅雨鋒面所肇致的結果」。
    """
    
    # 執行驗證
    result = verification_system.verify_information(test_content)
    
    # 輸出結果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()