import flet as ft
import json
import urllib.request
import threading
import os

# ===================== CONFIG =====================
DB_PATH = "songs.json"
PROJECT_ID = "grace-lyrics-admin"
BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/songs"

# ===================== DATA MANAGER =====================
class LyricsManager:
    def __init__(self):
        self.songs = []
        self._load()
    def _load(self):
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f: self.songs = json.load(f)
            except: pass

    def sync_cloud(self, callback):
        def _task():
            try:
                all_songs = [] ; next_token = None
                while True:
                    url = BASE_URL
                    if next_token: url += f"?pageToken={next_token}"
                    with urllib.request.urlopen(url) as r:
                        d = json.load(r)
                        for doc in d.get("documents", []):
                            f = doc.get("fields", {})
                            raw_lyrics = f.get("lyrics", f.get("Lyric", {})).get("stringValue", "")
                            # LYRICS POLISHER: Clean \n literals and standardize newlines
                            clean_lyrics = raw_lyrics.replace("\\n", "\n").replace("\\r", "\n").replace("\r\n", "\n")
                            all_songs.append({
                                "title": f.get("title", f.get("Title", {})).get("stringValue", "No Title"),
                                "lyrics": clean_lyrics,
                                "language": f.get("language", f.get("Language", {})).get("stringValue", "tamil").lower()
                            })
                        next_token = d.get("nextPageToken")
                        if not next_token: break
                self.songs = all_songs
                with open(DB_PATH, "w", encoding="utf-8") as out: json.dump(all_songs, out)
                callback(len(all_songs))
            except: callback(-1)
        threading.Thread(target=_task).start()

lm = LyricsManager()

# ===================== MAIN APP =====================
def main(page: ft.Page):
    # PREVENT BLANK SCREEN: Set colors immediately
    page.title = "Gods Grace Gospel Ministry"
    page.bgcolor = "#F5F5F5"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # APP STATE
    st = {"lang": "tamil", "q": "", "font_size": 22}

    # APP BAR (Shared)
    page.appbar = ft.AppBar(visible=False)

    # REUSABLE COMPONENTS
    body_container = ft.Container(expand=True)
    list_body = ft.ListView(expand=True, padding=ft.padding.only(left=15, right=15, bottom=20))
    search_bar = ft.TextField(
        hint_text="Search songs...", expand=True, bgcolor="white",
        border_radius=12, border_color="transparent", prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: filter_songs(e.control.value)
    )

    def filter_songs(q=""):
        st["q"] = q ; list_body.controls.clear()
        results = [s for s in lm.songs if s["language"] == st["lang"] and q.lower() in s["title"].lower()]
        for s in results:
            # SAFETY IMAGE CHECK
            icon_view = ft.Icon(ft.Icons.MUSIC_NOTE, color="#1A237E")
            if os.path.exists("icon.png"):
                icon_view = ft.Image(src="icon.png", width=30, height=30)
                
            list_body.controls.append(ft.Container(
                content=ft.ListTile(
                    leading=icon_view,
                    title=ft.Text(s["title"], weight="bold", color="black"), 
                    on_click=lambda e, song=s: show_reader(song)
                ),
                bgcolor="white", border_radius=12, border=ft.border.all(1, "#E8EAF6"), margin=ft.margin.symmetric(vertical=4),
                shadow=ft.BoxShadow(blur_radius=10, color="#10000000", offset=ft.Offset(0, 4))
            ))
        page.update()

    def show_reader(s):
        # UI Setup
        page.appbar.title = ft.Text(s["title"], color="white")
        page.appbar.bgcolor = "#1A237E"
        page.appbar.leading = ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render_home())
        page.appbar.actions = [
            ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_color="white", on_click=lambda _: zoom(-2)),
            ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, icon_color="white", on_click=lambda _: zoom(2))
        ]
        page.appbar.visible = True
        
        v_list = ft.ListView(expand=True, padding=30)
        def refresh():
            v_list.controls.clear()
            for line in s["lyrics"].split("\n"):
                if line.strip(): v_list.controls.append(ft.Text(line.strip(), size=st["font_size"], color="#2C3E50", weight="500"))
                else: v_list.controls.append(ft.Container(height=15))
            page.update()

        def zoom(delta):
            st["font_size"] = max(12, min(44, st["font_size"]+delta))
            refresh()

        body_container.content = v_list
        body_container.bgcolor = "#FFF9E1"
        refresh()

    def show_settings():
        page.appbar.title = ft.Text("Settings", color="white")
        page.appbar.visible = True
        page.appbar.actions = []
        
        logo_big = ft.Icon(ft.Icons.MUSIC_NOTE, size=100, color="#1A237E")
        if os.path.exists("icon.png"):
            logo_big = ft.Image(src="icon.png", width=120, height=120)

        def sync_act(e):
            e.control.disabled = True ; page.update()
            lm.sync_cloud(lambda cnt: (page.show_snack_bar(ft.SnackBar(ft.Text(f"Success! {cnt} songs synced."))), render_home()))

        body_container.content = ft.Container(padding=30, content=ft.Column([
            ft.Row([logo_big], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            ft.Text("Cloud Sync", size=24, weight="bold", color="black"),
            ft.Text(f"Target Project: {PROJECT_ID}", color="grey"),
            ft.Container(height=20),
            ft.ElevatedButton("SYNC NOW", icon=ft.Icons.SYNC, bgcolor="#1A237E", color="white", on_click=sync_act, height=60),
            ft.Divider(),
            ft.Text("Gods Grace Gospel Ministry v5.4.0", color="grey", size=12)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER))
        body_container.bgcolor = "#F5F5F5"
        page.update()

    def render_home():
        page.appbar.visible = False
        
        # LOGO CHECK
        logo_view = ft.Icon(ft.Icons.MUSIC_NOTE, color="white", size=40)
        if os.path.exists("icon.png"):
            logo_view = ft.Image(src="icon.png", width=50, height=50)

        header = ft.Container(
            gradient=ft.LinearGradient(begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1), colors=["#1A237E", "#283593"]),
            padding=ft.padding.only(top=40, left=20, right=20, bottom=20),
            content=ft.Column([
                ft.Row([
                    ft.Row([logo_view, ft.Column([ft.Text("Gods Grace", color="white", size=20, weight="bold", tight=True), ft.Text("Gospel Ministry", color="white", size=12)], spacing=0)]),
                    ft.IconButton(ft.Icons.SETTINGS, icon_color="white", on_click=lambda _: show_settings())
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.Row([ft.Container(content=search_bar, expand=True)])
            ])
        )
        lang_row = ft.Container(padding=15, content=ft.Row([
            ft.ElevatedButton("TAMIL", expand=1, bgcolor="#E8EAF6" if st["lang"]=="tamil" else "white", color="#1A237E" if st["lang"]=="tamil" else "grey", on_click=lambda _: (st.update({"lang": "tamil"}), filter_songs())), 
            ft.ElevatedButton("TELUGU", expand=1, bgcolor="#E8EAF6" if st["lang"]=="telugu" else "white", color="#1A237E" if st["lang"]=="telugu" else "grey", on_click=lambda _: (st.update({"lang": "telugu"}), filter_songs()))
        ], spacing=15))
        
        # ASSEMBLE HOME BODY
        home_stack = ft.Column([header, lang_row, list_body], spacing=0)
        body_container.content = home_stack
        body_container.bgcolor = "#F5F5F5"
        filter_songs(st["q"])

    # INITIAL RENDER
    page.add(body_container)
    render_home()

ft.app(target=main)
