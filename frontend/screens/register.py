# register.py
import flet as ft
import requests

class RegisterScreen(ft.View):
    def __init__(self, page):
        super().__init__(route="/")
        self.page = page

        # UI Fields
        self.username = ft.TextField(label="Username", width=300)
        self.email = ft.TextField(label="Email", width=300)
        self.password = ft.TextField(label="Password", password=True, width=300, max_length=72)

        self.gender = ft.Dropdown(
            label="Gender",
            width=300,
            options=[
                ft.dropdown.Option("Male"),
                ft.dropdown.Option("Female"),
                ft.dropdown.Option("Other"),
            ],
        )

        self.dob = ft.TextField(label="Date of Birth (YYYY-MM-DD)", width=300)

        self.msg = ft.Text(color="red")

        def register_user(e):
            payload = {
                "username": self.username.value.strip(),
                "email": self.email.value.strip(),
                "password": self.password.value.strip(),
                "gender": self.gender.value,
                "dob": self.dob.value.strip(),
            }

            if not all(payload.values()):
                self.msg.value = "Please fill all fields."
                self.update()
                return

            if len(payload["dob"]) != 10 or payload["dob"].count("-") != 2:
                self.msg.value = "DOB must be YYYY-MM-DD"
                self.update()
                return

            try:
                r = requests.post(
                    "http://127.0.0.1:8000/register",
                    json=payload,
                    timeout=10,
                    verify=False
                )
            except Exception as ex:
                self.msg.value = f"Network error: {ex}"
                self.update()
                return

            try:
                data = r.json()
            except:
                self.msg.value = f"Bad response: {r.text}"
                self.update()
                return

            if r.status_code != 200:
                detail = data.get("detail") if isinstance(data, dict) else None
                self.msg.value = detail or data or "Registration failed"
                self.update()
                return

            user = data.get("user")
            if not user:
                self.msg.value = "Error: No user returned."
                self.update()
                return

            uid = user.get("id") or user.get("user_id")
            if not uid:
                self.msg.value = "Could not find user ID."
                self.update()
                return

            self.page.session.set("user_id", uid)
            self.page.go("/profile_setup")

        # Go to login
        def go_login(e):
            self.page.go("/login")

        # UI layout
        self.controls = [
            ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment="center",
                controls=[
                    ft.Text("Register", size=30, weight="bold"),
                    self.username,
                    self.email,
                    self.password,
                    self.gender,
                    self.dob,
                    ft.ElevatedButton("Create Account", on_click=register_user),
                    ft.TextButton("Already have an account? Login", on_click=go_login),
                    self.msg,
                ],
            )
        ]
