from transitions.extensions import GraphMachine

from utils import *


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        
    def is_going_to_FSM(self, event):
        text = event.message.text
        return text == "show FSM"
    
    def on_enter_FSM(self, event):
        print("I'm entering FSM")
        reply_token = event.reply_token
        show_FSM(reply_token)
        self.advance(event)
        
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
        return True
    
    def on_enter_main_menu(self, event):
        print("I'm entering menu")

    def is_going_to_maintenance_method(self, event):
        text = event.message.text
        return text.lower() == "maintenance method"
    
    def on_enter_maintenance_method(self, event):
        print("I'm entering maintenance_method")
        reply_token = event.reply_token
        show_maintenance_method(reply_token)
        self.advance(event)

    def is_going_to_contact_us(self, event):
        text = event.message.text
        return text.lower() == "contact us"

    def on_enter_contact_us(self, event):
        print("I'm entering contact_us")
        reply_token = event.reply_token
        show_contact_us(reply_token)
        
    def is_going_to_address(self, event):
        text = event.message.text
        return text.lower() == "address"
    
    def on_enter_address(self, event):
        print("I'm entering address")
        reply_token = event.reply_token
        show_address(reply_token)
        self.advance(event)
    
    def is_going_to_contact_number(self, event):
        text = event.message.text
        return text.lower() == "contact number"
    
    def on_enter_contact_number(self, event):
        print("I'm entering contact_number")
        reply_token = event.reply_token
        show_contact_number(reply_token)
        self.advance(event)

    def is_going_to_contents_and_images(self, event):
        text = event.message.text
        return text.lower() == "contents and images"
    
    def on_enter_contents_and_images(self, event):
        print("I'm entering contents_and_images")
        reply_token = event.reply_token
        show_search_contents_and_images(reply_token)
    
    def is_going_to_idle(self, event):
        text = event.message.text
        return text.lower() == "leave main menu"
    
    def is_going_to_contents(self, event):
        text = event.message.text
        return text.lower() == "contents"
    
    def on_enter_contents(self, event):
        print("I'm entering contents")
        reply_token = event.reply_token
        show_contents(reply_token)
        self.advance(event)
    
    def is_going_to_office_chairs_and_sofas(self, event):
        text = event.message.text
        return text.lower() == "office chairs and sofas"
    
    def on_enter_office_chairs_and_sofas(self, event):
        print("I'm entering office_chairs")
        reply_token = event.reply_token
        show_office_chairs(reply_token)
        self.advance(event)
        
    def is_going_to_office_tables(self, event):
        text = event.message.text
        return text.lower() == "office tables"
    
    def on_enter_office_tables(self, event):
        print("I'm entering office_tables")
        reply_token = event.reply_token
        show_office_tables(reply_token)
        self.advance(event)

    def on_exit_menu(self):
        print("Leaving menu")
