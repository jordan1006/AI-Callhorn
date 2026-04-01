"""
MCP Server for Financial Data & PTT Integration
讓 Agent 能即時查詢 PTT 與財經數據
"""

import json
from datetime import datetime
from typing import Any

import httpx


class PTTMCPserver:
    """PTT 資料查詢 MCP Server"""
    
    def __init__(self):
        self.base_url = "https://api.ptexpansion.com"  # 範例 API
        self.board_cache = {}
        
    async def get_board_posts(self, board: str, limit: int = 10) -> list[dict]:
        """取得指定板最新的文章"""
        # 實際實現需要使用 PTT API 或爬蟲
        # 這裡是 mock 數據
        
        mock_posts = {
            "Stock": [
                {"title": "[心得] 0050 定期定額策略分享", "pushes": 45, "author": "abc123"},
                {"title": "[情報] 台積電法說會重點", "pushes": 128, "author": "stockgod"},
                {"title": "[請益] 現在進場TQQQ好嗎", "pushes": 23, "author": "newbie"},
                {"title": "[標的] 金融股推薦", "pushes": 67, "author": "banker"},
                {"title": "[討論] 大盤看法", "pushes": 89, "author": "bear"}
            ],
            "Tech_Job": [
                {"title": "[心得] 面試心得分享", "pushes": 34, "author": "dev01"},
                {"title": "[請益] 台積電值得去嗎", "pushes": 56, "author": "newgrad"}
            ]
        }
        
        return mock_posts.get(board, [])[:limit]
    
    async def search_keyword(self, board: str, keyword: str) -> list[dict]:
        """搜尋文章關鍵字"""
        posts = await self.get_board_posts(board, limit=50)
        
        results = []
        for post in posts:
            if keyword.lower() in post["title"].lower():
                results.append(post)
        
        return results
    
    def get_hot_topics(self) -> dict[str, list]:
        """取得熱門話題"""
        return {
            "Stock": ["台積電", "0050", "TQQQ", "金融股", "航運"],
            "Finance": ["ETF", "理財", "保險", "房貸"],
            "Crypto": ["比特幣", "以太坊", "狗狗幣"]
        }


class FinancialMCPserver:
    """財經數據 MCP Server"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def get_market_summary(self) -> dict:
        """取得市場摘要"""
        # 使用 yfinance 獲取數據
        try:
            import yfinance as yf
            
            tickers = {
                "tw": ["0050.TW", "2317.TW"],
                "us": ["TQQQ", "NVDA", "AAPL", "MSFT"],
                "crypto": ["BTC-USD", "ETH-USD"],
                "commodity": ["GC=F", "SI=F", "CL=F"]
            }
            
            summary = {}
            
            for category, symbols in tickers.items():
                summary[category] = {}
                for symbol in symbols:
                    try:
                        ticker = yf.Ticker(symbol)
                        hist = ticker.history(period="1d")
                        if not hist.empty:
                            price = float(hist['Close'].iloc[-1])
                            prev = float(hist['Open'].iloc[0])
                            change = (price - prev) / prev * 100
                            summary[category][symbol] = {
                                "price": price,
                                "change_pct": change
                            }
                    except Exception as e:
                        print(f"Error fetching {symbol}: {e}")
            
            return summary
            
        except ImportError:
            return {"error": "yfinance not installed"}
    
    async def get_currency_rate(self, pair: str = "TWD=X") -> dict:
        """取得匯率"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(pair)
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                rate = float(hist['Close'].iloc[-1])
                return {"pair": pair, "rate": rate}
            
        except Exception as e:
            return {"error": str(e)}
        
        return {"error": "No data"}
    
    async def get_economic_calendar(self) -> list[dict]:
        """取得經濟行事曆"""
        # 簡化的經濟數據列表
        events = [
            {"date": "2026-04-03", "event": "美國非農就業數據", "impact": "high"},
            {"date": "2026-04-04", "event": "Fed 會議記錄", "impact": "high"},
            {"date": "2026-04-10", "event": "台灣CPI數據", "impact": "medium"},
            {"date": "2026-04-15", "event": "美國CPI數據", "impact": "high"},
            {"date": "2026-04-17", "event": "台積電法說會", "impact": "high"},
        ]
        
        return events
    
    async def get_polymarket_odds(self, event: str) -> dict:
        """取得 Polymarket 預測市場赔率"""
        # 範例：取得特定事件的市場預測
        mock_odds = {
            "fed_rate_cut": {"yes": 0.35, "no": 0.65},
            "recession_2026": {"yes": 0.22, "no": 0.78},
            "bitcoin_100k": {"yes": 0.45, "no": 0.55}
        }
        
        return mock_odds.get(event, {"error": "Event not found"})
    
    async def close(self):
        await self.client.aclose()


class MCPserver:
    """整合型 MCP Server"""
    
    def __init__(self):
        self.ptt = PTTMCPserver()
        self.finance = FinancialMCPserver()
    
    async def handle_request(self, tool: str, params: dict) -> Any:
        """處理 MCP 請求"""
        if tool == "ptt_posts":
            return await self.ptt.get_board_posts(
                params.get("board", "Stock"),
                params.get("limit", 10)
            )
        
        elif tool == "ptt_search":
            return await self.ptt.search_keyword(
                params.get("board", "Stock"),
                params.get("keyword", "")
            )
        
        elif tool == "market_summary":
            return await self.finance.get_market_summary()
        
        elif tool == "currency_rate":
            return await self.finance.get_currency_rate(
                params.get("pair", "TWD=X")
            )
        
        elif tool == "economic_calendar":
            return await self.finance.get_economic_calendar()
        
        elif tool == "polymarket":
            return await self.finance.get_polymarket_odds(
                params.get("event", "")
            )
        
        return {"error": "Unknown tool"}
    
    async def close(self):
        await self.finance.close()


# MCP Server 入口點
async def main():
    """MCP Server 啟動"""
    server = MCPserver()
    
    # 測試請求
    print("📊 市場摘要:")
    summary = await server.handle_request("market_summary", {})
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    print("\n📝 PTT Stock 熱門:")
    posts = await server.handle_request("ptt_posts", {"board": "Stock", "limit": 5})
    for post in posts:
        print(f"- {post['title']} ({post['pushes']}推)")
    
    print("\n📅 經濟行事曆:")
    events = await server.handle_request("economic_calendar", {})
    for event in events:
        print(f"- {event['date']}: {event['event']}")
    
    await server.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
