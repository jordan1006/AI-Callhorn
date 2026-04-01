"""
Podcast Parser - 提取音檔/文字關鍵邏輯，進行「Golden Patent」逆向溯源
"""

import re
import json
from datetime import datetime
from typing import Any


class PodcastParser:
    """Podcast 內容解析器"""
    
    def __init__(self):
        self.key_patterns = {
            "price_mention": r"(\$|價格|漲|跌|%)[0-9,.]+",
            "date_mention": r"(\d{1,2}/\d{1,2}|\d{4}-\d{2}-\d{2}|今天|明天|下週)",
            "name_mention": r"[A-Z][a-z]+(\s[A-Z][a-z]+)+",  # 人名/公司名
            "prediction": r"(預測|認為|可能|估計|看(好|衰))",
            "action": r"(買|賣|加碼|減碼|停損|停利)",
        }
        
    def parse_text(self, text: str) -> dict[str, Any]:
        """解析文字內容，提取關鍵邏輯"""
        return {
            "content": text,
            "extracted": {
                "price_mentions": self._extract_pattern(text, "price_mention"),
                "date_mentions": self._extract_pattern(text, "date_mention"),
                "name_mentions": self._extract_pattern(text, "name_mention"),
                "predictions": self._extract_pattern(text, "prediction"),
                "actions": self._extract_pattern(text, "action"),
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _extract_pattern(self, text: str, pattern_key: str) -> list[str]:
        """提取符合模式的內容"""
        pattern = self.key_patterns.get(pattern_key, "")
        if not pattern:
            return []
        return re.findall(pattern, text)
    
    def extract_logic_chain(self, parsed: dict) -> list[dict]:
        """從解析結果中提取邏輯鏈"""
        extracted = parsed.get("extracted", {})
        chain = []
        
        # 建立邏輯鏈：預測 -> 行動
        predictions = extracted.get("predictions", [])
        actions = extracted.get("actions", [])
        
        for i, pred in enumerate(predictions):
            action = actions[i] if i < len(actions) else None
            chain.append({
                "step": i + 1,
                "prediction": pred,
                "suggested_action": action
            })
        
        return chain


class GoldenPatent溯源器:
    """「黃金專利」逆向溯源器 - 追蹤資訊源頭"""
    
    def __init__(self):
        self.known_sources = {
            "FED": "https://www.federalreserve.gov/",
            "IMF": "https://www.imf.org/",
            "WB": "https://www.worldbank.org/",
            "CNBC": "https://www.cnbc.com/",
            "Bloomberg": "https://www.bloomberg.com/",
            "Reuters": "https://www.reuters.com/",
            "PTT": "https://www.ptt.cc/",
            "WSJ": "https://www.wsj.com/",
        }
        
    def trace_source(self, claim: str) -> dict[str, Any]:
        """
        逆向溯源 claim 的潛在來源
        這是一個簡化的實現
        """
        sources = []
        
        for source_name, source_url in self.known_sources.items():
            if source_name.lower() in claim.lower():
                sources.append({
                    "name": source_name,
                    "url": source_url,
                    "confidence": 0.8
                })
        
        return {
            "claim": claim,
            "potential_sources": sources,
            "trace_time": datetime.now().isoformat()
        }
    
    def validate_claim(self, claim: str, market_data: dict) -> dict[str, Any]:
        """
        驗證 claim 是否與市場數據一致
        回傳「已反應」或「未反應」狀態
        """
        # 簡化的實現：檢查claim是否與數據吻合
        validation = {
            "claim": claim,
            "consistent": True,  # 應該對比實際數據
            "priced_in": False,
            "confidence": 0.5,
            "notes": "需要實際市場數據對比"
        }
        
        return validation


class ReverseEngine:
    """逆向工程主類別"""
    
    def __init__(self):
        self.parser = PodcastParser()
        self溯源器 = GoldenPatent溯源器()
        
    def analyze(self, content: str) -> dict[str, Any]:
        """分析內容，輸出逆向工程報告"""
        parsed = self.parser.parse_text(content)
        logic_chain = self.parser.extract_logic_chain(parsed)
        
        # 對每個預測進行溯源
        source_traces = []
        predictions = parsed.get("extracted", {}).get("predictions", [])
        for pred in predictions:
            trace = self溯源器.trace_source(pred)
            source_traces.append(trace)
        
        return {
            "content": content,
            "parsed": parsed,
            "logic_chain": logic_chain,
            "source_traces": source_traces,
            "analysis_time": datetime.now().isoformat()
        }


async def main():
    """測試"""
    engine = ReverseEngine()
    
    sample = """
    今天FED主席鮑威爾說通膨壓力仍在，預計六月可能升息。
    我認為科技股會下跌，所以建議減碼NVDA和TSLA。
    不過黃金可能會漲，因為避險需求增加。
    """
    
    result = engine.analyze(sample)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
