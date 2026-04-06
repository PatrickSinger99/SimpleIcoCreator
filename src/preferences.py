import json
import os


class Preferences:

    default_structure = {"ico_save_path": None}

    def __init__(self, save_path="./saved/preferences.json"):
        self.save_path = save_path

        # Create new file if not exists
        if not os.path.exists(self.save_path):
            print("Save file does not exist. Creating new.")
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

            with open(self.save_path, "w", encoding="utf-8") as file:
                json.dump(Preferences.default_structure, file)

    def get(self, key=None):
        try:
            with open(self.save_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if key:
                return data[key]
            else:
                return data

        except Exception as e:
            print("Failed to get saved value:", e)

    def save(self, parameter, value):
        try:
            data = self.get()
            data[parameter] = value

            with open(self.save_path, "w", encoding="utf-8") as file:
                json.dump(data, file)

            print("Preferences updated.")

        except Exception as e:
            print("Failed to save preferences:", e)
