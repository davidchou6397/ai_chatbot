# 生涯規劃 LINE Chat Bot

## 快速開始

### 1. 安裝依賴
```bash
pip install -r requirements.txt
```

### 2. 設定環境變數
```bash
export LINE_CHANNEL_SECRET="a219bfd132141cc5aa02f95399545a16"
export LINE_CHANNEL_ACCESS_TOKEN="你的_ACCESS_TOKEN"
```

或直接修改 `app.py` 中的設定。

### 3. 取得 Channel Access Token
1. 前往 LINE Developers Console
2. 選擇你的 Channel
3. 到 Messaging API 頁籤
4. 找到「Channel access token (long-lived)」
5. 點選「Issue」產生 Token

### 4. 啟動服務

**開發測試：**
```bash
python app.py
```

**正式環境（使用 gunicorn）：**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 搭配 Nginx + SSL

### Nginx 設定範例
```nginx
server {
    listen 443 ssl;
    server_name 136.115.85.72;

    ssl_certificate /etc/ssl/certs/your_cert.pem;
    ssl_certificate_key /etc/ssl/private/your_key.pem;

    location /callback {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Line-Signature $http_x_line_signature;
    }
}
```

### 使用 Let's Encrypt（如果有域名）
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 使用自簽憑證（測試用，LINE 可能不接受）
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/selfsigned.key \
  -out /etc/ssl/certs/selfsigned.crt
```

## 使用 systemd 管理服務

建立 `/etc/systemd/system/linebot.service`：
```ini
[Unit]
Description=LINE Career Bot
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/line-career-bot
Environment="LINE_CHANNEL_SECRET=your_secret"
Environment="LINE_CHANNEL_ACCESS_TOKEN=your_token"
ExecStart=/usr/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

啟動服務：
```bash
sudo systemctl daemon-reload
sudo systemctl enable linebot
sudo systemctl start linebot
sudo systemctl status linebot
```

## 功能說明

### 使用者指令
| 指令 | 功能 |
|------|------|
| 開始 / 生涯規劃 | 開始測驗 |
| 重新開始 | 重新測驗 |
| 我的結果 | 查看上次結果 |
| 說明 | 查看說明 |

### 測驗流程
1. 目前身份
2. 興趣領域
3. 核心優勢
4. 偏好工作型態
5. 重視的目標
6. 期望時程

完成後會產生個人化的職涯建議報告。

## 檔案結構
```
line-career-bot/
├── app.py              # 主程式
├── requirements.txt    # Python 依賴
└── README.md          # 說明文件
```

## 常見問題

### Q: LINE 顯示 Webhook 驗證失敗？
1. 確認伺服器有回應 200 OK
2. 確認 SSL 憑證有效
3. 確認 Channel Secret 正確

### Q: Bot 沒有回應？
1. 確認 Channel Access Token 正確
2. 確認已關閉「Auto-reply messages」
3. 查看伺服器 log

### Q: 如何查看 log？
```bash
# 使用 systemd
journalctl -u linebot -f

# 直接執行時
python app.py  # 會顯示在終端機
```
