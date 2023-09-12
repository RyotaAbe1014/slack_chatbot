import os
from os.path import join, dirname
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# openai
import openai

# APScheduler
from apscheduler.schedulers.blocking import BlockingScheduler


load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


#  DB接続
engine = create_engine('sqlite:///slack.db', echo=True)
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
session = Session()
Base = declarative_base()


# テーブル定義
class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    text = Column(String)


# テーブル作成
Base.metadata.create_all(bind=engine)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
openai.api_key = os.environ.get("CHATGPT_API_KEY")


app = App(token=SLACK_BOT_TOKEN)


# respond_to_mention関数内で、作成した関数を呼び出してメッセージを保存する
@app.event("app_mention")
def respond_to_mention(event, say):
    mention = event['text'].split(' ')[0]
    # メンションが@testbotだった場合のみ、メッセージを保存する
    if mention == '<@U04S5VCS3JP>':
        try:
            message = event['text'].split(' ')[1]
            # メッセージを保存する
            session.add(Message(text=message))
            session.commit()
            session.close()
            say("保存しました")
        except:
            session.rollback()
            session.close()
            say("保存に失敗しました")


# chatgpt
# gptが含まれている場合のみ、chatgptを呼び出す
@app.message("gpt")
def message_hello(message, say):
    message = message['text'].split(' ')[1]
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "日本語で返答してください。"
            },
            {
                "role": "user",
                "content": message
            },
        ],
    )
    print(res)
    say(res["choices"][0]["message"]["content"])


# APScheduler
# 1分ごとに現在時刻を投稿する
scheduler = BlockingScheduler()


@scheduler.scheduled_job('interval', minutes=1)
def timed_job():
    response = app.client.chat_postMessage(
        channel="aaa", text="Hello, world!")


if __name__ == "__main__":
    # Socket Modeで起動
    print("start")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
    scheduler.start()