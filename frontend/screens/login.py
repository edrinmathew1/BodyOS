# login.py
import flet as ft
import requests

class LoginScreen(ft.View):
    def __init__(self, page):
        super().__init__(route="/login")
        self.page = page

        self.email = ft.TextField(label="Email", width=300)
        self.password = ft.TextField(label="Password", password=True, width=300)
        self.msg = ft.Text(color="red")

        def login_user(e):
            payload = {
                "email": self.email.value.strip(),
                "password": self.password.value.strip()
            }

            if not all(payload.values()):
                self.msg.value = "Please enter email & password."
                self.update()
                return

            try:
                r = requests.post(
                    "http://127.0.0.1:8000/login",
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
                self.msg.value = detail or "Login failed"
                self.update()
                return

            user = data.get("user")
            if not user:
                self.msg.value = "Invalid login response."
                self.update()
                return

            uid = user.get("id") or user.get("user_id")
            self.page.session.set("user_id", uid)

            self.page.go("/profile_setup")  # or home dashboard later

        # go to register
        def go_register(e):
            self.page.go("/")

        self.controls = [
            ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment="center",
                controls=[
                    ft.Text("Login", size=30, weight="bold"),
                    self.email,
                    self.password,
                    ft.ElevatedButton("Login", on_click=login_user),
                    ft.TextButton("Create new account", on_click=go_register),
                    self.msg,
                ],
            )
        ]
