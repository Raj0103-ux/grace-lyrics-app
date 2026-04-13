import flet as ft
import json
import urllib.request
import threading
import os

# ===================== CONFIGURATION =====================
CLOUD_API_URL = "https://firestore.googleapis.com/v1/projects/grace-lyrics-545a1/databases/(default)/documents/songs"
DB_PATH = "songs.json"

class BibleManager:
    def __init__(self):
        self.books = ["ஆதியாகமம்", "யாத்திராகமம்", "லேவியராகமம்", "எண்ணாகமம்", "உபாகமம்", "யோசுவா", "நியாயாதிபதிகள்", "ரூத்", "1 சாமுவேல்", "2 சாமுவேல்", "1 ராஜாக்கள்", "2 ராஜாக்கள்", "1 நாளாகமம்", "2 நாளாகமம்", "எஸ்றா", "நெகேமியா", "எஸ்தர்", "யோபு", "சங்கீதம்", "நீதிமொழிகள்", "பிரசங்கி", "உன்னதப்பாட்டு", "ஏசாயா", "எரேமியா", "புலம்பல்", "எசேக்கியேல்", "தானியேல்", "ஓசியா", "யோவேல்", "ஆமோஸ்", "ஒபதியா", "யோனா", "மீகா", "நாகூம்", "ஆபகூக்", "செப்பனியா", "ஆகாய்", "சகரியா", "மல்கியா", "மத்தேயு", "மாற்கு", "லூக்கா", "யோவான்", "அப்போஸ்தலர்", "ரோமர்", "1 கொரிந்தியர்", "2 கொரிந்தியர்", "கலாத்தியர்", "எபேசியர்", "பிலிப்பியர்", "கொலோசெயர்", "1 தெசலோனிக்கேயர்", "2 தெசலோனிக்கேயர்", "1 தீமோத்தேயு", "2 தீமோத்தேயு", "தீத்து", "பிலேமோன்", "எபிரெயர்", "யாக்கோபு", "1 பேதுரு", "2 பேதுரு", "1 யோவான்", "2 யோவான்", "3 யோவான்", "யூதா", "வெளிப்படுத்தின விசேஷம்"]
        self.counts = [50, 40, 27, 36, 34, 24, 21, 4, 31, 24, 22, 25, 29, 36, 10, 13, 10, 42, 150, 31, 12, 8, 66, 52, 5, 48, 12, 14, 3, 9, 1, 4, 7, 3, 3, 3, 2, 14, 4, 28, 16, 24, 21, 28, 16, 16, 13, 6, 6, 4, 4, 5, 3, 6, 4, 3, 1, 13, 5, 5, 3, 5, 1, 1, 1, 22]
    def get_list(self): return [{"name": n, "ch": self.counts[i], "id": i+1} for i, n in enumerate(self.books)]

class SongManager:
    def __init__(self):
        self.songs = []
        self._load()
    def _load(self):
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f: self.songs = json.load(f)
            except: pass
        if not self.songs:
            self.songs = [{"id": "s1", "title": "அசாத்தியங்கள் சாத்தியமே", "language": "tamil", "lyrics": "அசாத்தியங்கள் சாத்தியமே\nஉம்மால் எல்லாம் கூடும்"}]

bible_eng = BibleManager()
song_eng = SongManager()

def main(page: ft.Page):
    page.title = "GGGM Super App"
    page.bgcolor = "#F5F5F5"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    st = {"v": "lyrics", "l": "tamil", "q": ""}

    def get_bg():
        # Clean Background Logo (Stays behind everything)
        return ft.Container(
            content=ft.Image(src="icon.png", opacity=0.08, width=300, height=300),
            alignment=ft.alignment.center, expand=True
        )

    def render():
        page.clean()
        page.appbar = ft.AppBar(
            title=ft.Text("Grace Lyrics" if st["v"]=="lyrics" else "Sacred Bible" if st["v"]=="bible" else "Settings", color="white", weight="bold"),
            bgcolor="#1A237E", elevation=4
        )
        page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.MUSIC_NOTE, label="Lyrics"),
                ft.NavigationBarDestination(icon=ft.Icons.MENU_BOOK, label="Bible"),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings"),
            ],
            selected_index=0 if st["v"]=="lyrics" else 1 if st["v"]=="bible" else 2,
            on_change=lambda e: (st.update({"v": ["lyrics", "bible", "settings"][e.control.selected_index]}), render())
        )

        content = ft.Column(expand=True)
        
        if st["v"] == "lyrics":
            songs = [s for s in song_eng.songs if s["language"] == st["l"] and st["q"].lower() in s["title"].lower()]
            content.controls = [
                ft.Container(content=ft.Column([
                    ft.TextField(hint_text="Search lyrics...", prefix_icon=ft.Icons.SEARCH, bgcolor="white", border_radius=12, on_change=lambda e: (st.update({"q": e.control.value}), render())),
                    ft.Row([
                        ft.ElevatedButton("TAMIL", expand=1, on_click=lambda _: (st.update({"l": "tamil"}), render())),
                        ft.ElevatedButton("TELUGU", expand=1, on_click=lambda _: (st.update({"l": "telugu"}), render())),
                    ])
                ]), padding=15),
                ft.ListView([ft.Container(content=ft.ListTile(title=ft.Text(s["title"], weight="bold"), leading=ft.Icon(ft.Icons.MUSIC_VIDEO, color="#1A237E"), on_click=lambda e, s=s: show_song(s)), bgcolor="white", border_radius=15, margin=ft.margin.symmetric(horizontal=15, vertical=5), shadow=ft.BoxShadow(blur_radius=10, color="#00000011")) for s in songs], expand=True)
            ]
        elif st["v"] == "bible":
            books = bible_eng.get_list()
            grid = ft.GridView(expand=True, runs_count=2, spacing=12, padding=15)
            for b in books:
                grid.controls.append(ft.Container(content=ft.Text(b["name"], weight="bold", size=14, text_align="center"), bgcolor="white", border_radius=15, alignment=ft.alignment.center, height=80, shadow=ft.BoxShadow(blur_radius=8, color="#00000008"), on_click=lambda e, bk=b: show_chapters(bk)))
            content.controls = [grid]
        elif st["v"] == "settings":
            content.controls = [
                ft.Container(content=ft.Column([
                    ft.ListTile(title=ft.Text("Cloud Sync"), leading=ft.Icon(ft.Icons.SYNC), on_click=lambda _: print("Syncing...")),
                    ft.ListTile(title=ft.Text("About GGGM v1.6.0"), leading=ft.Icon(ft.Icons.INFO_OUTLINE)),
                ]), padding=20)
            ]

        page.add(ft.Stack([get_bg(), content], expand=True))
        page.update()

    def show_song(s):
        page.clean()
        page.appbar = ft.AppBar(title=ft.Text(s["title"]), bgcolor="#1A237E", color="white", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render()))
        page.add(ft.Stack([get_bg(), ft.Container(content=ft.ListView([ft.Text(s["lyrics"], size=22)], padding=30), expand=True, bgcolor="#FFF9E166")]))
        page.update()

    def show_chapters(book):
        page.clean()
        page.appbar = ft.AppBar(title=ft.Text(book["name"]), bgcolor="#1A237E", color="white", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render()))
        grid = ft.GridView(expand=True, runs_count=5, spacing=10, padding=20)
        for i in range(1, book["ch"]+1):
            grid.controls.append(ft.Container(content=ft.Text(str(i), weight="bold"), bgcolor="white", border_radius=10, alignment=ft.alignment.center, on_click=lambda e: print(f"Ch {i}")))
        page.add(ft.Stack([get_bg(), grid]))
        page.update()

    render()

ft.app(target=main)
