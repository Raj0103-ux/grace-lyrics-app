import flet as ft
from src.ui.theme import get_theme
from src.ui.screens import get_home_view, get_song_view, get_admin_view
from src.models import db

def main(page: ft.Page):
    page.title = "Grace Lyrics"
    page.theme = get_theme()
    page.theme_mode = ft.ThemeMode.DARK

    try:
        db.init_db()
    except Exception as e:
        page.add(ft.Text(f"DB ERROR: {e}", color=ft.Colors.RED, selectable=True))
        return

    def route_change(route):
        try:
            page.views.clear()
            page.views.append(get_home_view(page))
            if page.route == "/admin":
                page.views.append(get_admin_view(page))
            elif page.route.startswith("/song/"):
                page.views.append(get_song_view(page, page.route.split("/")[2]))
            page.update()
        except Exception as e:
            page.views.clear()
            page.views.append(ft.View("/error", [ft.Text(f"ERROR: {e}", color=ft.Colors.RED, selectable=True)]))
            page.update()

    def view_pop(view):
        page.views.pop()
        page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main)
