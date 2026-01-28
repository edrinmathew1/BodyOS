import flet as ft
import requests

class ProfileSetupScreen(ft.View):
    def __init__(self, page):
        super().__init__(route="/profile_setup")
        self.page = page

        # Fields
        self.height_field = ft.TextField(label="Height (cm)", width=300)
        self.weight_field = ft.TextField(label="Weight (kg)", width=300)
        self.bmi_field = ft.TextField(label="BMI", width=300, read_only=True)

        self.activity_level = ft.Dropdown(
            label="Activity Level",
        
            width=300,
            options=[
                ft.dropdown.Option("Low"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("High"),
            ],
        )

        self.goal = ft.Dropdown(
            label="Goal",
            width=300,
            options=[
                ft.dropdown.Option("Maintain"),
                ft.dropdown.Option("Muscle Gain"),
                ft.dropdown.Option("Weight Loss"),
            ],
        )

        self.msg = ft.Text(color="green")

        # BMI calculator
        def calculate_bmi(e):
            try:
                h = float(self.height_field.value) / 100
                w = float(self.weight_field.value)
                bmi = w / (h * h)
                self.bmi_field.value = f"{bmi:.2f}"
            except:
                self.bmi_field.value = ""
            self.update()

        self.height_field.on_change = calculate_bmi
        self.weight_field.on_change = calculate_bmi

        # Save profile
        def save_profile(e):
            user_id = self.page.session.get("user_id")

            payload = {
                "user_id": user_id,
                "height_cm": float(self.height_field.value),
                "weight_kg": float(self.weight_field.value),
                "bmi": float(self.bmi_field.value),
                "activity_level": self.activity_level.value,
                "goal": self.goal.value,
            }

            if not all(payload.values()):
                self.msg.value = "Please fill all fields."
                self.update()
                return

            try:
                r = requests.post("http://127.0.0.1:8000/profile", json=payload)
            except Exception as ex:
                self.msg.value = f"Network error: {ex}"
                self.update()
                return

            if r.status_code != 200:
                self.msg.value = r.text
                self.update()
                return

            self.msg.value = "Profile saved!"
            self.update()

        # UI controls
        self.controls = [
            ft.Column(
                horizontal_alignment="center",
                scroll="auto",
                controls=[
                    ft.Text("Profile Setup", size=25, weight="bold"),
                    self.height_field,
                    self.weight_field,
                    self.bmi_field,
                    self.activity_level,
                    self.goal,
                    ft.ElevatedButton("Save Profile", on_click=save_profile),
                    self.msg,
                ],
            )
        ]
