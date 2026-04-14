"""
Enhanced Source Extractor - 自動分析每段內容的可能來源
透過關鍵字匹配 + 網路搜尋推斷來源
"""

import json
import re
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional

# 定義來源關鍵字庫
SOURCE_KEYWORDS = {
    # 央行/政府
    "Federal Reserve/FED": {
        "keywords": ["Fed", "聯準會", "鮑威爾", "葉倫", "FOMC", "美國聯邦準備", "利率", "縮表", " QE", "QT"],
        "data_sources": ["yfinance (FED funds)", "Fed官網"],
        "frequency": "每6周"
    },
    "台灣央行": {
        "keywords": ["央行", "楊金龙", "新青安", "房貸利率", "選擇性信用管制"],
        "data_sources": ["央行官網", "法說會"],
        "frequency": "每日"
    },
    "美國勞工部": {
        "keywords": ["非農", "就業報告", "CPI", "PCE", "物價", "勞動市場"],
        "data_sources": ["BLS.gov", "yfinance"],
        "frequency": "每月"
    },
    "IMF": {
        "keywords": ["IMF", "國際貨幣基金", "全球GDP", "世界經濟展望"],
        "data_sources": ["IMF Data"],
        "frequency": "季度"
    },
    "WTO": {
        "keywords": ["WTO", "全球貿易", "關稅", "貿易戰"],
        "data_sources": ["WTO官網"],
        "frequency": "季度"
    },
    "Bloomberg": {
        "keywords": ["Bloomberg", "彭博", "Bloomberg intelligence"],
        "data_sources": ["yfinance, Bloomberg Terminal"],
        "frequency": "即時"
    },
    "Reuters": {
        "keywords": ["路透", "Reuters", "路透社"],
        "data_sources": ["Reuters官網"],
        "frequency": "即時"
    },
    "WSJ": {
        "keywords": ["華爾街日报", "WSJ", "Wall Street Journal"],
        "data_sources": ["WSJ官網"],
        "frequency": "即時"
    },
    "PTT": {
        "keywords": ["PTT", "批踢踢", "ptt.cc", "鄉民"],
        "data_sources": ["PTT Stock板"],
        "frequency": "即時"
    },
    "Seeking Alpha": {
        "keywords": ["Seeking Alpha", "分析師"],
        "data_sources": ["Seeking Alpha"],
        "frequency": "即時"
    },
    # 數據來源
    "VIX": {
        "keywords": ["VIX", "恐慌指數", "芝加哥選擇權交易所"],
        "data_sources": ["CBOE", "yfinance (^VIX)"],
        "frequency": "即時"
    },
    "黃金/白銀": {
        "keywords": ["黃金", "白銀", "貴金屬", "GC=F", "SI=F"],
        "data_sources": ["yfinance (GC=F, SI=F)", "CME"],
        "frequency": "即時"
    },
    "原油": {
        "keywords": ["原油", "石油", "WTI", "Brent", "CL=F"],
        "data_sources": ["yfinance (CL=F)", "EIA"],
        "frequency": "即時"
    },
    "比特幣": {
        "keywords": ["比特幣", "BTC", "比特幣ETF"],
        "data_sources": ["yfinance (BTC-USD)", "Coinbase"],
        "frequency": "即時"
    },
    "半導體": {
        "keywords": ["台積電", "輝達", "NVIDIA", "英特爾", "AMD", "費城半導體", "SOX"],
        "data_sources": ["yfinance", "納斯達克"],
        "frequency": "即時"
    },
    "美股ETF": {
        "keywords": ["TQQQ", "SPY", "QQQ", "VOO", "IVV"],
        "data_sources": ["yfinance"],
        "frequency": "即時"
    },
}


class EnhancedSourceExtractor:
    """增強來源分析器"""
    
    def __init__(self, transcript_path: str):
        self.transcript_path = transcript_path
        self.transcript = []
        self.paragraphs = []
        
    def load(self):
        """載入逐字稿"""
        with open(self.transcript_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.transcript = data.get('transcript', [])
        
        # 清理並分段落
        self._process_paragraphs()
        
    def _process_paragraphs(self):
        """處理段落"""
        current_para = {'start': 0, 'text': '', 'source': None}
        min_duration = 3  # 至少3秒的內容
        
        for item in self.transcript:
            text = item.get('text', '').strip()
            if not text or len(text) < 3:
                continue
                
            # 過濾笑声和雜訊
            if any(x in text.lower() for x in ['哈哈', '嘿嘿', 'xd', '笑']):
                if len(text) < 8:
                    continue
                    
            # 這是一個新段落
            if len(text) > 30 or any(c in text for c in '.。'):
                text_to_add = current_para['text'] + ' ' + text if current_para['text'] else text
                current_para['text'] = text_to_add.strip()
                current_para['start'] = item.get('start', 0)
            else:
                text_to_add = current_para['text'] + ' ' + text if current_para['text'] else text
                current_para['text'] = text_to_add.strip()
                
        # 加入最後一個段落
        if current_para['text']:
            self.paragraphs.append(current_para)
            
    def analyze_sources(self) -> Dict:
        """分析每個段落的來源"""
        results = {
            'total_paragraphs': len(self.paragraphs),
            'sources_found': defaultdict(list),
            'paragraphs': []
        }
        
        for para in self.paragraphs:
            text = para.get('text', '')
            start = para.get('start', 0)
            
            # 搜尋關鍵字
            found_sources = []
            for source_name, config in SOURCE_KEYWORDS.items():
                for keyword in config['keywords']:
                    if keyword in text:
                        found_sources.append(source_name)
                        results['sources_found'][source_name].append({
                            'paragraph': text[:100],
                            'start': start,
                            'keyword': keyword
                        })
                        break
            
            results['paragraphs'].append({
                'start': start,
                'text': text,
                'sources': found_sources,
                'data_sources': [SOURCE_KEYWORDS[s]['data_sources'][0] for s in found_sources if s in SOURCE_KEYWORDS]
            })
            
        return results
        
    def generate_report(self) -> str:
        """生成報告"""
        results = self.analyze_sources()
        
        lines = []
        lines.append("=" * 70)
        lines.append("📊 早晨財經速解讀 - 來源分析報告")
        lines.append("=" * 70)
        lines.append(f"總段落數: {results['total_paragraphs']}")
        lines.append("")
        
        # 來源統計
        lines.append("📌 來源統計:")
        lines.append("-" * 40)
        
        source_stats = defaultdict(int)
        for source, items in results['sources_found'].items():
            source_stats[source] = len(items)
            
        for source, count in sorted(source_stats.items(), key=lambda x: -x[1]):
            config = SOURCE_KEYWORDS.get(source, {})
            data_source = config.get('data_sources', ['N/A'])[0]
            lines.append(f"  {source}: {count}次")
            lines.append(f"    → 資料來源: {data_source}")
            lines.append(f"    → 更新頻率: {config.get('frequency', 'N/A')}")
            lines.append("")
            
        # 段落樣本
        lines.append("📝 段落樣本 (每個來源最多3個):")
        lines.append("-" * 40)
        
        shown = defaultdict(int)
        for para in results['paragraphs']:
            for src in para['sources']:
                if shown[src] < 3:
                    lines.append(f"[{src}]")
                    lines.append(f"  {para['text'][:150]}")
                    lines.append("")
                    shown[src] += 1
                    
        # 與我們爬的數據對比
        lines.append("")
        lines.append("🔗 與系統數據對比:")
        lines.append("-" * 40)
        
        our_data_sources = {
            'yfinance': ['0050.TW', 'TQQQ', 'NVDA', 'GC=F', 'CL=F', 'BTC-USD'],
            'PTT': ['Stock板熱門'],
            'Fed': ['利率決策'],
        }
        
        for src, count in source_stats.items():
            if src in ['Federal Reserve/FED', 'VIX', '黃金/白銀', '原油', '半導體']:
                line = f"  ✅ {src}: 我們有爬取 ({our_data_sources.get(src.split('/')[0], ['N/A'])[0]})"
            else:
                line = f"  ⚠️ {src}: 需要新增"
            lines.append(line)
            
        return "\n".join(lines)


def main():
    extractor = EnhancedSourceExtractor('./transcripts/_CPEVxMZAe4_20260414.json')
    extractor.load()
    
    # 生成報告
    report = extractor.generate_report()
    print(report)
    
    # 儲存 JSON
    results = extractor.analyze_sources()
    output_path = './transcripts/_CPEVxMZAe4_sources_enhanced_20260414.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Enhanced report saved to: {output_path}")


if __name__ == "__main__":
    main()