from flask import Flask, request, abort, send_from_directory
from whitenoise import WhiteNoise

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, PostbackEvent, FollowEvent, UnfollowEvent, JoinEvent,
    MemberJoinedEvent, MemberLeftEvent, LeaveEvent, TextMessage,
    TextSendMessage, ImageSendMessage, TemplateSendMessage,
    ButtonsTemplate, MessageTemplateAction, PostbackTemplateAction,
    CarouselTemplate, CarouselColumn
)

from apscheduler.schedulers.background import BackgroundScheduler

import sys, socket

from settings import SETTINGS
from db_utils import DB
from utils import UTILS

import os
import atexit

app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='file')

line_bot_api = LineBotApi(SETTINGS['CHANNEL_ACCESS_TOKEN']) # channel access token
handler = WebhookHandler(SETTINGS['CHANNEL_SECRET']) # channel secret

db = DB()

import time

def menu(id):
    button_template = TemplateSendMessage(
        alt_text='歡迎使用我的line bot',
        template=ButtonsTemplate(
            title='歡迎使用我的linebot',
            text='嗨，我有提供一些功能供您使用，也可以藉由這個linebot更加認識我，藉由輸入menu重新獲得這個button',
            thumbnail_image_url='https://linebot4jam3s.herokuapp.com/dog3.jpg',
            actions=[
                PostbackTemplateAction(
                    label='關於我',
                    data='about'
                ),
                PostbackTemplateAction(
                    label='小工具',
                    data='tool'
                )
            ]
        )
    )

    line_bot_api.push_message(id, button_template)

def toolTemplate(id):
    button_template = TemplateSendMessage(
        alt_text='歡迎使用我的line bot',
        template=ButtonsTemplate(
            thumbnail_image_url='https://linebot4jam3s.herokuapp.com/dog2.jpeg',
            title='小工具',
            text='這是我實作的一些簡單的tools',
            actions=[
                PostbackTemplateAction(
                    label='高鐵時刻表',
                    data='查詢高鐵方式\nexample: high: 狀態 去回程, 起始站 南港, 終點站 左營, 出發日期 2021/05/24, 出發時間 23:00, 回程日期 2021/05/25, 回程時間 23:00\n狀態: 單程, 去回程\n高鐵車站: 南港, 台北, 板橋, 桃園, 新竹, 苗栗, 台中, 彰化, 雲林, 嘉義, 台南, 左營\n假設為單程的話則不需要回程日期、回程時間'
                ),
                PostbackTemplateAction(
                    label='TODOLIST',
                    data='使用方式\nexample:\n1. todo: 新增: 考試\n2. todo: 更新: 考試\n3. todo: 查詢: 完成\n4. todo: 刪除: 考試\n查詢狀態: 完成/未完成/全部'
                )
            ]
        )
    )

    line_bot_api.push_message(id, button_template)

def aboutMe(id):
    button_template = TemplateSendMessage(
        alt_text='歡迎使用我的line bot',
        template=ButtonsTemplate(
            title='認識更多關於James',
            text='嗨，這是我的linebot，可以藉由這個linebot更加認識我',
            thumbnail_image_url='https://linebot4jam3s.herokuapp.com/dog.jpg',
            actions=[
                PostbackTemplateAction(
                    label='觀看履歷',
                    data='resume'
                ),
                PostbackTemplateAction(
                    label='自我介紹',
                    data='introduction'
                ),
                PostbackTemplateAction(
                    label='Github',
                    data='github'
                )
            ]
        )
    )

    line_bot_api.push_message(id, button_template)

def highwayHandler(id, strr):
    search_type = ('單程', '去回程')
    dicts = {}
    data = {}
    for i in strr.split(','):
        try:
            tmp = i.strip().split(' ')
            dicts[tmp[0].strip()] = tmp[1].strip()
        except:
            break

    if dicts.get('狀態', '') in search_type:
        data = {
            'start_date': dicts['出發日期'],
            'start_time': dicts['出發時間'],
            'start_station': dicts['起始站'],
            'return_station': dicts['終點站'],
            'return_date': dicts['回程日期'],
            'return_time': dicts['回程時間'],
            'search_type': 'S' if search_type.index(dicts['狀態']) == 0 else 'R'
        }

        msgs = UTILS.highway_crawler(data)
        if msgs:
            for msg in msgs:
                db.insert_message(id, msg, True)
            return

    db.insert_message(id, '很抱歉，您的高鐵查詢指令有錯誤!', True)

def todoListHandler(id, strr):
    strr = strr.strip()
    pos = strr.find(':')
    action = strr[:pos]
    strr = strr[(pos+1):].strip()
    action_map = {
        '新增': 'create',
        '更新': 'update',
        '查詢': 'query',
        '刪除': 'delete'
    }

    action = action_map.get(action)

    msg = '很抱歉，您的 TODOLIST 指令有錯誤!'
    if action == 'create':
        status = db.insert_todo_list(id, strr)
        msg = '新增成功' if status else 'TODOLIST名稱已重複'
    elif action == 'update':
        status = db.update_todo_list(id, strr)
        msg = '更新成功' if status else '更新失敗'
    elif action == 'query':
        tuple_action = ('全部', '完成', '未完成')
        if strr in tuple_action:
            if strr == '全部':
                l = db.query_todo_list(id)
            else:
                l = db.query_todo_list(id, True if strr == '完成' else False)
            if len(l) == 0:
                msg = '沒有任何符合的任務'
            else:
                msg = '\n'.join(map(lambda x: '%s: %s' % (x[2], '完成' if x[3] else '未完成'), l))
        else:
            msg = '新增指令錯誤'
    elif action == 'delete':
        db.delete_todo_list(id, strr)
        msg = '刪除成功'

    db.insert_message(id, msg, True)

def handleMSG(id, text, status):
    text = text.strip()

    if text[:4].lower() == 'menu':
        menu(id)
    elif text[:6].lower() == 'resume':
        line_bot_api.push_message(id, ImageSendMessage(
            original_content_url="https://linebot4jam3s.herokuapp.com/resume.jpg",
            preview_image_url="https://linebot4jam3s.herokuapp.com/resume.jpg")
        )
    elif text[:5].lower() == 'about':
        aboutMe(id)
    elif text[:4].lower() == 'tool':
        toolTemplate(id)
    elif text[:5].lower() == 'todo:':
        todoListHandler(id, text[5:])
    elif text[:5].lower() == 'high:':
        highwayHandler(id, text[5:])
    elif text[:12].lower() == 'introduction':
        line_bot_api.push_message(id, TextSendMessage('嗨，你好我叫做何政剛。今年就讀台大電機所資訊科學組碩一。\n\
有3年的 Unix-Like OS 使用經驗，Linux為主，也有MacOS的使用經驗。有不少的網站開發經驗，主力於後端開發，\n\
DBMS有使用過 MongoDB/ MySQL/ PostgreSQL/ DynamoDB/ ES，\平常通常是用 PostgreSQL。\n\
有過一些雲端的使用經驗，例如 AWS, GCP 的一些服務，像是 AWS EC2, AWS S3, AWS SMS, GCP GAE, GCP GCE。\n\
另外我還有一些 Virtualization的開發經驗，像是 VirtualBox, VMware ESXI, Docker。\n\
我最擅長的語言是 Python，但也會其他的語言像是 C++, Java, JavaScript。我熱愛學習新的技術，希望未來可以成為更加成熟的軟體工程師。'))
    elif text[:6].lower() == 'github':
        line_bot_api.push_message(id, TextSendMessage('https://github.com/james0828'))
    else:
        # 如果是聊天機器人這邊發出的話，回傳
        if status:
            line_bot_api.push_message(id, TextSendMessage(text))
        else:
            line_bot_api.push_message(id, TextSendMessage('很抱歉，您輸入的指令沒有用途，請輸入menu查看使用選單'))
            

def reply_message():
    msgs = db.query_message()
    for msg in msgs:
        handleMSG(msg[1], msg[2], msg[3])
        db.update_message(msg[0])

    db.commit()

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 47200))
except socket.error:
    print("!!!scheduler already started, DO NOTHING")
else:
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=reply_message, trigger="interval", seconds=1)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    print("scheduler started")

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if getattr(event.source, 'group_id', None):
        db.insert_message(event.source.group_id, event.message.text)
    elif getattr(event.source, 'room_id', None):
        db.insert_message(event.source.room_id, event.message.text)
    else:
        db.insert_message(event.source.user_id, event.message.text)

@handler.add(PostbackEvent)
def handle_post_message(event):
    if getattr(event.source, 'group_id', None):
        db.insert_message(event.source.group_id, event.postback.data, True)
    elif getattr(event.source, 'room_id', None):
        db.insert_message(event.source.room_id, event.postback.data, True)
    else:
        db.insert_message(event.source.user_id, event.postback.data, True)

@handler.add(FollowEvent)
def handle_follow(event):
    menu(event.source.user_id)

@handler.add(JoinEvent)
def handle_follow(event):
    db.insert_message(event.source.user_id, '嗨，輸入 menu 可以查看選單', True)
    menu(event.source.user_id)

@handler.add(MemberJoinedEvent)
def handle_follow(event):
    if getattr(event.source, 'group_id', None):
        room_id = event.source.group_id
    else:
        room_id = event.source.room_id
    users = []
    for m in event.joined.members:
        user_id = getattr(m, 'user_id', None)
        if user_id:
            profile = line_bot_api.get_profile(m.user_id)
            users.append(profile.display_name)
    
    if len(users) !=0:
        db.insert_message(room_id, '歡迎 %s 的加入，輸入 menu 可以查看選單' % ','.join(users), True)

@handler.add(MemberLeftEvent)
def handle_follow(event):
    if getattr(event.source, 'group_id', None):
        room_id = event.source.group_id
    else:
        room_id = event.source.room_id

    users = []
    for m in event.left.members:
        user_id = getattr(m, 'user_id', None)
        if user_id:
            profile = line_bot_api.get_profile(m.user_id)
            users.append(profile.display_name)
    
    if len(users) !=0:
        db.insert_message(room_id, '很遺憾，在我們的群組缺少了 %s %s使用者，為了避免更多人退出，請輸入 menu 查看選單' % (','.join(users), '這個' if len(users) == 1 else '這些'), True)


if __name__ == "__main__":
    app.run(use_reloader=False)