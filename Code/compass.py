# compass.py
import math
import smbus2
import time
import logging
from geopy.distance import geodesic
from kivy.uix.screenmanager import Screen
from kivy.properties import (
    NumericProperty,
    ListProperty,
    StringProperty,
    BooleanProperty,
)
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.animation import Animation

# Load the KV file
Builder.load_file('compass.kv')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("compass.log"),
        logging.StreamHandler()
    ]
)

# Initialize the I2C bus for QMC5883L sensor
BUS_NUMBER = 22  # Change if your hardware uses a different bus
bus = smbus2.SMBus(BUS_NUMBER)
QMC5883L_ADDRESS = 0x0D
QMC5883L_CONTROL_1 = 0x09
QMC5883L_SET_RESET = 0x0B
QMC5883L_X_LSB = 0x00

class CompassScreen(Screen):
    # Define Kivy Properties
    estimated_arrival_time = StringProperty("--:--")
    needle_angle = NumericProperty(0)
    route_coords = ListProperty([])  # List of waypoints (longitude, latitude)
    current_waypoint_index = NumericProperty(0)
    steps = ListProperty([])
    next_turn_instruction = StringProperty("")
    is_navigation_mode = BooleanProperty(True)  # Start in Waypoint Mode
    speed = NumericProperty(0)
    total_distance = NumericProperty(0)
    elevation = NumericProperty(0)
    material = StringProperty("Asphalt")

    # **Added Property for Waypoint Distance**
    waypoint_distance = StringProperty("0 m")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bearing_history = []
        self.history_length = 5  # Number of samples for averaging

    def on_enter(self):
        """Called when the screen is entered."""
        logging.info("CompassScreen entered.")
        self.init_qmc5883l()
        self.start_compass_updates()
        if self.is_navigation_mode:
            if self.route_coords and self.steps:
                self.current_waypoint_index = 0
                logging.info("Route data received. Ready for navigation.")
            else:
                logging.warning("No route data available.")
        else:
            # If entering Compass Mode directly, ensure compass updates are active
            self.start_compass_updates()

    def on_leave(self):
        """Called when the screen is left."""
        self.stop_compass_updates()
        logging.info("CompassScreen left.")

    def switch_mode(self):
        """
        Toggle between Waypoint Mode and Compass Mode.
        Animates the needle and updates the interface after animation completes.
        """
        self.is_navigation_mode = not self.is_navigation_mode

        if self.is_navigation_mode:
            logging.info("Switching to Waypoint Mode")
            # Animate needle_angle to 360 degrees over 1 second
            anim = Animation(needle_angle=360, duration=1)
            # Bind the completion of animation to the callback
            anim.bind(on_complete=self._on_switch_to_waypoint_complete)
            anim.start(self)
        else:
            logging.info("Switching to Compass Mode")
            # Animate needle_angle to 0 degrees over 1 second
            anim = Animation(needle_angle=0, duration=1)
            # Bind the completion of animation to the callback
            anim.bind(on_complete=self._on_switch_to_compass_complete)
            anim.start(self)

    def _on_switch_to_waypoint_complete(self, animation, widget):
        """Callback executed after switching to Waypoint Mode animation completes."""
        try:
            # Change interface color to Waypoint Mode color
            self.change_interface_color("#1E90FF")  # DodgerBlue
            # Update the mode switch button icon to "flag"
            self.ids.mode_button.icon = "flag"
            # Stop compass updates since they're not needed in Waypoint Mode
            self.stop_compass_updates()
            # Update the waypoint_label with initial bearing
            self.update_waypoint_label()
            logging.info("Switched to Waypoint Mode successfully.")
        except Exception as e:
            logging.error(f"Error in _on_switch_to_waypoint_complete: {e}")

    def _on_switch_to_compass_complete(self, animation, widget):
        """Callback executed after switching to Compass Mode animation completes."""
        try:
            # Change interface color to Compass Mode color
            self.change_interface_color("#32CD32")  # LimeGreen
            # Update the mode switch button icon to "compass"
            self.ids.mode_button.icon = "compass"
            # Start compass updates to read sensor data
            self.start_compass_updates()
            # Initialize the compass sensor if necessary
            self.init_qmc5883l()
            # Update the compass_label with initial heading
            self.update_compass_label()
            logging.info("Switched to Compass Mode successfully.")
        except Exception as e:
            logging.error(f"Error in _on_switch_to_compass_complete: {e}")

    def change_interface_color(self, color_hex):
        """
        Change the background color of the interface.
        Args:
            color_hex (str): The color in HEX format.
        """
        try:
            color = get_color_from_hex(color_hex)
            # Update the background_color's rgb
            self.ids.background_color.rgb = color[:3]
            logging.debug(f"Interface color changing to {color_hex}")
        except Exception as e:
            logging.error(f"Error in change_interface_color: {e}")

    def init_qmc5883l(self):
        """Initialize the QMC5883L compass sensor."""
        try:
            control_1 = 0b11010101  # OSR=512, RNG=8G, ODR=50Hz, Mode=Continuous
            bus.write_byte_data(QMC5883L_ADDRESS, QMC5883L_CONTROL_1, control_1)
            bus.write_byte_data(QMC5883L_ADDRESS, QMC5883L_SET_RESET, 0x01)
            time.sleep(0.1)  # Wait for sensor to initialize
            logging.info("QMC5883L sensor initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize QMC5883L sensor: {e}")

    def read_raw_data(self):
        """Read raw magnetometer data from QMC5883L sensor."""
        try:
            data = bus.read_i2c_block_data(QMC5883L_ADDRESS, QMC5883L_X_LSB, 6)
            logging.debug(f"Raw sensor data: {data}")
            x = data[1] << 8 | data[0]
            y = data[3] << 8 | data[2]
            z = data[5] << 8 | data[4]
            x = self.twos_complement(x, 16)
            y = self.twos_complement(y, 16)
            z = self.twos_complement(z, 16)
            return x, y, z
        except Exception as e:
            logging.error(f"Error reading data from sensor: {e}")
            return 0, 0, 0  # Return zeros if reading fails

    def twos_complement(self, val, bits):
        """Compute two's complement of a value."""
        if val & (1 << (bits - 1)):
            val -= 1 << bits
        return val

    def start_compass_updates(self):
        """Start updating the compass needle at a specified interval."""
        try:
            # Update every 0.1 seconds for better responsiveness
            self.update_event = Clock.schedule_interval(self.update_compass, 0.1)
            logging.info("Compass updates started.")
        except Exception as e:
            logging.error(f"Error starting compass updates: {e}")

    def stop_compass_updates(self):
        """Stop updating the compass needle."""
        try:
            if hasattr(self, 'update_event') and self.update_event:
                self.update_event.cancel()
                logging.info("Compass updates stopped.")
        except Exception as e:
            logging.error(f"Error stopping compass updates: {e}")

    def update_compass(self, dt):
        """Update the compass needle based on the current mode."""
        try:
            if self.is_navigation_mode:
                # Waypoint Mode
                current_location = self.get_current_location()
                if current_location is None:
                    logging.warning("No current GPS location available.")
                    self.ids.bearing_label.text = "No GPS Fix"
                    self.ids.distance_label.text = ""
                    self.ids.waypoint_distance_label.text = "0 m"
                    self.ids.next_turn_label.text = ""
                    return
                self.update_navigation_mode(current_location[0], current_location[1])
            else:
                # Compass Mode
                x, y, z = self.read_raw_data()
                heading = self.get_heading(x, y)
                self.needle_angle = heading
                logging.debug(f"Compass heading: {heading} degrees")
                # Update the compass_label
                self.update_compass_label()
        except Exception as e:
            logging.error(f"Error in update_compass: {e}")

    def get_heading(self, x, y):
        """Calculate the heading based on x and y magnetometer values."""
        try:
            heading_rad = math.atan2(y, x)
            heading_deg = math.degrees(heading_rad)
            if heading_deg < 0:
                heading_deg += 360

            # Append to history for smoothing
            self.bearing_history.append(heading_deg)
            if len(self.bearing_history) > self.history_length:
                self.bearing_history.pop(0)

            # Calculate average
            average_heading = sum(self.bearing_history) / len(self.bearing_history)
            return average_heading
        except Exception as e:
            logging.error(f"Error calculating heading: {e}")
            return 0

    def update_navigation_mode(self, current_lat, current_lon):
        """
        Update the compass needle to point towards the next waypoint.
        Args:
            current_lat (float): Current latitude.
            current_lon (float): Current longitude.
        """
        try:
            if self.current_waypoint_index < len(self.route_coords):
                waypoint = self.route_coords[self.current_waypoint_index]
                dest_lon, dest_lat = waypoint

                bearing = self.calculate_initial_compass_bearing(
                    (current_lat, current_lon), (dest_lat, dest_lon)
                )
                self.needle_angle = bearing
                logging.debug(f"Waypoint bearing: {bearing} degrees")

                distance_to_waypoint = geodesic(
                    (current_lat, current_lon), (dest_lat, dest_lon)
                ).meters
                logging.debug(f"Distance to waypoint: {distance_to_waypoint} meters")

                # **Update the waypoint_distance property**
                self.update_waypoint_distance(distance_to_waypoint)

                # Update next turn instruction
                if self.current_waypoint_index < len(self.steps):
                    current_step = self.steps[self.current_waypoint_index]
                    instruction = current_step.get('instruction', '')
                    self.next_turn_instruction = instruction
                    self.ids.next_turn_label.text = instruction
                    logging.debug(f"Next turn instruction: {instruction}")
                else:
                    self.next_turn_instruction = ""
                    self.ids.next_turn_label.text = ""

                if distance_to_waypoint < 10:
                    self.current_waypoint_index += 1
                    logging.info(f"Reached waypoint {self.current_waypoint_index}. Moving to next waypoint.")
                    self.provide_waypoint_feedback()
                    if self.current_waypoint_index >= len(self.route_coords):
                        logging.info("All waypoints reached. Destination arrived.")
                        self.ids.bearing_label.text = "Arrived at Destination"
                        self.ids.distance_label.text = ""
                        self.ids.waypoint_distance_label.text = "0 m"
                        self.ids.next_turn_label.text = ""
                        self.stop_compass_updates()

                # Update the waypoint_label with current bearing
                self.update_waypoint_label(bearing)
            else:
                self.stop_compass_updates()
                self.waypoint_distance = "0 m"  # Update via property
                logging.info("Destination reached.")
        except Exception as e:
            logging.error(f"Error in update_navigation_mode: {e}")

    def calculate_initial_compass_bearing(self, pointA, pointB):
        """
        Calculates the bearing between two points.
        Args:
            pointA (tuple): (latitude, longitude) of the first point.
            pointB (tuple): (latitude, longitude) of the second point.
        Returns:
            float: Bearing in degrees.
        """
        try:
            lat1 = math.radians(pointA[0])
            lat2 = math.radians(pointB[0])
            diffLong = math.radians(pointB[1] - pointA[1])

            x = math.sin(diffLong) * math.cos(lat2)
            y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))

            initial_bearing = math.atan2(x, y)
            compass_bearing = (math.degrees(initial_bearing) + 360) % 360

            # Handle the case where both points are the same
            if math.isclose(pointA[0], pointB[0], abs_tol=1e-6) and math.isclose(pointA[1], pointB[1], abs_tol=1e-6):
                return 0  # Arbitrary value since bearing is undefined

            return compass_bearing
        except Exception as e:
            logging.error(f"Error calculating compass bearing: {e}")
            return 0

    def get_current_location(self):
        """
        Retrieve the current location from TestMapScreen.
        Returns:
            tuple or None: (latitude, longitude) if available, else None.
        """
        try:
            testmap_screen = self.manager.get_screen('testmap')
            lat, lon = testmap_screen.get_current_gps_coordinates()
            if lat is not None and lon is not None:
                return (lat, lon)
            else:
                return None
        except Exception as e:
            logging.error(f"Error getting current location: {e}")
            return None

    def update_waypoint_label(self, bearing=None):
        """Update the waypoint_label with the current bearing."""
        try:
            if bearing is not None:
                self.ids.waypoint_label.text = f"{int(bearing)}°"
            else:
                self.ids.waypoint_label.text = "0°"
            logging.debug(f"Updated waypoint_label: {self.ids.waypoint_label.text}")
        except Exception as e:
            logging.error(f"Error updating waypoint_label: {e}")

    def update_compass_label(self):
        """Update the compass_label with the current heading."""
        try:
            heading = self.get_current_heading()
            self.ids.compass_label.text = f"{int(heading)}°"
            logging.debug(f"Updated compass_label: {self.ids.compass_label.text}")
        except Exception as e:
            logging.error(f"Error updating compass_label: {e}")

    def get_current_heading(self):
        """Retrieve the current compass heading."""
        try:
            x, y, z = self.read_raw_data()
            heading = self.get_heading(x, y)
            return heading
        except Exception as e:
            logging.error(f"Error getting current heading: {e}")
            return 0

    def go_back(self):
        """Navigate back to the home screen."""
        try:
            self.manager.current = 'home'
            logging.info("Navigated back to home screen.")
        except Exception as e:
            logging.error(f"Error navigating back: {e}")

    def update_bottom_widgets(self):
        """Update the bottom widgets with current data."""
        try:
            self.ids.speed_label.text = f"{self.speed:.1f} km/h"
            self.ids.total_distance_label.text = f"{self.total_distance:.2f} km"
            self.ids.elevation_label.text = f"{self.elevation:.0f} m"
            self.ids.material_label.text = self.material
            logging.debug("Updated bottom widgets with current data.")
        except Exception as e:
            logging.error(f"Error updating bottom widgets: {e}")

    # **Added Method to Update Waypoint Distance**
    def update_waypoint_distance(self, distance):
        """Update the waypoint_distance property with the current distance."""
        try:
            if distance >= 1000:
                # Display in kilometers with two decimal places
                self.waypoint_distance = f"{distance / 1000:.2f} km"
            else:
                # Display in meters as an integer
                self.waypoint_distance = f"{int(distance)} m"
            logging.debug(f"Updated waypoint_distance: {self.waypoint_distance}")
        except Exception as e:
            logging.error(f"Error updating waypoint_distance: {e}")

    def provide_waypoint_feedback(self):
        """Provide visual feedback upon reaching a waypoint."""
        try:
            # Flash the compass needle
            anim = Animation(needle_angle=0, duration=0.2) + Animation(needle_angle=self.calculate_initial_compass_bearing(
                self.get_current_location(),
                self.route_coords[self.current_waypoint_index] if self.current_waypoint_index < len(self.route_coords) else (0, 0)
            ), duration=0.2)
            anim.start(self)

            # Flash the background color
            original_color = self.ids.background_color.rgb
            flash_color = get_color_from_hex("#FFD700")  # Gold color
            anim_bg = Animation(rgb=flash_color[:3], duration=0.2) + Animation(rgb=original_color, duration=0.2)
            anim_bg.start(self.ids.background_color)

            logging.info("Provided waypoint reach feedback.")
        except Exception as e:
            logging.error(f"Error providing waypoint feedback: {e}")

