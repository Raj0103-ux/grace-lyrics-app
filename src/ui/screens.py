import flet as ft
from src.models.db import get_songs_by_language, get_song_by_id, toggle_favorite, fetch_all_from_cloud

def create_song_list(page: ft.Page, language: str, search_query: str = ""):
    songs = get_songs_by_language(language, search_query)
    
    if not songs:
        return ft.Container(
            content=ft.Text(f"No {language} songs found natively yet. Did you sync from the cloud?", color=page.theme.color_scheme.secondary),
            alignment=ft.alignment.center,
            padding=20
        )
    
    list_view = ft.ListView(expand=True, spacing=10, padding=10)
    for song in songs:
        list_view.controls.append(
            ft.Card(
                content=ft.ListTile(
                    leading=ft.Icon(ft.icons.MUSIC_NOTE, color=page.theme.color_scheme.secondary),
                    title=ft.Text(f"{song.number}. {song.title}" if song.number else song.title, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(f"{len(song.lyrics.splitlines())} lines", color=page.theme.color_scheme.secondary),
                    trailing=ft.Icon(ft.icons.FAVORITE if song.is_favorite else ft.icons.CHEVRON_RIGHT, 
                                     color=ft.colors.RED_400 if song.is_favorite else None),
                    on_click=lambda e, s=song: _navigate_to_song(page, s)
                )
            )
        )
    return list_view

def _navigate_to_song(page: ft.Page, song):
    page.go(f"/song/{song.id}")
    
def _navigate_to_admin(page: ft.Page):
    page.go(f"/admin")

class HomeView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__("/", [])
        self.page = page
        self.search_query = ""
        self.current_tab_index = 0
        
        self.search_field = ft.TextField(
            hint_text="Search song title...",
            on_change=self.handle_search_change,
            expand=True,
            autofocus=True,
            border_color="transparent",
            content_padding=5
        )
        
        self.search_bar_container = ft.Container(
            content=self.search_field,
            visible=False,
            bgcolor=page.theme.color_scheme.surface,
            padding=10
        )
        
        self.tabs = ft.Tabs(
            selected_index=self.current_tab_index,
            on_change=self.handle_tab_change,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Tamil", icon=ft.icons.LANGUAGE, content=create_song_list(page, "tamil")),
                ft.Tab(text="Telugu", icon=ft.icons.LANGUAGE, content=create_song_list(page, "telugu")),
            ],
            expand=1,
        )
        
        self.controls = [
            ft.AppBar(
                title=ft.Text("Grace Lyrics", color=page.theme.color_scheme.secondary, weight=ft.FontWeight.BOLD),
                bgcolor=page.theme.color_scheme.primary,
                center_title=True,
                actions=[
                    ft.IconButton(ft.icons.SEARCH, icon_color=page.theme.color_scheme.secondary, on_click=self.toggle_search),
                    ft.IconButton(ft.icons.SETTINGS, icon_color=page.theme.color_scheme.secondary, on_click=lambda e: _navigate_to_admin(page))
                ]
            ),
            self.search_bar_container,
            self.tabs
        ]

    def handle_search_change(self, e):
        self.search_query = e.control.value
        self.update_lists()
        
    def toggle_search(self, e):
        self.search_bar_container.visible = not self.search_bar_container.visible
        if not self.search_bar_container.visible:
            self.search_query = ""
            self.search_field.value = ""
        self.page.update()
        self.update_lists()
        
    def handle_tab_change(self, e):
        self.current_tab_index = e.control.selected_index
        
    def update_lists(self):
        self.tabs.tabs[0].content = create_song_list(self.page, "tamil", self.search_query)
        self.tabs.tabs[1].content = create_song_list(self.page, "telugu", self.search_query)
        self.page.update()


class SongView(ft.View):
    def __init__(self, page: ft.Page, song_id: str):
        super().__init__(f"/song/{song_id}", [])
        self.page = page
        self.song = get_song_by_id(song_id)
        self.font_size = 18
        
        if not self.song:
            self.controls.append(ft.Text("Song not found in cache. Did you sync?"))
            return
            
        self.lyrics_text = ft.Text(self.song.lyrics, size=self.font_size, selectable=True)
        self.fav_icon = ft.Icon(
            name=ft.icons.FAVORITE if self.song.is_favorite else ft.icons.FAVORITE_BORDER,
            color=ft.colors.RED_400 if self.song.is_favorite else page.theme.color_scheme.secondary
        )
        
        self.controls = [
            ft.AppBar(
                title=ft.Text(self.song.title, size=16),
                bgcolor=page.theme.color_scheme.primary,
                actions=[
                    ft.IconButton(
                        icon=ft.icons.TEXT_DECREASE, 
                        icon_color=page.theme.color_scheme.secondary,
                        on_click=self.decrease_font
                    ),
                    ft.IconButton(
                        icon=ft.icons.TEXT_INCREASE, 
                        icon_color=page.theme.color_scheme.secondary,
                        on_click=self.increase_font
                    ),
                    ft.IconButton(
                        content=self.fav_icon,
                        on_click=self.toggle_fav
                    )
                ]
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(self.song.title, size=24, weight=ft.FontWeight.BOLD, color=page.theme.color_scheme.primary),
                        ft.Divider(),
                        self.lyrics_text,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
                expand=True
            )
        ]

    def increase_font(self, e):
        if self.font_size < 40:
            self.font_size += 2
            self.lyrics_text.size = self.font_size
            self.page.update()
            
    def decrease_font(self, e):
        if self.font_size > 12:
            self.font_size -= 2
            self.lyrics_text.size = self.font_size
            self.page.update()

    def toggle_fav(self, e):
        new_status = toggle_favorite(self.song.id)
        self.song.is_favorite = new_status
        self.fav_icon.name = ft.icons.FAVORITE if new_status else ft.icons.FAVORITE_BORDER
        self.fav_icon.color = ft.colors.RED_400 if new_status else self.page.theme.color_scheme.secondary
        self.page.update()


def get_home_view(page: ft.Page):
    return HomeView(page)

def get_song_view(page: ft.Page, song_id: str):
    return SongView(page, song_id)

class AdminView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__("/admin", [])
        self.page = page
        
        self.status_text = ft.Text("Ready.", color=ft.colors.GREEN)
        
        self.controls = [
            ft.AppBar(
                title=ft.Text("Cloud Sync Tools", size=16),
                bgcolor=page.theme.color_scheme.primary,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Database Synchronization", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Click the button below to download the latest songs from the administrative cloud. This will update your offline cache instantly."),
                        ft.ElevatedButton(
                            text="Sync Now",
                            icon=ft.icons.CLOUD_DOWNLOAD,
                            on_click=self.trigger_sync
                        ),
                        self.status_text
                    ]
                ),
                padding=20,
                expand=True
            )
        ]
        
    def trigger_sync(self, e):
        self.status_text.value = "Syncing from cloud..."
        self.status_text.color = ft.colors.BLUE
        self.page.update()
        
        try:
            count = fetch_all_from_cloud()
            self.status_text.value = f"Successfully synced {count} songs locally."
            self.status_text.color = ft.colors.GREEN
        except Exception as ex:
            self.status_text.value = f"Error syncing: {ex}"
            self.status_text.color = ft.colors.RED
            
        self.page.update()

def get_admin_view(page: ft.Page):
    return AdminView(page)

