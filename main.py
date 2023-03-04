import os
from os.path import join, dirname
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


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


Base.metadata.create_all(bind=engine)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")


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


SocketModeHandler(app, SLACK_APP_TOKEN).start()
