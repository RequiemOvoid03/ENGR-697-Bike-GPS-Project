from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivymd.app import MDApp
import time

Builder.load_file('Train.kv')
class TrainScreen(Screen):
    # Define properties for each metric to enable dynamic updates
    heart_rate = StringProperty('-- bpm')
    cadence = StringProperty('-- rpm')
    elapsed_time = StringProperty('0:00')
    distance = StringProperty('0.0 mi')
    speed = StringProperty('0.0 mph')
    avg_power = StringProperty('-- W')
    avg_heart_rate = StringProperty('-- bpm')
    battery_level = StringProperty('100%')
    current_time = StringProperty(time.strftime("%H:%M"))

    def __init__(self, **kwargs):
        super(TrainScreen, self).__init__(**kwargs)
        # Schedule the update_metrics method to be called every second
        Clock.schedule_interval(self.update_metrics, 1)
        self.start_time = time.time()

    def update_metrics(self, dt):
        # Update current time
        self.current_time = time.strftime("%H:%M")
        
        # Calculate elapsed time
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        self.elapsed_time = f"{minutes}:{seconds:02}"
        
        # Update metrics with dummy data
        # Replace these with actual sensor data as needed
        self.heart_rate = f"{70 + (elapsed % 30)} bpm"      # Example: fluctuating heart rate
        self.cadence = f"{80 + (elapsed % 20)} rpm"         # Example: fluctuating cadence
        self.distance = f"{(elapsed * 0.01):.2f} mi"        # Example: distance increases over time
        self.speed = f"{(elapsed % 15):.1f} mph"            # Example: fluctuating speed
        self.avg_power = f"{(50 + (elapsed % 100))} W"      # Example: fluctuating average power
        self.avg_heart_rate = f"{(60 + (elapsed % 40))} bpm" # Example: fluctuating average heart rate
        self.battery_level = f"{100 - (elapsed % 100)}%"    # Example: battery level decreasing

class MyApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TrainScreen(name='train'))
        return sm

    def go_back(self):
        self.root.current = 'train'

if __name__ == '__main__':
    MyApp().run()