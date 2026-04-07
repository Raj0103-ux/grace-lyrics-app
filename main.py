import flet as ft
from src.ui.theme import get_theme
from src.ui.screens import get_home_view, get_song_view, get_admin_view
import src.models.db as db

def main(page: ft.Page):
    page.title = "Grace Lyrics"
    page.theme = get_theme()
    page.theme_mode = ft.ThemeMode.DARK
    
    # Safely initialize the database inside the main thread!
    try:
        db.init_db()
        db.seed_mock_data()
    except Exception as db_err:
        page.add(ft.Text(f"CRITICAL DB INIT ERROR: {db_err}", color=ft.colors.RED))
        return

    def route_change(route):
        try:
            page.views.clear()
            
            # Always add home view as base
            page.views.append(get_home_view(page))
            
            # Admin view
            if page.route == "/admin":
                page.views.append(get_admin_view(page))
                
            # If route is a song, push the song view on top
            elif page.route.startswith("/song/"):
                song_id = page.route.split("/")[2]
                page.views.append(get_song_view(page, song_id))
                
            page.update()
        except Exception as e:
            page.views.clear()
            page.views.append(
                ft.View(
                    "/error",
                    [ft.Text(f"CRASH OCCURRED: {e}", color=ft.colors.RED, selectable=True)]
                )
            )
            page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Initialize app to home route
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main)
