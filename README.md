# Financial-Inverse-Engine

> AI 財經號角 - 透過「逆向工程」解析財經資訊，生成投資決策摘要

## 📌 專案願景

建立一個自主 Agent 系統，透過「逆向工程」解析財經 Podcast/新聞，溯源原始數據，並基於「全球資源價格傳導鏈」生成針對特定受眾（台灣高資產科技族群）的投資決策摘要與 Podcast 講稿。

## 🎯 目標受眾

- **身份：** 台灣科技業工程師
- **投資背景：** 具備美股與台股對等投資經驗
- **資產結構：**
  - 50% 台股（正二/0050）
  - 50% 美股（TQQQ/NVDA）
  - 2,000萬台幣房產

## 🏗️ 技術架構

### 核心框架
- OpenClaw MCP (Model Context Protocol) 整合
- Python 3.12+

### 資料獲取層
- 財經 API（Marketstack/Polygon）
- 貨幣、金屬（黃金、白銀、銅、白金）、石油、比特幣
- 主要板塊：運輸、科技、金融、軍工
- 社群偵察：PTT Stock、Reddit WSB、Polymarket

### 邏輯層 (Transmission Chain)
- Graph-based 影響力模型
- 標註「已反應(Priced-in)」與「未反應」狀態
- 歷史日期趨勢回測

## 📁 目錄結構

```
Financial-Inverse-Engine/
├── src/
│   ├── inverse_engine/        # 逆向工程引擎
│   │   ├── podcast_parser.py
│   │   └── script_generator.py
│   ├── transmission_chain/    # 傳導鏈邏輯
│   │   ├── impact_graph.json
│   │   └── dynamic_updater.py
│   ├── personalizer/          # 個人化分析
│   │   └── portfolio_impact.py
│   └── mcp_servers/           # MCP 伺服器
├── .github/
│   └── workflows/
├── requirements.txt
└── README.md
```

## 🚀 核心功能模組

### 1. inverse_engine
- `podcast_parser.py` - 提取音檔/文字關鍵邏輯，進行「Golden Patent」逆向溯源
- `script_generator.py` - 模擬原作者邏輯生成最新數據講稿

### 2. transmission_chain
- `impact_graph.json` - 定義資源間的傳導係數與路徑
- `dynamic_updater.py` - 每日更新價格傳導鏈，標記橫向擴散影響

### 3. personalizer
- `portfolio_impact.py` - 針對 50/50 台美股及 2,000 萬房產進行特化摘要

### 4. mcp_servers
- 專用 MCP Server，即時查詢 PTT 與財經數據

## 📊 輸出規範

1. **擴充性** - 程式碼模組化，方便加入新資源板塊（稀土、碳權等）
2. **易解讀性** - Summary 包含：
   - 傳導鏈關係圖（Mermaid.js 格式）
   - Actionable Advice（槓桿工具進退場建議）
3. **自動化** - GitHub Actions 每日定時執行分析

## 📝 授權

MIT License
