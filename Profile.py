from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivy.lang import Builder
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.app import MDApp
import os

Builder.load_file('Profile.kv')

class ProfileScreen(Screen):
    dialog = None  # Declare dialog as a class attribute for reusability

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_profile()

    def save_profile(self):
        # Get data from input fields
        name = self.ids.name_input.text
        email = self.ids.email_input.text
        cyclist_level = self.ids.Bicycle_input.text
        bicycle_model = self.ids.Type_input.text
        dob = self.ids.dob_input.text
        country = self.ids.country_input.text
        
        # Check if all fields are filled
        if all([name, email, cyclist_level, bicycle_model, dob, country]):
            try:
                # Write the data to a profile file
                with open("profile.txt", 'w') as file:
                    file.write(f"Name: {name}\nEmail: {email}\nCyclist Level: {cyclist_level}\nBicycle Model: {bicycle_model}\nDate of Birth: {dob}\nCountry/Region: {country}\n")
                
                self.show_dialog("Success", "Profile saved successfully!")
            except Exception as e:
                print(f"Error saving profile: {e}")
                self.show_dialog("Error", "Error saving profile. Please try again.")
        else:
            self.show_dialog("Warning", "Please fill in all fields.")

    def load_profile(self):
        file_path = "profile.txt"
        # Load profile data if the file exists
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    self.ids.name_input.text = lines[0].split(': ')[1].strip()
                    self.ids.email_input.text = lines[1].split(': ')[1].strip()
                    self.ids.Bicycle_input.text = lines[2].split(': ')[1].strip()
                    self.ids.Type_input.text = lines[3].split(': ')[1].strip()
                    self.ids.dob_input.text = lines[4].split(': ')[1].strip()
                    self.ids.country_input.text = lines[5].split(': ')[1].strip()
            except Exception as e:
                print(f"Error loading profile: {e}")
                self.show_dialog("Error", "Error loading profile.")
        else:
            print("Profile file does not exist.")

    def show_dialog(self, title, text):
        """Reusable method to show dialogs."""
        if not self.dialog:
            self.dialog = MDDialog(
                title=title,
                text=text,
                buttons=[MDFlatButton(text="OK", on_release=self.close_dialog)]
            )
        else:
            self.dialog.title = title
            self.dialog.text = text
        self.dialog.open()

    def close_dialog(self, *args):
        """Close the currently open dialog."""
        if self.dialog:
            self.dialog.dismiss()

    def change_picture(self):
        """This would be the code to change the profile picture."""
        self.show_dialog("Change Picture", "Picture change feature coming soon!")
    
    def go_back(self):
        self.manager.current = 'home'
