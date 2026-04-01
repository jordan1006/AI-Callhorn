"""
Script Generator - 模擬原作者邏輯生成最新數據講稿
"""

import json
from datetime import datetime
from typing import Any


class ScriptGenerator:
    """根據市場數據生成 Podcast 講稿"""
    
    def __init__(self, persona: str = "資深財經分析師"):
        self.persona = persona
        self.template = self._load_template()
        
    def _load_template(self) -> dict:
        """載入講稿模板"""
        return {
            "opening": [
                "各位觀眾大家好，我是{persona}。",
                "今天來到{date}，讓我們一起來關注市場動態。",
            ],
            "structure": [
                "首先，讓我們看一下今天的市場概況...",
                "接下來，我們追蹤幾個重要議題...",
                "最後，給大家一些投資建議..."
            ],
            "closing": [
                "以上是我今天的分析，祝福大家投資順利！",
                "記得做好風險管理，我們下次再見！"
            ]
        }
    
    def generate_script(self, market_data: dict) -> str:
        """根據市場數據生成完整講稿"""
        lines = []
        
        # Opening
        for template in self.template["opening"]:
            lines.append(template.format(
                persona=self.persona,
                date=datetime.now().strftime("%Y年%m月%d日")
            ))
        
        lines.append("")
        
        # 市場概況
        lines.append("📈 首先，讓我們看一下今天的市場概況：")
        if "index" in market_data:
            for idx_name, idx_data in market_data["index"].items():
                change = idx_data.get("change", 0)
                direction = "上漲" if change > 0 else "下跌"
                lines.append(f"- {idx_name} {direction} {abs(change):.2f}%")
        
        lines.append("")
        
        # 焦點議題
        lines.append("🔥 今日焦點：")
        if "focus" in market_data:
            for i, focus in enumerate(market_data["focus"], 1):
                lines.append(f"{i}. {focus}")
        
        lines.append("")
        
        # 傳導鏈分析
        if "transmission" in market_data:
            lines.append("🔗 傳導鏈分析：")
            for link in market_data["transmission"]:
                lines.append(f"- {link}")
        
        lines.append("")
        
        # 投資建議
        lines.append("💡 投資建議：")
        if "recommendations" in market_data:
            for rec in market_data["recommendations"]:
                lines.append(f"- {rec}")
        
        lines.append("")
        
        # Closing
        for template in self.template["closing"]:
            lines.append(template)
        
        return "\n".join(lines)
    
    def generate_actionable_advice(self, portfolio: dict, market_data: dict) -> str:
        """生成針對特定投資組合的 Actionable Advice"""
        advice = []
        
        # 台股分析
        tw_stocks = portfolio.get("tw_stocks", [])
        if tw_stocks:
            tw_change = market_data.get("tw_market_change", 0)
            
            if tw_change > 2:
                advice.append("�Taiwan+: 市場大漲，可考慮部分獲利了結")
            elif tw_change < -2:
                advice.append("�Taiwan+: 大跌是加碼機會，記得設停損")
            else:
                advice.append("�Taiwan+: 區間震盪，建議觀望")
        
        # 美股分析
        us_stocks = portfolio.get("us_stocks", [])
        if us_stocks:
            nasdaq_change = market_data.get("nasdaq_change", 0)
            
            if nasdaq_change > 1.5:
                advice.append("📈 TQQQ: 納指漲幅大，注意槓桿風險，可考慮減碼")
            elif nasdaq_change < -1.5:
                advice.append("📉 TQQQ: 大跌是撿便宜機會，但要用閒錢")
            else:
                advice.append("📊 TQQQ: 持續定投，不因波動而中斷")
        
        # 匯率影響
        twd_change = market_data.get("twd_change", 0)
        if twd_change < -2:
            advice.append("💵 台幣貶值超過2%，出口族群受惠，留意匯兌收益")
        elif twd_change > 2:
            advice.append("💵 台幣升值，有利進口但出口族群壓力大")
        
        # 房貸利率
        mortgage_rate = market_data.get("mortgage_rate", 2.0)
        advice.append(f"🏠 房貸利率約 {mortgage_rate:.2f}%，2,000萬房產每月負擔約 {20000000 * mortgage_rate/100 / 240:.0f} 元")
        
        return "\n".join(advice)


class TransmissionChainNarrator:
    """傳導鏈敘事者 - 將傳導鏈轉化為敘事"""
    
    def __init__(self):
        self.node_narratives = {}
        
    def narrate_chain(self, chain_data: dict) -> str:
        """將傳導鏈轉化為人類可讀的敘述"""
        lines = []
        
        if "impacts" in chain_data:
            lines.append("🔗 今日傳導鏈分析：\n")
            
            # 按權重排序
            sorted_impacts = sorted(
                chain_data["impacts"].items(),
                key=lambda x: abs(x[1].get("weight", 0)),
                reverse=True
            )
            
            for key, impact in sorted_impacts[:5]:  # 前5大影響
                from_node, to_node = key.split("->")
                weight = impact.get("weight", 0)
                direction = "正向" if weight > 0 else "負向"
                
                lines.append(f"- {from_node} → {to_node}: {direction}影響 (強度: {abs(weight):.2f})")
        
        return "\n".join(lines)
    
    def generate_mermaid_chart(self, graph_data: dict) -> str:
        """生成 Mermaid 關係圖"""
        lines = ["```mermaid", "flowchart LR"]
        
        # 節點分類配色
        colors = {
            "macro_event": "fill:#ff6b6b",
            "sector": "fill:#4ecdc4",
            "commodity": "fill:#ffe66d",
            "currency": "fill:#95e1d3",
            "policy": "fill:#f38181",
            "crypto": "fill:#aa96da",
            "real_estate": "fill:#fcbad3",
            "leverage_etf": "fill:#a8d8ea"
        }
        
        nodes = graph_data.get("nodes", {})
        
        for node_id, node_data in nodes.items():
            name = node_data.get("name", node_id)
            category = node_data.get("category", "default")
            color = colors.get(category, "fill:#ddd")
            
            lines.append(f'    {node_id}["{name}"]::{color}')
        
        lines.append("")
        
        edges = graph_data.get("edges", [])
        for edge in edges:
            from_node = edge["from"]
            to_node = edge["to"]
            weight = edge.get("weight", 0)
            label = edge.get("label", "")
            
            style = "-->" if weight > 0 else "-.->"
            lines.append(f'    {from_node} {style} {to_node} : "{label}"')
        
        lines.append("```")
        return "\n".join(lines)


async def main():
    """測試"""
    generator = ScriptGenerator()
    
    market_data = {
        "index": {
            "加權指數": {"change": 1.5},
            "Nasdaq": {"change": -0.8}
        },
        "focus": [
            "Fed 利率預期",
            "台積電法說",
            "以巴衝突影響"
        ],
        "transmission": [
            "戰爭 → 航運 → 石油 → 通膨 → Fed升息 → 科技股",
        ],
        "recommendations": [
            "關注 Fed 利率走向",
            "科技股暫時觀望",
            "黃金可適度配置"
        ],
        "tw_market_change": 1.5,
        "nasdaq_change": -0.8,
        "twd_change": -1.2,
        "mortgage_rate": 2.1
    }
    
    script = generator.generate_script(market_data)
    print(script)
    print("\n" + "="*50 + "\n")
    
    # Actionable Advice
    portfolio = {
        "tw_stocks": ["正二", "0050"],
        "us_stocks": ["TQQQ", "NVDA"]
    }
    
    advice = generator.generate_actionable_advice(portfolio, market_data)
    print("💡 Actionable Advice:\n")
    print(advice)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
