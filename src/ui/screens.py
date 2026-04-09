import flet as ft
from src.models.db import get_songs_by_language, get_song_by_id, toggle_favorite, fetch_all_from_cloud

def create_song_list(page: ft.Page, language: str, search_query: str = ""):
    try:
        songs = get_songs_by_language(language, search_query)
        if not songs:
            return ft.Container(
                content=ft.Text(f"No {language} songs yet. Tap Settings > Sync Now.", color=page.theme.color_scheme.secondary),
                alignment=ft.alignment.center, padding=20)
        lv = ft.ListView(expand=True, spacing=10, padding=10)
        for song in songs:
            lv.controls.append(ft.Card(content=ft.ListTile(
                leading=ft.Icon(ft.Icons.MUSIC_NOTE, color=page.theme.color_scheme.secondary),
                title=ft.Text(f"{song.number}. {song.title}" if song.number else song.title, weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(f"{len(song.lyrics.splitlines())} lines", color=page.theme.color_scheme.secondary),
                trailing=ft.Icon(ft.Icons.FAVORITE if song.is_favorite else ft.Icons.CHEVRON_RIGHT, color=ft.Colors.RED_400 if song.is_favorite else None),
                on_click=lambda e, s=song: page.go(f"/song/{s.id}"))))
        return lv
    except Exception as e:
        return ft.Text(f"Error: {e}", color=ft.Colors.RED)

class HomeView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__("/", [])
        self.page = page
        self.search_query = ""
        self.search_field = ft.TextField(hint_text="Search song title...", on_change=self.on_search, expand=True, border_color="transparent", content_padding=5)
        self.search_bar = ft.Container(content=self.search_field, visible=False, padding=10)
        self.tabs = ft.Tabs(selected_index=0, animation_duration=300, tabs=[
            ft.Tab(text="Tamil", icon=ft.Icons.LANGUAGE, content=create_song_list(page, "tamil")),
            ft.Tab(text="Telugu", icon=ft.Icons.LANGUAGE, content=create_song_list(page, "telugu"))], expand=1)
        self.controls = [
            ft.AppBar(title=ft.Text("GGGM", color=page.theme.color_scheme.secondary, weight=ft.FontWeight.BOLD), bgcolor=page.theme.color_scheme.primary, center_title=True, actions=[
                ft.IconButton(ft.Icons.SEARCH, icon_color=page.theme.color_scheme.secondary, on_click=self.toggle_search),
                ft.IconButton(ft.Icons.SETTINGS, icon_color=page.theme.color_scheme.secondary, on_click=lambda e: page.go("/admin"))]),
            self.search_bar, self.tabs]

    def on_search(self, e):
        self.search_query = e.control.value
        self.tabs.tabs[0].content = create_song_list(self.page, "tamil", self.search_query)
        self.tabs.tabs[1].content = create_song_list(self.page, "telugu", self.search_query)
        self.page.update()

    def toggle_search(self, e):
        self.search_bar.visible = not self.search_bar.visible
        if not self.search_bar.visible:
            self.search_query = ""
            self.search_field.value = ""
            self.tabs.tabs[0].content = create_song_list(self.page, "tamil")
            self.tabs.tabs[1].content = create_song_list(self.page, "telugu")
        self.page.update()

class SongView(ft.View):
    def __init__(self, page: ft.Page, song_id: str):
        super().__init__(f"/song/{song_id}", [])
        self.page = page
        self.song = get_song_by_id(song_id)
        self.font_size = 18
        if not self.song:
            self.controls.append(ft.Text("Song not found. Try syncing."))
            return
        self.lyrics_text = ft.Text(self.song.lyrics, size=self.font_size, selectable=True)
        self.fav_icon = ft.Icon(name=ft.Icons.FAVORITE if self.song.is_favorite else ft.Icons.FAVORITE_BORDER, color=ft.Colors.RED_400 if self.song.is_favorite else page.theme.color_scheme.secondary)
        self.controls = [
            ft.AppBar(title=ft.Text(self.song.title, size=16), bgcolor=page.theme.color_scheme.primary, actions=[
                ft.IconButton(icon=ft.Icons.TEXT_DECREASE, icon_color=page.theme.color_scheme.secondary, on_click=self.dec_font),
                ft.IconButton(icon=ft.Icons.TEXT_INCREASE, icon_color=page.theme.color_scheme.secondary, on_click=self.inc_font),
                ft.IconButton(content=self.fav_icon, on_click=self.toggle_fav)]),
            ft.Container(content=ft.Column([
                ft.Text(self.song.title, size=24, weight=ft.FontWeight.BOLD, color=page.theme.color_scheme.primary),
                ft.Divider(), self.lyrics_text], scroll=ft.ScrollMode.AUTO), padding=20, expand=True)]

    def inc_font(self, e):
        if self.font_size < 40:
            self.font_size += 2; self.lyrics_text.size = self.font_size; self.page.update()
    def dec_font(self, e):
        if self.font_size > 12:
            self.font_size -= 2; self.lyrics_text.size = self.font_size; self.page.update()
    def toggle_fav(self, e):
        ns = toggle_favorite(self.song.id)
        self.song.is_favorite = ns
        self.fav_icon.name = ft.Icons.FAVORITE if ns else ft.Icons.FAVORITE_BORDER
        self.fav_icon.color = ft.Colors.RED_400 if ns else self.page.theme.color_scheme.secondary
        self.page.update()

class AdminView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__("/admin", [])
        self.page = page
        self.status_text = ft.Text("Ready.", color=ft.Colors.GREEN)
        self.controls = [
            ft.AppBar(title=ft.Text("Cloud Sync Tools", size=16), bgcolor=page.theme.color_scheme.primary),
            ft.Container(content=ft.Column([
                ft.Text("Database Synchronization", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Download the latest songs from the cloud."),
                ft.ElevatedButton(text="Sync Now", on_click=self.sync),
                self.status_text]), padding=20, expand=True)]

    def sync(self, e):
        self.status_text.value = "Syncing..."; self.status_text.color = ft.Colors.BLUE; self.page.update()
        try:
            c = fetch_all_from_cloud()
            self.status_text.value = f"Synced {c} songs."; self.status_text.color = ft.Colors.GREEN
        except Exception as ex:
            self.status_text.value = f"Error: {ex}"; self.status_text.color = ft.Colors.RED
        self.page.update()

def get_home_view(page): return HomeView(page)
def get_song_view(page, sid): return SongView(page, sid)
def get_admin_view(page): return AdminView(page)
