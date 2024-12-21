from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from datetime import datetime
import pytz
from OnlineNav import OnlineNavScreen  # Import the OnlineNavScreen
from Courses import CoursesScreen # Import the CoursesScreen
from Profile import ProfileScreen #Import the ProfileScreen 
from Data import DataScreen #Import the DataScreen
from compass import CompassScreen #import the ComassScreen 
from Train import TrainScreen #import the TrainScreen
from testmap import TestMapScreen #Import the TestMapScreen

# Load the kv file
Builder.load_file('Myapp.kv')

class CircularIconButton(MDIconButton):
    def __init__(self, **kwargs):
        self.bg_color = kwargs.pop('md_bg_color', (1, 1, 1, 1))
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[50])
            self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class HomeScreen(Screen):

    def go_to_user_profile(self):
        # Implement navigation to the user profile screen
        print("Navigating to User Profile")
        self.manager.current = 'user_profile'  # Ensure 'user_profile' screen is defined

    def open_settings(self):
        # Implement opening of settings
        print("Opening Settings")
        self.manager.current = 'settings'  # Ensure 'settings' screen is defined

    def handle_bluetooth(self):
        # Implement Bluetooth handling functionality
        print("Handling Bluetooth")
        # Add your Bluetooth-related code here
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)

        # Bind the navigation buttons to switch screens
        self.ids.profile_button.bind(on_release=self.switch_to_screen('profile'))
        self.ids.map_button.bind(on_release=self.switch_to_screen('courses'))
        self.ids.settings_button.bind(on_release=self.switch_to_screen('data'))
        self.ids.navigation_button.bind(on_release=self.switch_to_screen('testmap'))
        self.ids.train_button.bind(on_release=self.switch_to_screen('Train'))
        self.ids.training_button.bind(on_release=self.switch_to_screen('compass'))

        # Schedule the time update
        Clock.schedule_interval(self.update_time, 60)  # Update time every minute
        self.update_time(0)  # Initial time update

    def switch_to_screen(self, screen_name):
        def switch(*args):
            self.manager.current = screen_name
        return switch

    def update_time(self, dt):
        try:
            pacific_time = datetime.now(pytz.timezone('US/Pacific')).strftime("%I:%M %p")
            self.ids.current_time.text = pacific_time
        except AttributeError:
            print("Error: Unable to access 'current_time' label. IDs not yet available.")

class BackScreen(Screen):
    def __init__(self, screen_name, **kwargs):
        super().__init__(**kwargs)
        self.name = screen_name
        layout = MDBoxLayout(orientation='vertical')
        self.add_widget(layout)
        
        # Toolbar with Back Button
        toolbar = MDTopAppBar(title=screen_name.capitalize(), left_action_items=[["arrow-left", lambda x: self.go_back()]])
        layout.add_widget(toolbar)

        # Screen Content
        layout.add_widget(MDLabel(text=f'{screen_name.capitalize()} Screen', halign='center'))

    def go_back(self, *args):
        self.manager.current = 'home'

class MyApp(MDApp):
    
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(CoursesScreen(name='courses'))
        sm.add_widget(DataScreen(name='data'))
        sm.add_widget(BackScreen(screen_name='navigation'))
        sm.add_widget(CompassScreen(name='compass'))     #Add the CompassScreen
        sm.add_widget(TestMapScreen(name='testmap'))  # Add the TestMapScreen
        sm.add_widget(TrainScreen(name='Train'))  # Adds the TrainScreen
        return sm

    def go_back(self):
        self.root.current = 'home'
    

if __name__ == '__main__':
    MyApp().run()
