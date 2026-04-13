import flet as ft
import json
import urllib.request
import threading
import os

# ===================== CONFIGURATION =====================
CLOUD_API_URL = "https://firestore.googleapis.com/v1/projects/grace-lyrics-545a1/databases/(default)/documents/songs"
DB_PATH = "songs.json"

class BibleEngine:
    def __init__(self):
        self.books = ["ஆதியாகமம்", "யாத்திராகமம்", "லேவியராகமம்", "எண்ணாகமம்", "உபாகமம்", "யோசுவா", "நியாயாதிபதிகள்", "ரூத்", "1 சாமுவேல்", "2 சாமுவேல்", "1 ராஜாக்கள்", "2 ராஜாக்கள்", "1 நாளாகமம்", "2 நாளாகமம்", "எஸ்றா", "நெகேமியா", "எஸ்தர்", "யோபு", "சங்கீதம்", "நீதிமொழிகள்", "பிரசங்கி", "உன்னதப்பாட்டு", "ஏசாயா", "எரேமியா", "புலம்பல்", "எசேக்கியேல்", "தானியேல்", "ஓசியா", "யோவேல்", "ஆமோஸ்", "ஒபதியா", "யோனா", "மீகா", "நாகூம்", "ஆபகூக்", "செப்பனியா", "ஆகாய்", "சகரியா", "மல்கியா", "மத்தேயு", "மாற்கு", "லூக்கா", "யோவான்", "அப்போஸ்தலர்", "ரோமர்", "1 கொரிந்தியர்", "2 கொரிந்தியர்", "கலாத்தியர்", "எபேசியர்", "பிலிப்பியர்", "கொலோசெயர்", "1 தெசலோனிக்கேயர்", "2 தெசலோனிக்கேயர்", "1 தீமோத்தேயு", "2 தீமோத்தேயு", "தீத்து", "பிலேமோன்", "எபிரெயர்", "யாக்கோபு", "1 பேதுரு", "2 பேதுரு", "1 யோவான்", "2 யோவான்", "3 யோவான்", "யூதா", "வெளிப்படுத்தின விசேஷம்"]
        self.counts = [50, 40, 27, 36, 34, 24, 21, 4, 31, 24, 22, 25, 29, 36, 10, 13, 10, 42, 150, 31, 12, 8, 66, 52, 5, 48, 12, 14, 3, 9, 1, 4, 7, 3, 3, 3, 2, 14, 4, 28, 16, 24, 21, 28, 16, 16, 13, 6, 6, 4, 4, 5, 3, 6, 4, 3, 1, 13, 5, 5, 3, 5, 1, 1, 1, 22]

    def get_list(self):
        return [{"name": n, "chapters": self.counts[i], "id": i+1} for i, n in enumerate(self.books)]

    def fetch_verses(self, book, chapter):
        # Professional Ethereal Placeholder while sync is set up
        return f"{book} {chapter}\n\n1. ஆதியிலே தேவன் வானத்தையும் பூமியையும் சிருஷ்டித்தார்.\n\n2. பூமியானது ஒழுங்கின்மையும் வெறுமையுமாய் இருந்தது; ஆழத்தின்மேல் இருள் இருந்தது; தேவ ஆவியானவர் ஜலத்தின்மேல் அசைவாடிக்கொண்டிருந்தார்.\n\n3. வெளிச்சம் உண்டாகக்கடவது என்றார், அப்பொழுது வெளிச்சம் உண்டாயிற்று."

class SongEngine:
    def __init__(self):
        self.songs = []
    def load(self, path):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f: self.songs = json.load(f)
            except: pass
        if not self.songs:
            self.songs = [{"id": "s1", "title": "அசாத்தியங்கள் சாத்தியமே", "language": "tamil", "lyrics": "அசாத்தியங்கள் சாத்தியமே\nஉம்மால் எல்லாம் கூடும்"}]

# ===================== JEWEL UI v1.3.0 =====================
bible_eng = BibleEngine()
song_eng = SongEngine()

def main(page: ft.Page):
    page.title = "GGGM Jewel Edition"
    page.padding = 0
    page.bgcolor = "#1A237E" # Base Indigo
    
    data_dir = page.client_storage.get("db_path") or "."
    song_eng.load(os.path.join(data_dir, DB_PATH))

    # State
    st = {"v": "lyrics", "lang": "tamil", "q": "", "sz": 22}

    def get_jewel_bg():
        # Clean Linear Gradient (Safe for all GPUs)
        return ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["#1A237E", "#4A148C"] # Indigo to Violet
            )
        )

    def jewel_card(content, on_click=None):
        return ft.Container(
            content=content,
            bgcolor="white",
            border_radius=25,
            padding=15,
            margin=ft.margin.symmetric(horizontal=15, vertical=5),
            shadow=ft.BoxShadow(blur_radius=15, color="#00000033"),
            on_click=on_click
        )

    def nav_bar():
        return ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.MUSIC_NOTE_ROUNDED, label="Lyrics"),
                ft.NavigationBarDestination(icon=ft.Icons.MENU_BOOK_ROUNDED, label="Bible"),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS_ROUNDED, label="Settings"),
            ],
            selected_index=0 if st["v"]=="lyrics" else 1 if st["v"]=="bible" else 2,
            on_change=lambda e: (st.update({"v": ["lyrics", "bible", "settings"][e.control.selected_index]}), render()),
            bgcolor="#ffffff", height=70
        )

    def render_lyrics():
        # Filtering logic
        songs = [s for s in song_eng.songs if s["language"] == st["lang"] and st["q"].lower() in s["title"].lower()]
        
        return ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("Grace Lyrics", size=32, weight="bold", color="white"),
                    ft.TextField(
                        hint_text="Search lyrics...", prefix_icon=ft.Icons.SEARCH,
                        border_radius=15, border_color="white24", bgcolor="white10", color="white",
                        on_change=lambda e: (st.update({"q": e.control.value}), render())
                    ),
                    ft.Row([
                        ft.ElevatedButton("TAMIL", expand=1, on_click=lambda _: (st.update({"lang": "tamil"}), render())),
                        ft.ElevatedButton("TELUGU", expand=1, on_click=lambda _: (st.update({"lang": "telugu"}), render())),
                    ], spacing=10)
                ], spacing=20),
                padding=ft.Padding(25, 60, 25, 20)
            ),
            ft.Column([jewel_card(
                ft.ListTile(
                    title=ft.Text(s["title"], weight="bold", size=16),
                    leading=ft.Icon(ft.Icons.MUSIC_VIDEO_ROUNDED, color="#1A237E"),
                    trailing=ft.Icon(ft.Icons.ARROW_FORWARD_IOS_ROUNDED, size=14)
                ),
                on_click=lambda e, s=s: show_details(s)
            ) for s in songs], scroll="auto", expand=True)
        ], expand=True)

    def show_details(s):
        page.clean()
        page.add(ft.Stack([
            get_jewel_bg(),
            ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color="white", on_click=lambda _: back_home()),
                        ft.Text(s["title"], weight="bold", size=20, color="white", expand=1),
                        ft.IconButton(ft.Icons.SHARE_ROUNDED, icon_color="white"),
                    ]), padding=ft.Padding(15, 50, 15, 10)
                ),
                ft.Container(
                    content=ft.Column([ft.Text(s["lyrics"], size=st["sz"], color="#2c3e50", line_height=1.5)], scroll="auto"),
                    expand=True, padding=30, bgcolor="#FFF9E1", border_radius=ft.border_radius.only(top_left=40, top_right=40)
                )
            ], expand=True)
        ]))
        page.update()

    def render_bible():
        books = bible_eng.get_list()
        grid = ft.GridView(expand=True, runs_count=2, spacing=15, padding=20)
        for b in books:
            grid.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.BOOK_ROUNDED, color="#1A237E"),
                        ft.Text(b["name"], weight="bold", size=14, text_align="center")
                    ], alignment="center", spacing=5),
                    bgcolor="white", border_radius=20, shadow=ft.BoxShadow(blur_radius=10, color="#00000011"),
                    on_click=lambda e, bk=b: show_chapters(bk)
                )
            )
        return ft.Column([
            ft.Container(content=ft.Text("Sacred Bible", size=32, weight="bold", color="white"), padding=ft.Padding(25, 60, 25, 10)),
            grid
        ], expand=True)

    def show_chapters(book):
        page.clean()
        grid = ft.GridView(expand=True, runs_count=5, spacing=10, padding=20)
        for i in range(1, book["chapters"]+1):
            grid.controls.append(ft.Container(content=ft.Text(str(i), weight="bold"), bgcolor="white", border_radius=12, alignment=ft.alignment.center, on_click=lambda e, c=i: show_reader(book, c)))
        page.add(ft.Stack([
            get_jewel_bg(),
            ft.Column([
                ft.Container(content=ft.Row([ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color="white", on_click=lambda _: back_home()), ft.Text(book["name"], color="white", size=22, weight="bold")]), padding=ft.Padding(15, 50, 15, 10)),
                grid
            ], expand=True)
        ]))
        page.update()

    def show_reader(book, ch):
        verses = bible_eng.fetch_verses(book["name"], ch)
        page.clean()
        page.add(ft.Stack([
            get_jewel_bg(),
            ft.Column([
                ft.Container(content=ft.Row([ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color="white", on_click=lambda _: show_chapters(book)), ft.Text(f"{book['name']} {ch}", color="white", size=20, weight="bold")]), padding=ft.Padding(15, 50, 15, 10)),
                ft.Container(content=ft.Column([ft.Text(verses, size=st["sz"], color="#2c3e50", line_height=1.6)], scroll="auto"), expand=True, padding=30, bgcolor="#FFF9E1", border_radius=ft.border_radius.only(top_left=35, top_right=35))
            ], expand=True)
        ]))
        page.update()

    def back_home():
        page.clean()
        page.navigation_bar = nav_bar()
        render()

    def render():
        page.controls.clear()
        page.navigation_bar = nav_bar()
        v = {"lyrics": render_lyrics, "bible": render_bible, "settings": lambda: ft.Container(content=ft.Text("Settings", color="white"), padding=50)}[st["v"]]()
        page.add(ft.Stack([get_jewel_bg(), v]))
        page.update()

    render()

ft.app(target=main)
