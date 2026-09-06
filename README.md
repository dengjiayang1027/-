# 蔥明錢 Lite

針對舊電腦優化的版本。

主要優化：
- K 線只顯示最近 120 根
- 移除 Volume 圖層
- 統計卡改成 HTML，減少 Streamlit 元件
- 交易理由改為單一 multiselect
- 減少多餘欄位與重繪
- demo 資料只在第一次載入時建立
- 啟動時關閉 usage stats

啟動：
1. `pip install -r requirements.txt`
2. 雙擊 `啟動蔥明錢_Lite.bat`

或：
`python -m streamlit run app.py`
