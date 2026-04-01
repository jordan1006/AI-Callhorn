"""
Portfolio Impact Analyzer
針對 50/50 台美股及 2,000 萬房產進行特化摘要
"""

import json
from datetime import datetime
from typing import Any


class PortfolioImpactAnalyzer:
    """投資組合影響分析器"""
    
    def __init__(self, portfolio: dict):
        """
        初始化投資組合
        預設結構:
        - tw_stocks: 50% (正二/0050)
        - us_stocks: 50% (TQQQ/NVDA)
        - real_estate: 20,000,000 TWD
        """
        self.portfolio = portfolio
        self.total_value = self._calculate_total()
        
    def _calculate_total(self) -> float:
        """計算總資產"""
        tw = self.portfolio.get("tw_value", 10_000_000)
        us = self.portfolio.get("us_value", 10_000_000)
        re = self.portfolio.get("real_estate_value", 20_000_000)
        return tw + us + re
    
    def analyze_market_impact(self, market_data: dict) -> dict[str, Any]:
        """分析市場數據對投資組合的影響"""
        impacts = {}
        
        # 台股影響
        tw_change = market_data.get("tw_market_change", 0)
        tw_value = self.portfolio.get("tw_value", 10_000_000)
        tw_impact = tw_value * tw_change / 100
        impacts["tw_stocks"] = {
            "change_pct": tw_change,
            "value_change": tw_impact,
            "weighted_impact": tw_impact / self.total_value * 100
        }
        
        # 美股影響
        us_change = market_data.get("us_market_change", 0)
        us_value = self.portfolio.get("us_value", 10_000_000)
        us_impact = us_value * us_change / 100
        impacts["us_stocks"] = {
            "change_pct": us_change,
            "value_change": us_impact,
            "weighted_impact": us_impact / self.total_value * 100
        }
        
        # 匯率影響
        twd_change = market_data.get("twd_change", 0)
        # 台幣貶值對美股的影響（以台幣計價）
        us_value_twd = self.portfolio.get("us_value", 10_000_000)
        fx_impact = us_value_twd * twd_change / 100
        impacts["fx_impact"] = {
            "twd_change": twd_change,
            "value_change": fx_impact,
            "weighted_impact": fx_impact / self.total_value * 100
        }
        
        # 房產影響
        mortgage_rate = market_data.get("mortgage_rate", 2.0)
        re_value = self.portfolio.get("real_estate_value", 20_000_000)
        
        # 房貸利率影響（假設房貸 1000 萬，20年本息攤還）
        mortgage_principal = 10_000_000
        monthly_payment = self._calc_mortgage(mortgage_principal, mortgage_rate, 20)
        annual_cost = monthly_payment * 12
        
        impacts["real_estate"] = {
            "property_value": re_value,
            "mortgage_rate": mortgage_rate,
            "monthly_payment": monthly_payment,
            "annual_cost": annual_cost,
            "cost_ratio": annual_cost / re_value * 100
        }
        
        # 總影響
        total_change = sum(i["value_change"] for i in impacts.values() 
                         if isinstance(i, dict) and "value_change" in i)
        
        return {
            "impacts": impacts,
            "total_change": total_change,
            "total_change_pct": total_change / self.total_value * 100,
            "analysis_time": datetime.now().isoformat()
        }
    
    def _calc_mortgage(self, principal: float, rate: float, years: int) -> float:
        """計算房貸月付額"""
        monthly_rate = rate / 100 / 12
        n = years * 12
        if monthly_rate == 0:
            return principal / n
        return principal * (monthly_rate * (1 + monthly_rate)**n) / ((1 + monthly_rate)**n - 1)
    
    def generate_summary(self, market_data: dict) -> str:
        """生成個人化摘要"""
        analysis = self.analyze_market_impact(market_data)
        impacts = analysis["impacts"]
        
        lines = []
        lines.append("📊 投資組合每日摘要")
        lines.append("="*40)
        
        # 資產配置
        lines.append("\n💰 資產配置：")
        lines.append(f"- 台股 (50%): {self.portfolio.get('tw_value', 10_000_000):,.0f} TWD")
        lines.append(f"- 美股 (50%): {self.portfolio.get('us_value', 10_000_000):,.0f} TWD")
        lines.append(f"- 房產: {self.portfolio.get('real_estate_value', 20_000_000):,.0f} TWD")
        lines.append(f"- 總資產: {self.total_value:,.0f} TWD")
        
        # 今日變化
        lines.append("\n📈 今日變化：")
        tw = impacts.get("tw_stocks", {})
        if tw:
            direction = "↑" if tw.get("change_pct", 0) > 0 else "↓"
            lines.append(f"- 台股: {direction} {abs(tw.get('change_pct', 0)):.2f}% ({tw.get('value_change', 0):+,.0f} TWD)")
        
        us = impacts.get("us_stocks", {})
        if us:
            direction = "↑" if us.get("change_pct", 0) > 0 else "↓"
            lines.append(f"- 美股: {direction} {abs(us.get('change_pct', 0)):.2f}% ({us.get('value_change', 0):+,.0f} TWD)")
        
        fx = impacts.get("fx_impact", {})
        if fx:
            direction = "↑" if fx.get("twd_change", 0) > 0 else "↓"
            lines.append(f"- 台幣: {direction} {abs(fx.get('twd_change', 0)):.2f}% (對美股影響: {fx.get('value_change', 0):+,.0f} TWD)")
        
        # 總計
        total = analysis["total_change"]
        total_pct = analysis["total_change_pct"]
        direction = "↑" if total > 0 else "↓"
        lines.append(f"\n💵 總損益: {direction} {abs(total):,.0f} TWD ({total_pct:+.2f}%)")
        
        # 房貸狀態
        re = impacts.get("real_estate", {})
        if re:
            lines.append("\n🏠 房貸狀態：")
            lines.append(f"- 房貸利率: {re.get('mortgage_rate', 0):.2f}%")
            lines.append(f"- 月付額: {re.get('monthly_payment', 0):,.0f} TWD")
            lines.append(f"- 年負擔: {re.get('annual_cost', 0):,.0f} TWD")
        
        # Actionable Advice
        lines.append("\n" + "="*40)
        lines.append("💡 建議：")
        
        advice = self._generate_advice(analysis)
        lines.extend(advice)
        
        return "\n".join(lines)
    
    def _generate_advice(self, analysis: dict) -> list[str]:
        """生成投資建議"""
        advice = []
        impacts = analysis["impacts"]
        
        tw = impacts.get("tw_stocks", {})
        us = impacts.get("us_stocks", {})
        fx = impacts.get("fx_impact", {})
        
        # 台股建議
        if tw.get("change_pct", 0) > 3:
            advice.append("- 台股大漲，可考慮部分獲利了結")
        elif tw.get("change_pct", 0) < -3:
            advice.append("- 台股大跌，是加碼好時機")
        
        # 美股建議
        if us.get("change_pct", 0) > 2:
            advice.append("- TQQQ 漲幅大，注意槓桿風險，減碼為宜")
        elif us.get("change_pct", 0) < -2:
            advice.append("- TQQQ 大跌，可用閒錢加碼")
        
        # 匯率建議
        if fx.get("twd_change", 0) < -3:
            advice.append("- 台幣重貶，有利出口族群，可關注電子類股")
        elif fx.get("twd_change", 0) > 3:
            advice.append("- 台幣強升，進口成本下降，但出口壓力大")
        
        if not advice:
            advice.append("- 市場區間震盪，建議觀望，保持現金水位")
        
        return advice


class TransmissionChainAnalyzer:
    """傳導鏈分析 - 追蹤影響路徑"""
    
    def __init__(self, graph_path: str = None):
        self.graph_path = graph_path
        
    def analyze_chain(self, trigger: str, market_data: dict) -> list[dict]:
        """分析從觸發事件到投資組合的傳導路徑"""
        # 簡化的實現
        # 實際應該使用圖數據庫或 networkx
        chains = []
        
        # 定義常見的傳導路徑
        common_paths = [
            {
                "trigger": "war",
                "path": ["war", "shipping", "oil", "inflation_expectation", "fed_rate", "tech_stock"],
                "impact": "negative"
            },
            {
                "trigger": "oil",
                "path": ["oil", "inflation_expectation", "bond_yield", "usd_index", "twd_usd"],
                "impact": "mixed"
            },
            {
                "trigger": "fed_rate",
                "path": ["fed_rate", "bond_yield", "tech_stock", "tqqq"],
                "impact": "negative"
            }
        ]
        
        for path_info in common_paths:
            if path_info["trigger"] == trigger:
                chains.append(path_info)
        
        return chains
    
    def predict_impact(self, event: str, market_data: dict) -> dict:
        """預測事件對投資組合的影響"""
        chains = self.analyze_chain(event, market_data)
        
        if not chains:
            return {"impact": "unknown", "confidence": 0}
        
        # 簡單的影響計算
        avg_impact = sum(1 if c["impact"] == "positive" else -1 for c in chains) / len(chains)
        
        return {
            "event": event,
            "chains": chains,
            "impact": "positive" if avg_impact > 0 else "negative",
            "confidence": len(chains) / 5  # 假設最多5條路徑
        }


async def main():
    """測試"""
    portfolio = {
        "tw_value": 10_000_000,
        "us_value": 10_000_000,
        "real_estate_value": 20_000_000
    }
    
    analyzer = PortfolioImpactAnalyzer(portfolio)
    
    market_data = {
        "tw_market_change": 1.8,
        "us_market_change": -1.2,
        "twd_change": -0.8,
        "mortgage_rate": 2.1
    }
    
    summary = analyzer.generate_summary(market_data)
    print(summary)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
