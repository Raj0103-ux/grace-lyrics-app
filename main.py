import flet as ft
import json
import urllib.request
import threading
import os

# ===================== CONFIG =====================
DB_PATH = "songs.json"
FIREBASE_URL = "https://firestore.googleapis.com/v1/projects/grace-lyrics-545a1/databases/(default)/documents/songs"

class LyricsState:
    def __init__(self):
        self.songs = []
        self._load()
    def _load(self):
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f: self.songs = json.load(f)
            except: pass
    def sync(self, callback):
        def _task():
            try:
                with urllib.request.urlopen(FIREBASE_URL) as r:
                    d = json.load(r)
                    new_list = []
                    for doc in d.get("documents", []):
                        f = doc.get("fields", {})
                        new_list.append({
                            "title": f.get("title", {}).get("stringValue", "No Title"),
                            "lyrics": f.get("lyrics", {}).get("stringValue", ""),
                            "language": f.get("language", {}).get("stringValue", "tamil").lower()
                        })
                    self.songs = new_list
                    with open(DB_PATH, "w", encoding="utf-8") as out: json.dump(new_list, out)
                    callback(True)
            except: callback(False)
        threading.Thread(target=_task).start()

ls = LyricsState()

def main(page: ft.Page):
    # ===================== UI CONSTANTS =====================
    INDIGO_GRADIENT = ft.LinearGradient(
        begin=ft.alignment.top_center,
        end=ft.alignment.bottom_center,
        colors=["#1A237E", "#283593"]
    )
    PARCHMENT_BG = "#FFF9E1" # Digital Hymn Book Texture
    CARD_BG = "#FFFFFF"
    
    page.title = "Grace Lyrics Premium"
    page.bgcolor = "#F5F5F5"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    st = {"lang": "tamil", "q": ""}
    
    # ===================== NAVIGATION LOGIC =====================
    def route_change(route):
        page.views.clear()
        
        # HOME VIEW
        if page.route == "/":
            home_view()
        # SETTINGS VIEW
        elif page.route == "/settings":
            settings_view()
        # LYRICS VIEW (Handled dynamically)
        elif page.route.startswith("/song/"):
            song_idx = int(page.route.split("/")[-1])
            song_view(ls.songs[song_idx])
            
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # ===================== COMPONENT: HOME =====================
    def home_view():
        list_body = ft.ListView(expand=True, padding=ft.padding.only(left=15, right=15, bottom=20))
        
        def filter_songs(q=""):
            st["q"] = q
            list_body.controls.clear()
            results = [s for s in ls.songs if s["language"] == st["lang"] and q.lower() in s["title"].lower()]
            for i, s in enumerate(ls.songs):
                if s["language"] == st["lang"] and q.lower() in s["title"].lower():
                    # HYMN BOOK STYLE CARD
                    list_body.controls.append(ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.Icons.MUSIC_NOTE, color="#1A237E", size=20),
                            title=ft.Text(s["title"], weight="bold", color="black", size=16),
                            on_click=lambda e, idx=i: page.go(f"/song/{idx}")
                        ),
                        bgcolor=CARD_BG,
                        border_radius=12,
                        border=ft.border.all(1, "#E8EAF6"),
                        shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.with_opacity(0.05, "black"), offset=ft.Offset(0, 4)),
                        margin=ft.margin.symmetric(vertical=6)
                    ))
            page.update()

        # Premium Header
        header = ft.Container(
            gradient=INDIGO_GRADIENT,
            padding=ft.padding.only(top=40, left=20, right=20, bottom=20),
            content=ft.Column([
                ft.Row([
                    ft.Image(src="icon.png", width=40, height=40),
                    ft.Text("Grace Lyrics", color="white", size=24, weight="bold"),
                    ft.IconButton(ft.Icons.SETTINGS, icon_color="white", on_click=lambda _: page.go("/settings"))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.TextField(
                    hint_text="Search hymns...",
                    bgcolor="white",
                    border_radius=10,
                    prefix_icon=ft.Icons.SEARCH,
                    border_color="transparent",
                    on_change=lambda e: filter_songs(e.control.value)
                )
            ])
        )

        lang_toggle = ft.Container(
            padding=15,
            content=ft.Row([
                ft.ElevatedButton("TAMIL", expand=1, bgcolor="#E8EAF6" if st["lang"]=="tamil" else "white", color="#1A237E" if st["lang"]=="tamil" else "grey", on_click=lambda _: (st.update({"lang": "tamil"}), filter_songs(st["q"]))),
                ft.ElevatedButton("TELUGU", expand=1, bgcolor="#E8EAF6" if st["lang"]=="telugu" else "white", color="#1A237E" if st["lang"]=="telugu" else "grey", on_click=lambda _: (st.update({"lang": "telugu"}), filter_songs(st["q"]))),
            ], spacing=15)
        )

        page.views.append(ft.View("/", [header, lang_toggle, list_body], padding=0, bgcolor="#F5F5F5"))
        filter_songs(st["q"])

    # ===================== COMPONENT: SETTINGS =====================
    def settings_view():
        def sync_now(e):
            ls.sync(lambda success: (
                page.show_snack_bar(ft.SnackBar(ft.Text("Cloud Sync Complete!" if success else "Connection Fail"))) if success else None,
                page.go("/")
            ))

        page.views.append(ft.View("/settings", [
            ft.AppBar(title=ft.Text("Settings", color="white"), bgcolor="#1A237E", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: page.go("/"))),
            ft.Container(padding=30, content=ft.Column([
                ft.Text("Data Synchronization", size=20, weight="bold", color="black"),
                ft.ListTile(
                    title=ft.Text("Sync with Firebase", color="black"),
                    subtitle=ft.Text("Pull latest lyrics from the cloud", color="grey"),
                    leading=ft.Icon(ft.Icons.CLOUD_SYNC, color="#1A237E"),
                    on_click=sync_now
                ),
                ft.Divider(),
                ft.Text("Grace Lyrics Premium v4.0", size=12, color="grey")
            ]))
        ], bgcolor="white", padding=0))

    # ===================== COMPONENT: SONG READING =====================
    def song_view(s):
        verses = s["lyrics"].split("\n")
        v_list = ft.ListView(expand=True, padding=30)
        for line in verses:
            if line.strip():
                # HYMN BOOK STYLE TYPOGRAPHY
                v_list.controls.append(ft.Text(line, size=21, color="#2C3E50", weight="500", line_height=1.5))
            else:
                v_list.controls.append(ft.Container(height=15))

        page.views.append(ft.View(f"/song", [
            ft.AppBar(
                title=ft.Text(s["title"], color="white"),
                bgcolor="#1A237E",
                leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: page.go("/"))
            ),
            v_list
        ], bgcolor=PARCHMENT_BG, padding=0))

    # Start the app
    page.go("/")

ft.app(target=main)
