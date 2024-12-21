from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ListProperty
from kivy.lang import Builder

# Load the KivyMD file
Builder.load_file('courses.kv')

class CoursesScreen(Screen):
    leaderboard_data = ListProperty()

    def __init__(self, **kwargs):
        super(CoursesScreen, self).__init__(**kwargs)
        # Sample data for the leaderboard
        self.leaderboard_data = [
            {'rank': 1, 'name': 'Peloton Patty', 'gender': 'F', 'age': 20, 'location': 'Utah', 'score': 351, 'image': 'Tylerthecreator.png'},
            {'rank': 2, 'name': 'Peter Pelo', 'gender': 'M', 'age': 30, 'location': 'Utah', 'score': 337, 'image': 'Tylerthecreator.png'},
            {'rank': 3, 'name': 'Pam Pedal', 'gender': 'F', 'age': 30, 'location': 'Utah', 'score': 325, 'image': 'Tylerthecreator.png'},
            {'rank': 4, 'name': 'Biker Brody', 'gender': 'M', 'age': 30, 'location': 'Utah', 'score': 311, 'image': 'Tylerthecreator.png'},
            {'rank': 5, 'name': 'Echelon Lover', 'gender': 'M', 'age': 40, 'location': 'Utah', 'score': 302, 'image': 'Tylerthecreator.png'},
            # Add more riders as needed
        ]

    def on_kv_post(self, base_widget):
        # Populates the leaderboard after the KV file has been loaded
        self.populate_leaderboard()

    def populate_leaderboard(self):
        # Populate the leaderboard list with data from leaderboard_data
        for rider in self.leaderboard_data:
            self.ids.leaderboard_list.add_widget(
                LeaderboardRow(
                    rank=rider['rank'],
                    name=rider['name'],
                    gender=rider['gender'],
                    age=rider['age'],
                    location=rider['location'],
                    score=rider['score'],
                    image=rider['image']
                )
            )

class BikeGPSApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "LightGreen"
        self.theme_cls.theme_style = "Dark"  # Use 'Light' for light theme
        sm = ScreenManager()
        sm.add_widget(CoursesScreen(name='courses'))
        return sm

if __name__ == '__main__':
    BikeGPSApp().run()

