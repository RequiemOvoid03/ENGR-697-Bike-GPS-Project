from kivy.uix.screenmanager import Screen
from kivy_garden.graph import Graph, MeshLinePlot
from kivy_garden.graph import LinePlot
from kivymd.uix.label import MDLabel  # Import MDLabel from KivyMD
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.lang import Builder
from kivymd.uix.label import MDLabel 
import matplotlib.pyplot as plt
import numpy as np

# Load the kv file for DataScreen
Builder.load_file('data.kv')

class DataScreen(Screen):
    def on_enter(self):
        # Create charts
        self.create_distance_traveled_chart()
        self.create_average_speed_chart()
        self.create_last_ride_duration_chart()
        self.create_elevation_chart()
        self.create_calories_burned_chart()
        self.create_road_material_chart()

    def create_distance_traveled_chart(self):
        data = np.random.rand(100)
        graph = Graph(
            xlabel='Time',
            ylabel='Distance (km)',
            border_color = [0,1,1,1],
            x_ticks_minor=5,
            x_ticks_major=25,
            y_ticks_major=0.2,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            xmin=0,
            xmax=100,
            ymin=0,
            ymax=1
        )
        plot = LinePlot(color=[0, 0, 1, 1], line_width = 2.0)  # Blue color
        plot.points = [(x, y) for x, y in enumerate(data)]
        graph.add_plot(plot)
        self.ids.distance_traveled_chart.clear_widgets()
        self.ids.distance_traveled_chart.add_widget(graph)

    def create_average_speed_chart(self):
        data = np.random.rand(100)
        graph = Graph(
            xlabel='Time',
            ylabel='Speed (km/h)',
            border_color = [0,1,1,1],
            x_ticks_minor=5,
            x_ticks_major=25,
            y_ticks_major=0.2,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            xmin=0,
            xmax=100,
            ymin=0,
            ymax=1
        )
        plot = LinePlot(color=[0, 1, 0, 1], line_width = 2.0)  # Green color
        plot.points = [(x, y) for x, y in enumerate(data)]
        graph.add_plot(plot)
        self.ids.average_speed_chart.clear_widgets()
        self.ids.average_speed_chart.add_widget(graph)

    def create_last_ride_duration_chart(self):
        data = np.random.rand(100)
        graph = Graph(
            xlabel='Time',
            ylabel='Duration (min)',
            border_color = [0,1,1,1],
            x_ticks_minor=5,
            x_ticks_major=25,
            y_ticks_major=0.2,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            xmin=0,
            xmax=100,
            ymin=0,
            ymax=1
        )
        plot = LinePlot(color=[1, 0.5, 0, 1], line_width = 2.0)  # Orange color
        plot.points = [(x, y) for x, y in enumerate(data)]
        graph.add_plot(plot)
        self.ids.last_ride_duration_chart.clear_widgets()
        self.ids.last_ride_duration_chart.add_widget(graph)

    def create_elevation_chart(self):
        data = np.random.rand(100)
        graph = Graph(
            xlabel='Time',
            ylabel='Elevation (m)',
            border_color = [0,1,1,1],
            x_ticks_minor=5,
            x_ticks_major=25,
            y_ticks_major=0.2,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            xmin=0,
            xmax=100,
            ymin=0,
            ymax=1
        )
        plot = LinePlot(color=[0.58, 0.0, 0.83, 1], line_width = 2.0)  # Purple color
        plot.points = [(x, y) for x, y in enumerate(data)]
        graph.add_plot(plot)
        self.ids.elevation_chart.clear_widgets()
        self.ids.elevation_chart.add_widget(graph)

    def create_calories_burned_chart(self):
        data = np.random.rand(100)
        graph = Graph(
            xlabel='Time',
            ylabel='Calories',
            border_color = [0,1,1,1],
            x_ticks_minor=5,
            x_ticks_major=25,
            y_ticks_major=0.2,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            xmin=0,
            xmax=100,
            ymin=0,
            ymax=1
        )
        plot = LinePlot(color=[1, 0, 0, 1], line_width = 2.0)  # Red color
        plot.points = [(x, y) for x, y in enumerate(data)]
        graph.add_plot(plot)
        self.ids.calories_burned_chart.clear_widgets()
        self.ids.calories_burned_chart.add_widget(graph)

    def create_road_material_chart(self):
        # Pie chart using Matplotlib
        labels = ['Asphalt', 'Gravel', 'Dirt', 'Sand']
        data = np.random.rand(4)
        fig, ax = plt.subplots()
        ax.pie(data, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
        ax.set_title('Road Material Distribution')

        self.ids.road_material_chart.clear_widgets()
        self.ids.road_material_chart.add_widget(FigureCanvasKivyAgg(fig))

        
    def go_back(self):
        self.manager.current = 'home'
