import flet as ft
from screens.register import RegisterScreen
from screens.profile_setup import ProfileSetupScreen

def main(page: ft.Page):

    # Page visual properties (MUST be here)
    page.title = "BodyOS"
    page.bgcolor = "#F4F5FF"
    page.window_width = 400
    page.window_height = 700

    # ROUTING SYSTEM
    def route_change(route):
        page.views.clear()

        if page.route == "/":
            page.views.append(RegisterScreen(page))

        elif page.route == "/profile_setup":
            page.views.append(ProfileSetupScreen(page))

        page.update()

    page.on_route_change = route_change

    # Initial route load
    page.go("/")

ft.app(target=main)
