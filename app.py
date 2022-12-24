import os
import sys, configparser
from flask import Flask, jsonify, request, abort, send_file
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from fsm import TocMachine
from utils import send_text_message
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("toclinebot-80594-firebase-adminsdk-g85c3-2673698c57.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'


states = ["main_menu", "contents_and_images", "contact_us", "search_style_or_category", "search", "start_search", "category"]
transitions = [{"trigger": "advance", "source": "main_menu", "dest": "search_style_or_category", "conditions": "is_going_to_search_style_or_category",},
        {"trigger": "advance", "source": "main_menu", "dest": "contents_and_images", "conditions": "is_going_to_contents_and_images",},
        {"trigger": "advance", "source": "main_menu", "dest": "contact_us", "conditions": "is_going_to_contact_us",},
        {"trigger": "advance", "source": "search_style_or_category", "dest": "search", "conditions": "is_going_to_search",},
        {"trigger": "advance", "source": "search_style_or_category", "dest": "category", "conditions": "is_going_to_category",},
        {"trigger": "advance", "source": "search", "dest": "start_search"},
        {"trigger": "advance", "source": "start_search", "dest": "search", "conditions": "is_going_to_backto_search"},
        {
            "trigger": "advance", 
            "source": ["main_menu", "category", "start_search", "search", "contents_and_images", "contact_us"], 
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu"
        },
        {
            "trigger": "advance", 
            "source": ["start_search", "main_menu", "contents_and_images", "contact_us"], 
            "dest": "search",
            "conditions": "is_going_to_search"
        }]


# machine = TocMachine(
#     states=["main_menu", "contents_and_images", "contact_us", "search_style_or_category", "search", "start_search", "category"],
#     transitions=[
#         {"trigger": "advance", "source": "main_menu", "dest": "search_style_or_category", "conditions": "is_going_to_search_style_or_category",},
#         {"trigger": "advance", "source": "main_menu", "dest": "contents_and_images", "conditions": "is_going_to_contents_and_images",},
#         {"trigger": "advance", "source": "main_menu", "dest": "contact_us", "conditions": "is_going_to_contact_us",},
#         {"trigger": "advance", "source": "search_style_or_category", "dest": "search", "conditions": "is_going_to_search",},
#         {"trigger": "advance", "source": "search_style_or_category", "dest": "category", "conditions": "is_going_to_category",},
#         {"trigger": "advance", "source": "search", "dest": "start_search"},
#         {"trigger": "advance", "source": "start_search", "dest": "search", "conditions": "is_going_to_backto_search"},
#         {
#             "trigger": "advance", 
#             "source": ["main_menu", "category", "start_search", "search", "contents_and_images", "contact_us"], 
#             "dest": "main_menu",
#             "conditions": "is_going_to_main_menu"
#         },
#         {
#             "trigger": "advance", 
#             "source": ["start_search", "main_menu", "contents_and_images", "contact_us"], 
#             "dest": "search",
#             "conditions": "is_going_to_search"
#         },
#     ],
#     initial="main_menu",
#     auto_transitions=False,
#     show_conditions=True,
# )
# machine.get_graph().draw("fsm.png", prog="dot", format="png")

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
config = configparser.ConfigParser()
config.read('config.ini')
channel_access_token = config.get('line-bot', 'channel_access_token')
channel_secret = config.get('line-bot', 'channel_secret')
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

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))
    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
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
        document_ref = db.collection("linebot_user_ids").document(event.source.user_id)
        state = document_ref.get()
        if(state.exists):
            initial_state = state.to_dict()['state']
        else:
            d = {'user_id': event.source.user_id, 'state': 'main_menu'}
            document_ref.set(d)
            initial_state = "main_menu"
        machine = TocMachine(states=states, transitions=transitions, initial=initial_state, auto_transitions=False, show_conditions=True)
        print(f"\nFSM STATE: {machine.state}")
        # print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        
        if(state.to_dict()['state'] != machine.state):
            document_ref.update({'state': machine.state})
        
    return "OK"


# @app.route("/show-fsm", methods=["GET"])
# def show_fsm():
#     machine.get_graph().draw("fsm.png", prog="dot", format="png")
#     return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 10000)
    app.run(host="0.0.0.0", port=port, debug=True)
