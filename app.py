"""
生涯規劃 LINE Chat Bot
"""
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage, 
    QuickReply, QuickReplyItem, MessageAction
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
import os
import json

app = Flask(__name__)

# ============ 設定區 ============
# 請替換成你的 Token（建議用環境變數）
CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', 'a219bfd132141cc5aa02f95399545a16')
CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', 'aFz9hv4mLW6sVIGauZcIuRWa/j9faB4X3YhmK0MYx12mm4VVmM6lFwHOaX3/0j8SSx7VCgy4v7417/Lnj30TjVvvmGpn/mrleO9K8+FczV5odujjXNf2ND4AJE+N4/RlWl/ducs6P4/Qkq7Iqz0ivwdB04t89/1O/w1cDnyilFU=')

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# ============ 用戶狀態管理 ============
# 正式環境建議改用 Redis 或資料庫
user_sessions = {}

# ============ 生涯規劃問答流程 ============
CAREER_QUESTIONS = [
    {
        'id': 'identity',
        'question': '👋 歡迎使用生涯規劃助手！\n\n請問你目前的身份是？',
        'options': ['學生', '社會新鮮人', '在職中', '轉職考慮中', '待業中']
    },
    {
        'id': 'interest',
        'question': '🎯 你對哪個領域比較有興趣？',
        'options': ['科技/資訊', '商業/金融', '創意/設計', '醫療/照護', '教育/研究', '製造/工程']
    },
    {
        'id': 'strength',
        'question': '💪 你認為自己最大的優勢是？',
        'options': ['邏輯分析', '溝通表達', '創意發想', '細心耐心', '領導統籌', '動手實作']
    },
    {
        'id': 'work_style',
        'question': '🏢 你偏好的工作型態？',
        'options': ['穩定大公司', '新創公司', '自由接案', '創業當老闆', '公職/教職']
    },
    {
        'id': 'goal',
        'question': '🌟 你最重視的職涯目標是？',
        'options': ['高薪收入', '工作生活平衡', '自我成長', '社會影響力', '穩定安全感']
    },
    {
        'id': 'timeline',
        'question': '⏰ 你希望在多久內達成轉變？',
        'options': ['3個月內', '半年內', '1年內', '2-3年', '慢慢來不急']
    }
]

# ============ 職涯建議對照表 ============
CAREER_SUGGESTIONS = {
    '科技/資訊': {
        '邏輯分析': ['軟體工程師', '資料分析師', '系統架構師', 'AI/ML工程師'],
        '創意發想': ['UI/UX設計師', '產品經理', '遊戲設計師'],
        '溝通表達': ['技術PM', '解決方案架構師', '技術寫手'],
        '領導統籌': ['技術主管', 'CTO', '專案經理'],
        '動手實作': ['全端工程師', '嵌入式工程師', 'DevOps工程師'],
        '細心耐心': ['QA工程師', '資安分析師', 'DBA']
    },
    '商業/金融': {
        '邏輯分析': ['財務分析師', '管理顧問', '精算師'],
        '溝通表達': ['業務經理', '客戶經理', '公關經理'],
        '領導統籌': ['專案經理', '營運經理', '創業家'],
        '創意發想': ['行銷企劃', '品牌經理', '商業開發'],
        '細心耐心': ['會計師', '稽核', '風控專員'],
        '動手實作': ['營運專員', '供應鏈管理', '採購專員']
    },
    '創意/設計': {
        '創意發想': ['平面設計師', '插畫家', '藝術總監'],
        '邏輯分析': ['UX研究員', '資訊設計師'],
        '溝通表達': ['創意總監', '品牌顧問'],
        '動手實作': ['視覺設計師', '動態設計師', '3D設計師'],
        '領導統籌': ['設計主管', '創意總監'],
        '細心耐心': ['排版設計師', '印刷設計師']
    },
    '醫療/照護': {
        '細心耐心': ['護理師', '藥師', '醫檢師'],
        '溝通表達': ['社工師', '心理諮商師', '個管師'],
        '邏輯分析': ['醫師', '臨床研究員'],
        '動手實作': ['物理治療師', '職能治療師', '牙醫師'],
        '領導統籌': ['護理長', '醫務管理師'],
        '創意發想': ['藝術治療師', '音樂治療師']
    },
    '教育/研究': {
        '溝通表達': ['教師', '講師', '培訓師'],
        '邏輯分析': ['研究員', '學者', '資料科學家'],
        '創意發想': ['課程設計師', '教育科技專家'],
        '細心耐心': ['圖書館員', '檔案管理師'],
        '領導統籌': ['教育主管', '校長', '研究主持人'],
        '動手實作': ['實驗室技術員', '教學助理']
    },
    '製造/工程': {
        '動手實作': ['機械工程師', '電子工程師', '製程工程師'],
        '邏輯分析': ['品管工程師', '工業工程師', 'R&D工程師'],
        '領導統籌': ['廠長', '生產主管', '專案工程師'],
        '細心耐心': ['品保工程師', '測試工程師'],
        '創意發想': ['產品研發', '工業設計師'],
        '溝通表達': ['FAE', '技術業務', '供應商管理']
    }
}

# ============ 路由 ============
@app.route("/", methods=['GET'])
def home():
    return "LINE Career Bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    app.logger.info(f"Request body: {body}")
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature")
        abort(400)
    
    return 'OK'

# ============ 訊息處理 ============
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    user_text = event.message.text.strip()
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        # 開始/重新開始指令
        if user_text in ['開始', '生涯規劃', '重新開始', '測驗', '開始測驗']:
            user_sessions[user_id] = {'step': 0, 'answers': {}}
            reply = create_question_message(0)
        
        # 查看結果
        elif user_text == '我的結果':
            if user_id in user_sessions and 'result' in user_sessions[user_id]:
                reply = TextMessage(text=user_sessions[user_id]['result'])
            else:
                reply = TextMessage(text='你還沒有完成測驗喔！\n輸入「開始」來進行生涯規劃測驗。')
        
        # 說明
        elif user_text in ['說明', '幫助', 'help', '?', '？']:
            reply = TextMessage(text=get_help_text())
        
        # 處理問答流程
        elif user_id in user_sessions and 'step' in user_sessions[user_id]:
            session = user_sessions[user_id]
            current_step = session['step']
            
            if current_step < len(CAREER_QUESTIONS):
                # 儲存答案
                question_id = CAREER_QUESTIONS[current_step]['id']
                session['answers'][question_id] = user_text
                session['step'] = current_step + 1
                
                # 下一題或產生結果
                if session['step'] < len(CAREER_QUESTIONS):
                    reply = create_question_message(session['step'])
                else:
                    # 產生結果
                    result_text = generate_career_result(session['answers'])
                    session['result'] = result_text
                    reply = TextMessage(text=result_text)
            else:
                reply = TextMessage(text='測驗已完成！\n輸入「重新開始」可以再測一次。')
        
        # 預設回覆
        else:
            reply = TextMessage(text='👋 嗨！我是生涯規劃助手。\n\n輸入「開始」來進行職涯探索測驗！\n輸入「說明」查看更多功能。')
        
        # 發送回覆
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[reply]
            )
        )

def create_question_message(step):
    """建立問題訊息（含快速回覆按鈕）"""
    question = CAREER_QUESTIONS[step]
    progress = f"({step + 1}/{len(CAREER_QUESTIONS)})"
    
    quick_reply = QuickReply(items=[
        QuickReplyItem(action=MessageAction(label=opt[:20], text=opt))
        for opt in question['options']
    ])
    
    return TextMessage(
        text=f"{progress} {question['question']}",
        quick_reply=quick_reply
    )

def generate_career_result(answers):
    """根據答案產生職涯建議"""
    identity = answers.get('identity', '未知')
    interest = answers.get('interest', '科技/資訊')
    strength = answers.get('strength', '邏輯分析')
    work_style = answers.get('work_style', '穩定大公司')
    goal = answers.get('goal', '高薪收入')
    timeline = answers.get('timeline', '1年內')
    
    # 取得職業建議
    field_suggestions = CAREER_SUGGESTIONS.get(interest, {})
    careers = field_suggestions.get(strength, ['建議進一步諮詢職涯顧問'])
    
    # 根據工作型態調整建議
    style_tips = {
        '穩定大公司': '建議優先考慮知名企業或上市公司，累積完整經歷。',
        '新創公司': '新創環境能快速成長，但需評估公司穩定性。',
        '自由接案': '建議先累積作品集與人脈，逐步轉型。',
        '創業當老闆': '建議先在相關產業累積經驗與資源。',
        '公職/教職': '需準備國考或教師資格，建議提早規劃。'
    }
    
    # 根據時程給建議
    timeline_tips = {
        '3個月內': '時間緊迫，建議聚焦現有技能可快速轉換的職位。',
        '半年內': '有時間進行 1-2 個技能補強或證照準備。',
        '1年內': '可以進行較完整的轉型準備，包含進修課程。',
        '2-3年': '有充足時間進行深度學習或學位進修。',
        '慢慢來不急': '可以邊工作邊探索，逐步調整方向。'
    }
    
    result = f"""🎊 生涯規劃分析報告

━━━━━━━━━━━━━━━━━━━━
📋 你的選擇摘要
━━━━━━━━━━━━━━━━━━━━
• 目前身份：{identity}
• 興趣領域：{interest}
• 核心優勢：{strength}
• 偏好型態：{work_style}
• 重視目標：{goal}
• 期望時程：{timeline}

━━━━━━━━━━━━━━━━━━━━
💼 推薦職業方向
━━━━━━━━━━━━━━━━━━━━
"""
    
    for i, career in enumerate(careers[:4], 1):
        result += f"{i}. {career}\n"
    
    result += f"""
━━━━━━━━━━━━━━━━━━━━
💡 個人化建議
━━━━━━━━━━━━━━━━━━━━
🏢 {style_tips.get(work_style, '')}

⏰ {timeline_tips.get(timeline, '')}

━━━━━━━━━━━━━━━━━━━━
📚 建議下一步
━━━━━━━━━━━━━━━━━━━━
1️⃣ 研究推薦職業的技能需求
2️⃣ 盤點現有技能與缺口
3️⃣ 制定學習計畫
4️⃣ 建立作品集或專案經驗
5️⃣ 更新履歷，開始投遞

━━━━━━━━━━━━━━━━━━━━
輸入「重新開始」可以再測一次
輸入「我的結果」查看此報告"""
    
    return result

def get_help_text():
    """說明文字"""
    return """📖 生涯規劃助手使用說明

🔹 開始測驗
輸入「開始」或「生涯規劃」

🔹 重新測驗
輸入「重新開始」

🔹 查看結果
輸入「我的結果」

🔹 查看說明
輸入「說明」

━━━━━━━━━━━━━━━━━━━━
測驗共 6 題，約需 2 分鐘
完成後會收到個人化職涯建議報告！"""

# ============ 主程式 ============
if __name__ == "__main__":
    # 開發環境用，正式環境請用 gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)
