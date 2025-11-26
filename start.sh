#!/bin/bash

# LINE Bot 啟動腳本
# 使用前請先設定以下變數

export LINE_CHANNEL_SECRET="a219bfd132141cc5aa02f95399545a16"
export LINE_CHANNEL_ACCESS_TOKEN="aFz9hv4mLW6sVIGauZcIuRWa/j9faB4X3YhmK0MYx12mm4VVmM6lFwHOaX3/0j8SSx7VCgy4v7417/Lnj30TjVvvmGpn/mrleO9K8+FczV5odujjXNf2ND4AJE+N4/RlWl/ducs6P4/Qkq7Iqz0ivwdB04t89/1O/w1cDnyilFU="

# Token 已設定完成

echo "🚀 啟動 LINE Career Bot..."
echo "📡 Webhook URL: https://136.115.85.72/callback"
echo ""

# 開發環境
# python app.py

# 正式環境（使用 gunicorn）
gunicorn -w 4 -b 0.0.0.0:5000 app:app --access-logfile - --error-logfile -
