import os
import sys, configparser
from flask import Flask, jsonify, request, abort, send_file
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from fsm import TocMachine
from utils import send_text_message

os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'

machine = TocMachine(
    states=["main_menu", "contents_and_images", "contents", "office_tables", "office_chairs_and_sofas",
            "contact_us", "contact_number", "address", "search_style_or_category", "search", "start_search", "category"],
    transitions=[
        {"trigger": "advance", "source": "main_menu", "dest": "search_style_or_category", "conditions": "is_going_to_search_style_or_category",},
        {"trigger": "advance", "source": "main_menu", "dest": "contents_and_images", "conditions": "is_going_to_contents_and_images",},
        {"trigger": "advance", "source": "main_menu", "dest": "contact_us", "conditions": "is_going_to_contact_us",},
        {"trigger": "advance", "source": "search_style_or_category", "dest": "search", "conditions": "is_going_to_search",},
        {"trigger": "advance", "source": "search_style_or_category", "dest": "category", "conditions": "is_going_to_category",},
        {"trigger": "advance", "source": "main_menu", "dest": "address", "conditions": "is_going_to_address",},
        {"trigger": "advance", "source": "main_menu", "dest": "contact_number", "conditions": "is_going_to_contact_number",},
        {"trigger": "advance", "source": "contact_us", "dest": "address", "conditions": "is_going_to_address",},
        {"trigger": "advance", "source": "contact_us", "dest": "contact_number", "conditions": "is_going_to_contact_number",},
        {"trigger": "advance", "source": ["main_menu","contents_and_images"], "dest": "office_chairs_and_sofas", "conditions": "is_going_to_office_chairs_and_sofas",},
        {"trigger": "advance", "source": ["main_menu","contents_and_images"], "dest": "office_tables", "conditions": "is_going_to_office_tables",},
        {"trigger": "advance", "source": ["main_menu","contents_and_images"], "dest": "contents", "conditions": "is_going_to_contents",},
        {"trigger": "advance", "source": "search", "dest": "start_search"},
        {"trigger": "advance", "source": "start_search", "dest": "search", "conditions": "is_going_to_backto_search"},
        {"trigger": "advance", "source": "main_menu", "dest": "main_menu", "conditions": "is_staying_at_main_menu"},
        {
            "trigger": "advance", 
            "source": ["category", "start_search", "search", "contents_and_images", "contents", "office_tables", "office_chairs_and_sofas", "contact_us", "contact_number", "address"], 
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu"
        },
        {
            "trigger": "advance", 
            "source": ["start_search", "main_menu", "contents_and_images", "contents", "office_tables", "office_chairs_and_sofas", "contact_us", "contact_number", "address"], 
            "dest": "search",
            "conditions": "is_going_to_search"
        },
    ],
    initial="main_menu",
    auto_transitions=False,
    show_conditions=True,
)
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
        print(f"\nFSM STATE: {machine.state}")
        # print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        # if response == False:
        #     send_text_message(event.reply_token, "Not Entering any State")
    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
