import os
from os.path import join, dirname
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")


app = App(token=SLACK_BOT_TOKEN)


# respond_to_mention関数内で、作成した関数を呼び出してメッセージを保存する
@app.event("app_mention")
def respond_to_mention(event, say):
    mention = event['text'].split(' ')[0]
    # メンションが@testbotだった場合のみ、メッセージを保存する
    if mention == '<@U04S5VCS3JP>':
        say("保存しました")
    else:
        say("not mention @testbot")


SocketModeHandler(app, SLACK_APP_TOKEN).start()
