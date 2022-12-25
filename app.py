import os
import sys
import random

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message
from utils import state_machine

load_dotenv()


machine = TocMachine(
    states=["user", "state1", "state2"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state1",
            "conditions": "is_going_to_state1",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state2",
            "conditions": "is_going_to_state2",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state3",
            "conditions": "is_going_to_state3",
        },
        {"trigger": "go_back", "source": ["state1", "state2", "state3"], "dest": "user"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

sm = state_machine()

app = Flask(__name__, static_url_path="")

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)

if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        msg = event.message.text
        reply = msg
        random.seed(None)
        ask_again = "\n\n如要繼續，請輸入「占卜」、「改運」或「擲筊」"
        fortunate = [['天降祥瑞', '小確幸', '平平無奇', '小心夜路', '諸事不順'],
                     ['紅鸞星動', '累世情緣', '喜提狗糧', '孤單寂寞冷', '虐戀情深'],
                     ['鴻運當頭', '吉星高照', '穩紮穩打', '如履薄冰', '打包回家']]
                     
        sentence = {'天降祥瑞':'你最近有如神助，萬事順心！',
                    '小確幸':'雖然沒有逆天的運氣，但不時會遇到讓你會心一笑的人事物喔！',
                    '平平無奇':'你的運氣實在是平凡的無話可說。',
                    '小心夜路':'當心，你可能會陰溝裡翻船！',
                    '諸事不順':'沒什麼好說的了，祈禱吧。',
                    '紅鸞星動':'大喜之日，別忘了送一份請帖給我。',
                    '累世情緣':'你和你對象如果不是真的，我就是假的！',
                    '喜提狗糧':'只有你被閃，沒有你閃別人。這邊誠心建議備好墨鏡。',
                    '孤單寂寞冷':'孤獨的滋味是一個人慶祝情人節。',
                    '虐戀情深':'前路艱險，為你掬一把同情淚。',
                    '鴻運當頭':'升官發財近在眼前，別猶豫，上吧！',
                    '吉星高照':'近日或遇命中貴人，良機莫誤！',
                    '穩紮穩打':'跬步千里，切莫心急。',
                    '如履薄冰':'小心駛得萬年船，建議常懷戒慎恐懼之心。',
                    '打包回家':'很遺憾，幫你為你的錢包默哀三秒。'}

        if sm.states == 0:
            if msg == "開始":
                reply = "歡迎！\n\n輸入「占卜」可占卜運勢\n輸入「改運」可扭轉運勢\n輸入「擲筊」可求神問卦"
                sm.switch_to_state1()
            else:
                reply = "請輸入開始以啟用機器人"
        elif sm.states == 1:
            if msg == "占卜":
                sm.switch_to_divine()
                reply = "請問你想要占卜的項目是「運勢」、「感情」還是「事業」？"
            elif msg == "改運":
                reply = "沒問題！請輸入一個數字，我將為你檢測你的幸運值。"
                sm.switch_to_fortune()
            elif msg == "擲筊":
                reply = "你想要向神明詢問什麼問題？"
                sm.switch_to_dice()
            else:
                reply = "請輸入「占卜」、「改運」或「擲筊」"
        elif sm.states == 2:  #占卜
            id = -1
            luck = random.randint(1, 101)
            end = "\n\n占卜結束，請重新選擇「占卜」、「改運」或「擲筊」"
            start = "占卜結果為："
            if msg == "運勢":
                id = 0
            elif msg == "感情":
                id = 1
            elif msg == "事業":
                id = 2
            else:
                reply = "請輸入「運勢」、「感情」或「事業」！"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(reply))
                continue
                
            if luck >= 95:
                reply = start + fortunate[id][0] + "\n\n" + sentence[fortunate[id][0]] + end
            elif luck >= 80:
                reply = start + fortunate[id][1] + "\n\n" + sentence[fortunate[id][1]] + end
            elif luck >= 40:
                reply = start + fortunate[id][2] + "\n\n" + sentence[fortunate[id][2]] + end
            elif luck >= 5:
                reply = start + fortunate[id][3] + "\n\n" + sentence[fortunate[id][3]] + end
            else:
                reply = start + fortunate[id][4] + "\n\n" + sentence[fortunate[id][4]] + end
            sm.switch_to_state1()
        elif sm.states == 3:  #改運
            try:
                seed = int(msg)
                random.seed(seed)
                luck = random.randint(1, 101)
                if luck >= 75:
                    reply = "你的運氣已經不差了，不可以太貪心喔！" + ask_again
                elif luck >= 20:
                    reply = "你的運氣看來很普通，不過現在已經成功變好了。" + ask_again
                else:
                    reply = "哎呀，看來你的運氣已經無法被拯救了，祝你好運。" + ask_again
                sm.switch_to_state1()
            except:
                reply = "請輸入數字！"
        elif sm.states == 4:  #擲筊
            luck = random.randint(1, 101)
            if luck > 50:
                reply = "擲筊結果是：聖杯。" + ask_again
            elif luck > 25:
                reply = "擲筊結果是：怒杯。" + ask_again
            else:
                reply = "神明笑而不語。" + ask_again
                
            sm.switch_to_state1()
        else:
            reply = "錯誤回覆"
        
            
        line_bot_api.reply_message(event.reply_token, TextSendMessage(reply))

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    check_state = 0
    signature = request.headers["X-Line-Signature"]
    print("try again")
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")
    
def initialize():
    check_state = 0


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
