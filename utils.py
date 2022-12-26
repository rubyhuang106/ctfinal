import os

from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage


channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)


def send_text_message(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

    return "OK"
    
class state_machine():
    states = 0
    count = 0
    dice_again = False
    
    def switch_to_state1(self):
        self.states = 1

    def switch_to_divine(self):
        self.states = 2
        
    def switch_to_fortune(self):
        self.states = 3
        
    def switch_to_dice(self):
        self.states = 4
    
    def switch_to_waiting(self):
        self.states = 21
        self.count += 1
        
    def clear_count(self):
        self.count = 0
        

"""
def send_image_url(id, img_url):
    pass
def send_button_message(id, text, buttons):
    pass
"""
