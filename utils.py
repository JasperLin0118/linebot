import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials as SAC
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, ImageSendMessage, URITemplateAction, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction, CarouselColumn, CarouselContainer, CarouselTemplate, ImageCarouselColumn, ConfirmTemplate, MessageAction, ImageCarouselTemplate, LocationSendMessage
import requests
import bs4
import time

channel_access_token = "d7LmOXC9iutUkR//iJHfWy55z5oWmOkz2/Nx1FM34Y5LVfbTdwe+n/cCjcARAax+CD1oRkPGMKAWTKdi2P84uJSq5RBLYs4P4nwdMc9SkTtXK2oiKMyp6ch5XFsRFSOGNlOyH3iId6EPkKJnugb3+QdB04t89/1O/w1cDnyilFU=/bfDiSkEsrHaYtAS/fKH6vi9aMnwsM08hZJmg/xwPJVD="

styles = {'不限': "", '現代風' : "Modern", '簡約風':"Simplicity", 
            '飯店風':"Hotel", '奢華風':"Luxury", '休閒風':"Leisure", 
            '鄉村風':"Rustic", '混搭風':"Mashup", '日式':"Japanese", 
            'LOFT':"Industrial", '前衛風':"AvantGarde"}
styles_ind = ['不限', '現代風', '簡約風', '飯店風', '奢華風', '休閒風', 
              '鄉村風', '混搭風', '日式', 'LOFT', '前衛風'] 

def send_text_message(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))
    return "OK"

def show_search_style_or_category(reply_token):
    line_bot_api = LineBotApi(channel_access_token)
    Carousel_template = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/GVWVqOO.png',
                title='請選擇要查詢的風格或類別',
                text=' ',
                actions=[
                    MessageTemplateAction(
                        label='風格',
                        text='search'
                    ),
                    MessageTemplateAction(
                        label="類別",
                        text="category"
                    )
                ]
            )
        ]
    )
    )
    line_bot_api.reply_message(reply_token,Carousel_template)

def show_category(reply_token):
    line_bot_api = LineBotApi(channel_access_token)
    Carousel_template = TemplateSendMessage(
        alt_text='Image Carousel template',
        template=ImageCarouselTemplate(
        columns=[
            ImageCarouselColumn(
                image_url='https://i.imgur.com/EsGdyZi.png',
                action=URITemplateAction(
                        label='大會議室',
                        uri='https://officesnapshots.com/photos/?filter_meeting-spaces=large-meeting-room'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://i.imgur.com/lpdriMH.png',
                action=URITemplateAction(
                        label='小會議室',
                        uri='https://officesnapshots.com/photos/?filter_meeting-spaces=small-meeting-room'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://i.imgur.com/o8sd5bc.png',
                action=URITemplateAction(
                        label='開放式工作站',
                        uri='https://officesnapshots.com/photos/?filter_work-spaces=open-office'
                    )
            )
        ]
    )
    )
    line_bot_api.reply_message(reply_token,Carousel_template)

def show_search(reply_token):
    line_bot_api = LineBotApi(channel_access_token)
    prefer = "請輸入想要的風格或編號:\n"
    ind = 1
    for key, value in styles.items():
        if(ind != len(styles)):
            prefer += f"{ind:2d}: {key}\n"
        else:
            prefer += f"{ind:2d}: {key}"
        ind += 1
    line_bot_api.reply_message(reply_token, TextSendMessage(text=prefer))
    
def show_start_search(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    url_end = '&pattern=Office&page=1'
    if(text.isdigit() and (int(text) > 0 and int(text) <= len(styles_ind))):
        url = 'https://decotv.com.tw/gallery?works=' + styles[styles_ind[int(text)-1]] + url_end
    elif(not text.isdigit() and text in styles.keys()):
        url = 'https://decotv.com.tw/gallery?works=' + styles[text] + url_end
    else:
        line_bot_api.reply_message(reply_token,TextSendMessage(text="輸入錯誤，請重新輸入"))
    # , headers={"user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
    response = requests.get(url)
    html = bs4.BeautifulSoup(response.text, 'html.parser')
    links = html.find_all("img", {"class": "bgimg"})
    links2 = html.find_all("div", {"class": "frameitemin caseclicknew btn"})
    time.sleep(3)
    popup_url_link = []
    img_urls = []
    popup_url = 'https://decotv.com.tw/works_thisid,'
    popup_url_mid = '_thispic,'
    links_length = 5 if len(links) > 5 else len(links)
    for i in range(links_length):
        img_urls.append('https://decotv.com.tw/' + links[i]['src'])
        popup_url_link.append(popup_url + links2[i].get("data-id") + popup_url_mid + links2[i].get("data-pic"))
      
    imagecarouselcolumns = []
    for i in range(links_length):
        imagecarouselcolumns.append(
            ImageCarouselColumn(
                image_url=img_urls[i],
                action=URITemplateAction(label=str(i+1), uri=popup_url_link[i])))
    if(len(links) > 5):
        imagecarouselcolumns.append(
            ImageCarouselColumn(
                image_url="https://i.imgur.com/4CIrAa9.png",
                action=URITemplateAction(label="查看更多", uri=url)))
    imagecarouselcolumns.append(
            ImageCarouselColumn(
                image_url="https://i.imgur.com/PoXcTmZ.png",
                action=MessageTemplateAction(label="重新查詢", text="重新查詢")))
    imagecarouselcolumns.append(
            ImageCarouselColumn(
                image_url='https://i.imgur.com/iuDuTbt.png?1',
                action=MessageTemplateAction(label='返回主選單', text='main menu')))
    
    Carousel_template = TemplateSendMessage(
        alt_text='Image Carousel template',
        template=ImageCarouselTemplate(
        columns=imagecarouselcolumns))
    line_bot_api.reply_message(reply_token,Carousel_template)

def show_enter_menu(reply_token):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, TextSendMessage(text="可從選單中選擇服務項目了"))
    
def show_main_menu(reply_token):
    line_bot_api = LineBotApi(channel_access_token)
    Carousel_template = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/dXfoAvK.jpg',
                title='主選單',
                text='請選擇想要的服務項目',
                actions=[
                    MessageTemplateAction(
                        label='查詢家具目錄&圖片',
                        text='contents and images'
                    ),
                    MessageTemplateAction(
                        label='保養方法',
                        text="maintenance method"
                    ),
                    MessageTemplateAction(
                        label='聯絡我們',
                        text="contact us"
                    )
                ]
            )
        ]
    )
    )
    line_bot_api.reply_message(reply_token,Carousel_template)
    
def show_maintenance_method(reply_token):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token,ImageSendMessage(
        original_content_url='https://i.imgur.com/ITshKAM.png', 
        preview_image_url='https://i.imgur.com/ITshKAM.png'))
    
def show_FSM(reply_token):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token,ImageSendMessage(
        original_content_url="https://i.imgur.com/AlUAb6h.png",
        preview_image_url="https://i.imgur.com/AlUAb6h.png"))
    
def show_contact_us(reply_token):
    line_bot_api = LineBotApi(channel_access_token)
    Carousel_template = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/XjDtpGl.png',
                title='聯絡我們',
                text=' ',
                actions=[
                    MessageTemplateAction(
                        label='地址',
                        text='address'
                    ),
                    MessageTemplateAction(
                        label="聯絡電話",
                        text="contact number"
                    )
                ]
            )
        ]
    )
    )
    line_bot_api.reply_message(reply_token,Carousel_template)
    
def show_address(reply_token):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, LocationSendMessage(title="地址", address="台北市內湖區成功路四段188號14樓之11", latitude=25.08414356007363, longitude=121.59439182744914))

def show_contact_number(reply_token):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, TextSendMessage(text="聯絡電話:(02)2794-2268"))

def show_search_contents_and_images(reply_token):
    line_bot_api = LineBotApi(channel_access_token)
    Carousel_template = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
        columns=[
            CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/WSh5g9U.jpg',
                title='家具目錄&圖片',
                text='請選擇想要的家具目錄或圖片',
                actions=[ 
                    MessageTemplateAction(
                        label='目錄',
                        text='contents'
                    ),
                    MessageTemplateAction(
                        label='辦公桌',
                        text='office tables'
                    ),
                    MessageTemplateAction(
                        label='辦公椅&沙發',
                        text='office chairs and sofas'
                    )
                ]
            )
        ]
    )
    )
    line_bot_api.reply_message(reply_token,Carousel_template)
    
def show_office_chairs(reply_token):
    line_bot_api = LineBotApi(channel_access_token)
    Carousel_template = TemplateSendMessage(
        alt_text='Image Carousel template',
        template=ImageCarouselTemplate(
        columns=[
            ImageCarouselColumn(
                image_url='https://i.imgur.com/vA4AV0k.jpg',
                action=URITemplateAction(
                        label='辦公椅(SD)',
                        uri="https://drive.google.com/drive/folders/1zb0oE92j4H7nwSjnREH1qO9gctXaAO45"
                    )
            ),
            ImageCarouselColumn(
                image_url='https://i.imgur.com/hKw6Hfw.jpg',
                action=URITemplateAction(
                        label='造型椅(LG)',
                        uri='https://drive.google.com/drive/folders/1VvAbvKri-wz1mswbvyQ4eB-uv6jhdSP1'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://i.imgur.com/Calzg5r.png',
                action= URITemplateAction(
                        label='沙發',
                        uri='https://drive.google.com/drive/folders/12kw46rchbYTRjybj2BH0pGglCM8t5KnE'
                    )
            )
        ]
    )
    )
    line_bot_api.reply_message(reply_token,Carousel_template)
    
def show_office_tables(reply_token):
    line_bot_api = LineBotApi(channel_access_token)
    Carousel_template = TemplateSendMessage(
        alt_text='Image Carousel template',
        template=ImageCarouselTemplate(
        columns=[
            ImageCarouselColumn(
                image_url='https://i.imgur.com/C1qXu2a.jpg',
                action=URITemplateAction(
                        label='獨立桌(LG)',
                        uri='https://drive.google.com/drive/folders/1PohqcyoW1TPUdDfVoGP8Tu0bKorexUtp'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://i.imgur.com/emrkJns.jpg',
                action=URITemplateAction(
                        label='獨立桌(KT)',
                        uri="https://drive.google.com/drive/folders/1_ds45brlPQq5WK5cyIwZsgAe_GSFVcQQ"
                    )
            ),
            ImageCarouselColumn(
                image_url='https://i.imgur.com/pQFaPYe.jpg',
                action=URITemplateAction(
                        label='獨立桌(OS)',
                        uri='https://drive.google.com/drive/folders/1KcZU87EBVlUiShEQhuvQS0Fa-LNnyxQ4'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://i.imgur.com/Kp9l3J9.jpg',
                action=URITemplateAction(
                        label='升降桌(LG)',
                        uri="https://drive.google.com/drive/folders/1iTJy6aX9tVHDeJrVZ6mjQZJW7WgoEdZe"
                    )
            ),
            ImageCarouselColumn(
                image_url='https://i.imgur.com/5ok0DxE.jpg',
                action=URITemplateAction(
                        label='主管桌(DS)',
                        uri="https://drive.google.com/drive/folders/1Zp0vS6zQdBHcKK2ReqP6lHOZQ0hJ3jxl"
                    )
            )
        ]
    )
    )
    line_bot_api.reply_message(reply_token,Carousel_template)
    
def show_contents(reply_token):
    line_bot_api = LineBotApi(channel_access_token)
    Carousel_template = TemplateSendMessage(
        alt_text='Image Carousel template',
        template=ImageCarouselTemplate(
        columns=[
            ImageCarouselColumn(
                image_url='https://i.imgur.com/cAuLdQJ.png',
                action=URITemplateAction(
                        label='主管桌目錄',
                        uri='https://drive.google.com/drive/folders/1JKvSRxe4ynifQpUz0yLxu9bJSGAzC5xt'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://i.imgur.com/O0Fe27J.png',
                action=URITemplateAction(
                        label='家具綜合目錄',
                        uri="https://drive.google.com/drive/folders/1-0X1bsMc8DVgJxMlvSrrsX0P8NIqVrLl"
                    )
            ),
            ImageCarouselColumn(
                image_url='https://i.imgur.com/V3FdBxP.png',
                action=URITemplateAction(
                        label='獨立桌目錄',
                        uri='https://drive.google.com/drive/folders/1DFXEHQA9nILGK9TCCW2pW4bTHAAk3Me5'
                    )
            ),
            ImageCarouselColumn(
                image_url='https://i.imgur.com/W1UMAsj.png',
                action=URITemplateAction(
                        label='辦公椅目錄',
                        uri="https://drive.google.com/drive/folders/11tUf4GMAW2jtIEdQmnPT25gaiTuJtRSo"
                    )
            )
        ]
    )
    )
    line_bot_api.reply_message(reply_token,Carousel_template)