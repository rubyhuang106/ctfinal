from transitions.extensions import GraphMachine
from functools import partial

from utils import send_text_message


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_state1(self, event):
        text = event.message.text
        return text.lower() == "go to state1"

    def is_going_to_state2(self, event):
        text = event.message.text
        return text.lower() == "go to state2"

    def on_enter_state1(self, event):
        print("I'm entering state1")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state1")
        self.go_back()

    def on_exit_state1(self):
        print("Leaving state1")

    def on_enter_state2(self, event):
        print("I'm entering state2")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state2")
        self.go_back()

    def on_exit_state2(self):
        print("Leaving state2")

class Model:
    def clear_state(self, deep=False, force=False):
        print("Clearing state ...")
        return True


model = Model()
machine = GraphMachine(model=model, states=['idle', '選擇', '占卜', '改運', '擲筊', '等待'],
                       transitions=[
                           {'trigger': "輸入", 'source': 'idle', 'dest': '選擇', 'conditions': "開始"},
                           {'trigger': "輸入", 'source': '選擇', 'dest': '占卜',
                            'conditions': "占卜"},
                           {'trigger': "輸入", 'source': '選擇', 'dest': '改運', 'conditions': "改運"},
                           {'trigger': "輸入", 'source': '選擇', 'dest': '擲筊', 'conditions': "擲筊"},
                           {'trigger': "輸入", 'source': '改運', 'dest': '等待', 'conditions': "非數字"},
                           {'trigger': "", 'source': '等待', 'dest': '選擇', 'conditions': "三次輸入非數字"},
                           {'trigger': "輸入", 'source': '等待', 'dest': '改運', 'conditions': "數字"},
                           {'trigger': "結束", 'source': ['占卜', '改運', '擲筊'], 'dest': '選擇'}
                       ],
                       initial='idle', show_conditions=True)

model.get_graph().draw('my_state_diagram.png', prog='dot')
