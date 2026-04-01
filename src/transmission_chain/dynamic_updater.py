"""
Transmission Chain Dynamic Updater
每日更新價格傳導鏈，並標記橫向擴散影響
"""

import json
import os
from datetime import datetime
from typing import Any

import httpx
import yaml


class TransmissionChainUpdater:
    """傳導鏈動態更新器"""
    
    def __init__(self, graph_path: str):
        self.graph_path = graph_path
        self.graph = self._load_graph()
        self.client = httpx.AsyncClient(timeout=30.0)
        
    def _load_graph(self) -> dict:
        """載入傳導圖"""
        with open(self.graph_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def fetch_price_data(self, symbols: list[str]) -> dict[str, float]:
        """
        從 Yahoo Finance 獲取價格數據
        使用 yfinance 庫
        """
        try:
            import yfinance as yf
            
            prices = {}
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    prices[symbol] = float(hist['Close'].iloc[-1])
            return prices
        except Exception as e:
            print(f"Error fetching prices: {e}")
            return {}
    
    async def update_chain(self) -> dict:
        """
        更新傳導鏈
        計算當日價格變動對下游節點的影響
        """
        # 定義符號映射
        symbol_map = {
            "oil": "CL=F",       # WTI原油
            "gold": "GC=F",       # 黃金
            "silver": "SI=F",     # 白銀
            "copper": "HG=F",     # 銅
            "usd_index": "DX-Y.NYB",  # 美元指數
            "bitcoin": "BTC-USD",
            "tqqq": "TQQQ",
            "taiwan_plus": "0050.TW",  # 0050
        }
        
        prices = await self.fetch_price_data(list(symbol_map.values()))
        
        # 計算影響傳播
        impact_results = self._propagate_impact(prices, symbol_map)
        
        return {
            "updated_at": datetime.now().isoformat(),
            "prices": prices,
            "impacts": impact_results,
            "new_priced_in": self._detect_new_priced_in(impact_results)
        }
    
    def _propagate_impact(self, prices: dict, symbol_map: dict) -> dict:
        """根據價格變動計算沿傳導鏈的影響"""
        impacts = {}
        
        # 簡單的影響傳播計算
        # 這裡應該實現更複雜的圖傳播算法
        for edge in self.graph.get("edges", []):
            from_node = edge["from"]
            to_node = edge["to"]
            weight = edge.get("weight", 0)
            
            # 如果源節點有價格數據，計算對目標節點的影響
            # 實際實現需要歷史數據對比
            impacts[f"{from_node}->{to_node}"] = {
                "weight": weight,
                "direction": "positive" if weight > 0 else "negative",
                "strength": abs(weight)
            }
        
        return impacts
    
    def _detect_new_priced_in(self, impacts: dict) -> list[str]:
        """檢測新出現的「已反應」節點"""
        # 簡化的實現：基於閾值判斷
        # 實際需要歷史趨勢回測
        new_markers = []
        return new_markers
    
    def save_updates(self, updates: dict):
        """儲存更新結果"""
        output_path = self.graph_path.replace(".json", "_updates.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(updates, f, ensure_ascii=False, indent=2)
    
    async def close(self):
        await self.client.aclose()


class ImpactGraph:
    """影響力圖管理器"""
    
    def __init__(self, graph_data: dict):
        self.nodes = graph_data.get("nodes", {})
        self.edges = graph_data.get("edges", [])
        self.priced_in = graph_data.get("priced_in_markers", {})
    
    def get_node(self, node_id: str) -> dict | None:
        return self.nodes.get(node_id)
    
    def get_edges_from(self, node_id: str) -> list[dict]:
        return [e for e in self.edges if e["from"] == node_id]
    
    def get_edges_to(self, node_id: str) -> list[dict]:
        return [e for e in self.edges if e["to"] == node_id]
    
    def generate_mermaid_chart(self) -> str:
        """生成 Mermaid 傳導鏈關係圖"""
        lines = ["```mermaid", "flowchart LR"]
        
        # 節點定義
        for node_id, node_data in self.nodes.items():
            name = node_data.get("name", node_id)
            category = node_data.get("category", "default")
            # 簡化的節點樣式
            lines.append(f'    {node_id}["{name}"]')
        
        lines.append("")
        
        # 邊定義
        for edge in self.edges:
            from_node = edge["from"]
            to_node = edge["to"]
            weight = edge.get("weight", 0)
            label = edge.get("label", "")
            
            # 根據權重決定邊的樣式
            if weight > 0:
                style = "-->"
            else:
                style = "-.->"
            
            lines.append(f'    {from_node} {style} {to_node} : "{label}"')
        
        lines.append("```")
        return "\n".join(lines)
    
    def get_transmission_path(self, start: str, end: str) -> list[dict]:
        """取得從起點到終點的傳導路徑"""
        from collections import deque
        
        visited = set()
        queue = deque([(start, [])])
        
        while queue:
            current, path = queue.popleft()
            
            if current == end:
                return path
            
            if current in visited:
                continue
            
            visited.add(current)
            
            for edge in self.get_edges_from(current):
                next_node = edge["to"]
                new_path = path + [edge]
                queue.append((next_node, new_path))
        
        return []
    
    def calculate_cumulative_impact(self, start: str) -> dict[str, float]:
        """計算從某節點對所有下游節點的累積影響"""
        impacts = {start: 1.0}
        visited = set()
        
        def propagate(node: str, current_impact: float):
            if node in visited:
                return
            visited.add(node)
            
            for edge in self.get_edges_from(node):
                next_node = edge["to"]
                weight = edge.get("weight", 0)
                new_impact = current_impact * weight
                
                if next_node in impacts:
                    impacts[next_node] = max(impacts[next_node], new_impact)
                else:
                    impacts[next_node] = new_impact
                
                propagate(next_node, new_impact)
        
        propagate(start, 1.0)
        return impacts


async def main():
    """每日執行更新"""
    graph_path = os.path.join(
        os.path.dirname(__file__),
        "impact_graph.json"
    )
    
    updater = TransmissionChainUpdater(graph_path)
    updates = await updater.update_chain()
    updater.save_updates(updates)
    
    # 生成 Mermaid 圖
    graph = ImpactGraph(updater.graph)
    mermaid_chart = graph.generate_mermaid_chart()
    print(mermaid_chart)
    
    await updater.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
