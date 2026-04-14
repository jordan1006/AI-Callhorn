"""
Podcast Fetcher - 每日自動抓取 游庭皓的財經皓角 節目逐字稿
使用方法:
    python podcast_downloader.py --channel UC0lbAQVpenvfA2QqzsRtL_g --output ./transcripts
"""

import os
import json
import argparse
from datetime import datetime, timedelta
from typing import Optional
import re

# Try to import youtube-transcript-api, fall back to manual method
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("youtube-transcript-api not available, using alternative method...")


class PodcastDownloader:
    """Podcast 下載器"""
    
    def __init__(self, channel_id: str, output_dir: str = "./transcripts"):
        self.channel_id = channel_id
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 財經皓角頻道資訊
        self.channel_info = {
            "UC0lbAQVpenvfA2QqzsRtL_g": {
                "name": "游庭皓的財經皓角",
                "description": "解析財經時事，分享投資觀點",
                "playlist_id": "PLuAHvR06yXa2eUdcfYOxX1tC3RrFQQxB_"
            }
        }
        
    def get_video_list(self, max_results: int = 10) -> list[dict]:
        """取得最近影片列表 - 使用 web scraping"""
        # 簡化的實現：從 channel 頁面擷取
        # 實際應該用 YouTube Data API
        return []  # TODO: Implement with API
        
    def fetch_transcript(self, video_id: str) -> Optional[dict]:
        """擷取影片逐字稿"""
        if not YOUTUBE_API_AVAILABLE:
            return self._fetch_transcript_manual(video_id)
            
        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=['zh-TW', 'zh', 'en']
            )
            return {
                "video_id": video_id,
                "transcript": transcript,
                "fetched_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error fetching transcript for {video_id}: {e}")
            return None
            
    def _fetch_transcript_manual(self, video_id: str) -> Optional[dict]:
        """手動擷取方法（使用 requests）"""
        # 嘗試從 YouTube 取得 auto-generated captions
        url = f"https://www.youtube.com/api/timedtext?v={video_id}&lang=zh-TW"
        # 這個方法有限制，需要 proper API
        return None
        
    def clean_transcript(self, transcript_data: dict) -> dict:
        """清理逐字稿"""
        if not transcript_data:
            return transcript            
        
        raw_texts = transcript_data.get("transcript", [])
        cleaned_texts = []
        
        # 定義要過濾的內容模式
        filter_patterns = [
            r"(?:[嗨笑哈哈]{1,})",  # 笑聲
            r"\[.*?\]",  # 括號內容（通常是非語音標記）
            r"\(.*?\)",  
            r"XD+",
            r"哈哈哈+",
            r"嘿嘿+",
        ]
        
        for item in raw_texts:
            text = item.get("text", "")
            
            # 跳過太短的項目（通常是非語音）
            if len(text) < 2:
                continue
                
            # 跳過包含笑声的項目
            if any(p in text.lower() for p in ["哈哈", "嘿嘿", "笑笑", "xd"]):
                if len(text) < 5:  # 短的笑聲
                    continue
                    
            # 基本清理
            text = text.strip()
            
            # 標記財經相關關鍵詞
            is_finance = any(kw in text for kw in [
                "漲", "跌", "利率", "通膨", "Fed", "央行",
                "台積電", "股票", "ETF", "投資",
                "美元", "台幣", "房貸", "CPI"
            ])
            
            cleaned_texts.append({
                "text": text,
                "start": item.get("start"),
                "duration": item.get("duration"),
                "is_finance_related": is_finance
            })
            
        transcript_data["transcript"] = cleaned_texts
        transcript_data["cleaned_at"] = datetime.now().isoformat()
        
        return transcript_data
        
    def extract_sources(self, transcript_data: dict) -> dict:
        """分析逐字稿，提取資料來源"""
        if not transcript_data:
            return {"error": "No transcript data"}
            
        # 關鍵字對應的來源
        source_keywords = {
            "Federal Reserve/FED": [
                "Fed", "聯準會", "鮑威爾", "葉倫",
                "FOMC", "利率決策", "縮表"
            ],
            "Bloomberg": [
                "Bloomberg", "彭博"
            ],
            "CNBC": [
                "CNBC"
            ],
            "Reuters": [
                "路透", "Reuters"
            ],
            "WSJ": [
                "華爾街日报", "WSJ", "Wall Street Journal"
            ],
            "IMF": [
                "IMF", "國際貨幣基金"
            ],
            "World Bank": [
                "世界銀行", "World Bank"
            ],
            "CNA/中央社": [
                "中央社", "CNA"
            ],
            "經濟日報": [
                "經濟日报", "工商時報"
            ],
            "PTT": [
                "PTT", "批踢踢", "ptt.cc"
            ],
            "Yahoo Finance": [
                "Yahoo", "雅虎", "YAHOO"
            ],
            "MarketWatch": [
                "MarketWatch"
            ],
            "Seeking Alpha": [
                "Seeking Alpha"
            ]
        }
        
        # 統計來源出現次數
        source_counts = {source: 0 for source in source_keywords}
        
        for item in transcript_data.get("transcript", []):
            text = item.get("text", "")
            for source, keywords in source_keywords.items():
                for kw in keywords:
                    if kw in text:
                        source_counts[source] += 1
                        break
                        
        # 排序並返回
        sorted_sources = sorted(
            source_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "sources": [s for s, c in sorted_sources if c > 0],
            "counts": {s: c for s, c in sorted_sources if c > 0},
            "analyzed_at": datetime.now().isoformat()
        }
        
    def save_transcript(self, transcript_data: dict, video_id: str) -> str:
        """儲存逐字稿"""
        if not transcript_data:
            return None
            
        # 生成檔名
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{self.output_dir}/{video_id}_{date_str}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)
            
        return filename
        
    def save_source_report(self, source_analysis: dict, video_id: str) -> str:
        """儲存來源分析報告"""
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{self.output_dir}/{video_id}_sources_{date_str}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(source_analysis, f, ensure_ascii=False, indent=2)
            
        return filename


def main():
    parser = argparse.ArgumentParser(
        description="抓取 游庭皓的財經皓角 逐字稿"
    )
    parser.add_argument(
        "--channel", 
        default="UC0lbAQVpenvfA2QqzsRtL_g",
        help="YouTube Channel ID"
    )
    parser.add_argument(
        "--video",
        help="Specific video ID (optional)"
    )
    parser.add_argument(
        "--output",
        default="./transcripts",
        help="Output directory"
    )
    
    args = parser.parse_args()
    
    downloader = PodcastDownloader(
        channel_id=args.channel,
        output_dir=args.output
    )
    
    # 如果沒有指定影片，抓取最新的一個
    video_id = args.video
    
    if video_id:
        print(f"Fetching transcript for {video_id}...")
        transcript = downloader.fetch_transcript(video_id)
        
        if transcript:
            # 清理
            cleaned = downloader.clean_transcript(transcript)
            
            # 保存
            saved = downloader.save_transcript(cleaned, video_id)
            print(f"Saved to: {saved}")
            
            # 分析來源
            sources = downloader.extract_sources(cleaned)
            print(f"Sources: {sources['sources']}")
            
            # 保存來源報告
            report_file = downloader.save_source_report(sources, video_id)
            print(f"Source report saved to: {report_file}")
        else:
            print("No transcript available")
    else:
        print(f"Channel: {args.channel}")
        print("Use --video <id> to fetch specific video")


if __name__ == "__main__":
    main()