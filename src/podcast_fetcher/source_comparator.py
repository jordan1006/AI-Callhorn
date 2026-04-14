"""
Source Comparator - 比對 游庭皓的財經皓角 資料來源與每日爬取資料的關係
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path


class SourceComparator:
    """來源比對器"""
    
    def __init__(self, transcript_dir: str = "./transcripts"):
        self.transcript_dir = transcript_dir
        
        # 定義資料來源對應的數據提供者和 API
        self.source_to_data = {
            "Federal Reserve/FED": {
                "data_source": "yfinance (TQQQ, ^DJI, ^GSPC)",
                "api": "Fed利率決策, 官網聲明",
                "frequency": "每6周FOMC"
            },
            "Bloomberg": {
                "data_source": "yfinance, 收盤數據",
                "api": "Bloomberg Terminal",
                "frequency": "即時"
            },
            "CNBC": {
                "data_source": "web fetch",
                "api": "CNBC官網",
                "frequency": "即時"
            },
            "Reuters": {
                "data_source": "web fetch",
                "api": "Reuters官網",
                "frequency": "即時"
            },
            "WSJ": {
                "data_source": "web fetch",
                "api": "WSJ官網",
                "frequency": "即時"
            },
            "IMF": {
                "data_source": "官方API",
                "api": "IMF Data",
                "frequency": "季度"
            },
            "World Bank": {
                "data_source": "官方API",
                "api": "World Bank API",
                "frequency": "季度"
            },
            "CNA/中央社": {
                "data_source": "web fetch",
                "api": "CNA官網",
                "frequency": "即時"
            },
            "經濟日報": {
                "data_source": "web fetch",
                "api": "經濟日报官網",
                "frequency": "每日"
            },
            "PTT": {
                "data_source": "PTT API / web scraper",
                "api": "PTT Stock板",
                "frequency": "即時"
            },
            "Yahoo Finance": {
                "data_source": "yfinance",
                "api": "Yahoo Finance",
                "frequency": "即時"
            },
            "MarketWatch": {
                "data_source": "web fetch",
                "api": "MarketWatch官網",
                "frequency": "即時"
            },
            "Seeking Alpha": {
                "data_source": "web fetch",
                "api": "Seeking Alpha",
                "frequency": "即時"
            }
        }
        
    def load_podcast_sources(self, video_id: str, date: str = None) -> Optional[dict]:
        """載入 podcast 來源分析"""
        if not date:
            date = datetime.now().strftime("%Y%m%d")
            
        filepath = f"{self.transcript_dir}/{video_id}_sources_{date}.json"
        
        if not os.path.exists(filepath):
            # 嘗試找最近的���案
            files = list(Path(self.transcript_dir).glob(f"{video_id}_sources_*.json"))
            if files:
                filepath = str(max(files, key=os.path.getmtime))
            else:
                return None
                
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def load_daily_sources(self) -> dict:
        """載入每日爬取的數據來源"""
        # 這個應該從 MCP server 或 dynamic_updater 取得
        # 簡化的版本：基於我們目前爬取的數據
        return {
            "yfinance_data": {
                "sources": ["Yahoo Finance"],
                "tickers": ["0050.TW", "TQQQ", "NVDA", "GC=F", "BTC-USD"],
                "frequency": "每日"
            },
            "ptt_data": {
                "sources": ["PTT"],
                "boards": ["Stock"],
                "frequency": "每日"
            },
            "economic_calendar": {
                "sources": ["經濟日報", "Bloomberg"],
                "frequency": "每日"
            }
        }
        
    def compare_sources(
        self, 
        podcast_sources: dict, 
        daily_sources: dict
    ) -> dict:
        """比對 podcast 來源與每日來源"""
        
        if not podcast_sources:
            return {"error": "No podcast sources loaded"}
            
        podcast_list = podcast_sources.get("sources", [])
        
        # 找出重疊
        overlapping = []
        podcast_only = []
        daily_only = []
        
        # 檢查每個 podcast 來源
        for source in podcast_list:
            source_lower = source.lower()
            
            # 檢查是否有對應的 daily 數據
            found_in_daily = False
            for daily_name, daily_info in daily_sources.items():
                daily_source_list = daily_info.get("sources", [])
                for ds in daily_source_list:
                    if ds.lower() in source_lower or source_lower in ds.lower():
                        overlapping.append({
                            "source": source,
                            "daily_category": daily_name,
                            "match_type": "exact"
                        })
                        found_in_daily = True
                        break
                        
            if not found_in_daily:
                podcast_only.append(source)
                
        # 檢查 daily 來源中哪些不在 podcast 中
        for daily_name, daily_info in daily_sources.items():
            for ds in daily_info.get("sources", []):
                ds_lower = ds.lower()
                matched = False
                for ps in podcast_list:
                    if ds_lower in ps.lower() or ps.lower() in ds_lower:
                        matched = True
                        break
                if not matched:
                    daily_only.append({
                        "source": ds,
                        "category": daily_name
                    })
                    
        return {
            "comparison_date": datetime.now().isoformat(),
            "podcast_sources": podcast_list,
            "overlapping_sources": overlapping,
            "podcast_only": podcast_only,
            "daily_only": daily_only,
            "coverage_rate": len(overlapping) / len(podcast_list) * 100 if podcast_list else 0
        }
        
    def generate_report(self, comparison: dict) -> str:
        """生成比對報告"""
        
        lines = []
        lines.append("=" * 60)
        lines.append("📊 資料來源比對報告")
        lines.append("=" * 60)
        lines.append(f"比對日期: {comparison.get('comparison_date', 'N/A')}")
        lines.append("")
        
        # 覆蓋率
        coverage = comparison.get("coverage_rate", 0)
        lines.append(f"📈 來源覆蓋率: {coverage:.1f}%")
        lines.append("")
        
        # 重疊來源
        if comparison.get("overlapping_sources"):
            lines.append("✅ 已有數據對應的來源:")
            for item in comparison["overlapping_sources"]:
                lines.append(f"   • {item['source']} → {item['daily_category']}")
            lines.append("")
            
        # Podcast 獨有來源
        if comparison.get("podcast_only"):
            lines.append("⚠️ Podcast 使用但我們未爬取的來源:")
            for source in comparison["podcast_only"]:
                lines.append(f"   • {source}")
            lines.append("")
            
        # Daily 獨有來源
        if comparison.get("daily_only"):
            lines.append("💡 我們有但 Podcast 未引用的來源:")
            for item in comparison["daily_only"]:
                lines.append(f"   • {item['source']} ({item['category']})")
            lines.append("")
            
        return "\n".join(lines)
        
    def run_comparison(self, video_id: str = None) -> dict:
        """執行完整比對"""
        
        # 預設使用最新的 video_id (需要從 podcast downloader 取得)
        if not video_id:
            # 嘗試找最新的 transcript 檔案
            files = list(Path(self.transcript_dir).glob("*_sources_*.json"))
            if files:
                # 從檔名取得 video_id
                filename = os.path.basename(max(files, key=os.path.getmtime))
                video_id = filename.split("_sources_")[0]
            else:
                return {"error": "No transcript files found"}
                
        # 載入 podcast 來源
        podcast_sources = self.load_podcast_sources(video_id)
        
        # 載入每日來源
        daily_sources = self.load_daily_sources()
        
        # 比對
        comparison = self.compare_sources(podcast_sources, daily_sources)
        
        # 生成報告
        print(self.generate_report(comparison))
        
        return comparison


def main():
    parser = argparse.ArgumentParser(
        description="比對 Podcast 資料來源與每日數據"
    )
    parser.add_argument(
        "--transcript-dir",
        default="./transcripts",
        help="Transcript directory"
    )
    parser.add_argument(
        "--video",
        help="Video ID"
    )
    
    args = parser.parse_args()
    
    comparator = SourceComparator(
        transcript_dir=args.transcript_dir
    )
    
    comparator.run_comparison(args.video)


if __name__ == "__main__":
    main()