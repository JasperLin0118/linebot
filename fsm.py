from transitions.extensions import GraphMachine

from utils import *


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        
    def is_going_to_search(self, event):
        text = event.message.text
        return text.lower() == "search"
    
    def on_enter_search(self, event):
        print("I'm entering search")
        reply_token = event.reply_token
        show_search(reply_token)
        
    def is_going_to_backto_search(self, event):
        text = event.message.text
        return text == "重新查詢" or text == "輸入錯誤，請重新輸入"
        
    def on_enter_start_search(self, event):
        print("I'm going to start search")
        reply_token = event.reply_token
        show_start_search(reply_token, event.message.text)

    def is_going_to_search_style_or_category(self, event):
        text = event.message.text
        return text.lower() == "search style or category"
    
    def on_enter_search_style_or_category(self, event):
        print("I'm entering search_style_or_category")
        reply_token = event.reply_token
        show_search_style_or_category(reply_token)
        
    def is_going_to_category(self, event):
        text = event.message.text
        return text.lower() == "category"
    
    def on_enter_category(self, event):
        print("I'm entering category")
        reply_token = event.reply_token
        show_category(reply_token)
        self.advance(event)

    def is_going_to_main_menu(self, event):
        text = event.message.text
        reply_token = event.reply_token
        if(text == "address"):
            show_address(reply_token)
        elif(text == "contact number"):
            show_contact_number(reply_token)
        elif(text == "show FSM"):
            show_FSM(reply_token)
            if(self.state != "main_menu"):
                return True
            return False
        elif(text == "maintenance method"):
            show_maintenance_method(reply_token)
            if(self.state != "main_menu"):
                return True
            return False
        elif(text == "office tables"):
            show_office_tables(reply_token)
            return False
        elif(text == "office chairs and sofas"):
            show_office_chairs(reply_token)
            return False
        elif(text == "contents"):
            show_contents(reply_token)
            return False
        elif(text == "search style or category"):
            show_search_style_or_category(reply_token)
        elif(text == "contents and images"):
            show_search_contents_and_images(reply_token)
        elif(text == "contact us"):
            show_contact_us(reply_token)
        elif(text == "main menu"):
            show_enter_menu(reply_token)
        return True
    
    def on_enter_main_menu(self, event):
        print("I'm entering menu")

    def is_going_to_contact_us(self, event):
        text = event.message.text
        return text.lower() == "contact us"
    
    def on_enter_contact_us(self, event):
        print("I'm entering contact_us")
        reply_token = event.reply_token
        show_contact_us(reply_token)

    def is_going_to_contents_and_images(self, event):
        text = event.message.text
        return text.lower() == "contents and images"
    
    def on_enter_contents_and_images(self, event):
        print("I'm entering contents_and_images")
        reply_token = event.reply_token
        show_search_contents_and_images(reply_token)

    def on_exit_menu(self):
        print("Leaving menu")
