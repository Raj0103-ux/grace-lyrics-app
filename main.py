import flet as ft
import json
import urllib.request
import threading
import os

# ===================== CONFIG =====================
DB_PATH = "songs.json"
FIREBASE_URL = "https://firestore.googleapis.com/v1/projects/grace-lyrics-545a1/databases/(default)/documents/songs"

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
                with urllib.request.urlopen(FIREBASE_URL) as r:
                    d = json.load(r)
                    nl = []
                    for doc in d.get("documents", []):
                        f = doc.get("fields", {})
                        nl.append({
                            "title": f.get("title", {}).get("stringValue", "No Title"),
                            "lyrics": f.get("lyrics", {}).get("stringValue", ""),
                            "language": f.get("language", {}).get("stringValue", "tamil").lower()
                        })
                    self.songs = nl
                    with open(DB_PATH, "w", encoding="utf-8") as out: json.dump(nl, out)
                    callback(True)
            except: callback(False)
        threading.Thread(target=_task).start()

lm = LyricsManager()

# ===================== MAIN APP =====================
def main(page: ft.Page):
    # UI THEME
    page.title = "Grace Hub Zero-G"
    page.bgcolor = "#F5F5F5"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    
    st = {"lang": "tamil", "q": "", "view": "home"}

    # GLOBAL LIST REFS
    list_body = ft.ListView(expand=True, padding=ft.padding.only(left=15, right=15, bottom=20))
    search_bar = ft.TextField(
        hint_text="Search lyrics...", expand=True, bgcolor="white",
        border_radius=12, border_color="transparent", prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: filter_songs(e.control.value)
    )

    def filter_songs(q=""):
        st["q"] = q
        list_body.controls.clear()
        results = [s for s in lm.songs if s["language"] == st["lang"] and q.lower() in s["title"].lower()]
        for s in results:
            list_body.controls.append(ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.MUSIC_NOTE, color="#1A237E"),
                    title=ft.Text(s["title"], weight="bold", color="black"),
                    on_click=lambda e, song=s: show_detail(song)
                ),
                bgcolor="white", border_radius=12, border=ft.border.all(1, "#E8EAF6"), margin=ft.margin.symmetric(vertical=4),
                shadow=ft.BoxShadow(blur_radius=10, color="#10000000", offset=ft.Offset(0, 4))
            ))
        page.update()

    def show_detail(s):
        page.clean()
        # HYMN BOOK STYLE READER
        v_list = ft.ListView(expand=True, padding=30)
        for line in s["lyrics"].split("\n"):
            if line.strip(): v_list.controls.append(ft.Text(line, size=22, color="#2C3E50", weight="500"))
            else: v_list.controls.append(ft.Container(height=15))
            
        page.appbar = ft.AppBar(
            title=ft.Text(s["title"], color="white"),
            bgcolor="#1A237E",
            leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render_home())
        )
        page.bgcolor = "#FFF9E1" # Parchment
        page.add(v_list)
        page.update()

    def show_settings():
        page.clean()
        def msg(m): page.snack_bar = ft.SnackBar(ft.Text(m)); page.snack_bar.open = True; page.update()
        page.appbar = ft.AppBar(title=ft.Text("Settings", color="white"), bgcolor="#1A237E", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render_home()))
        page.bgcolor = "#F5F5F5"
        page.add(ft.Container(padding=30, content=ft.Column([
            ft.Text("Cloud Controls", size=24, weight="bold", color="black"),
            ft.ListTile(
                title=ft.Text("Sync Now with Firebase", color="black"),
                leading=ft.Icon(ft.Icons.CLOUD_DOWNLOAD, color="#1A237E"),
                on_click=lambda _: lm.sync_cloud(lambda s: msg("Sync Success!" if s else "Sync Fail") or render_home())
            ),
            ft.Divider(),
            ft.Text("App Version 5.0.0 (IronLite)", color="grey")
        ])))
        page.update()

    def render_home():
        page.clean()
        page.bgcolor = "#F5F5F5"
        page.appbar = None # Using Custom Header for Premium look
        
        # PRO GRADIENT HEADER
        header = ft.Container(
            gradient=ft.LinearGradient(begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1), colors=["#1A237E", "#283593"]),
            padding=ft.padding.only(top=40, left=20, right=20, bottom=20),
            content=ft.Column([
                ft.Row([
                    ft.Row([ft.Image(src="icon.png", width=40, height=40), ft.Text("Grace Lyrics", color="white", size=24, weight="bold")]),
                    ft.IconButton(ft.Icons.SETTINGS, icon_color="white", on_click=lambda _: show_settings())
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.Row([ft.Container(content=search_bar, expand=True)])
            ])
        )

        lang_row = ft.Container(padding=15, content=ft.Row([
            ft.ElevatedButton("TAMIL", expand=1, bgcolor="#E8EAF6" if st["lang"]=="tamil" else "white", color="#1A237E" if st["lang"]=="tamil" else "grey", on_click=lambda _: (st.update({"lang": "tamil"}), filter_songs())),
            ft.ElevatedButton("TELUGU", expand=1, bgcolor="#E8EAF6" if st["lang"]=="telugu" else "white", color="#1A237E" if st["lang"]=="telugu" else "grey", on_click=lambda _: (st.update({"lang": "telugu"}), filter_songs())),
        ], spacing=15))

        page.add(header, lang_row, list_body)
        filter_songs(st["q"])

    # STARTING
    render_home()

ft.app(target=main)
