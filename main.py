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
    def get_list(self): return [{"name": n, "chapters": self.counts[i]} for i, n in enumerate(self.books)]

bible_eng = BibleManager()

def main(page: ft.Page):
    page.title = "Grace Lyrics"
    page.bgcolor = "#F5F5F5" # Light Gray
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    st = {"v": "lyrics", "l": "tamil", "q": ""}

    def wrap_with_logo(content):
        # CENTERED WATERMARK LOGO
        return ft.Container(
            content=content,
            expand=True,
            image_src="icon.png", # Automatically looks in the root or assets
            image_opacity=0.07,
            image_fit=ft.ImageFit.CONTAIN,
            alignment=ft.alignment.center
        )

    def render():
        page.controls.clear()
        
        # NATIVE APP BAR
        page.appbar = ft.AppBar(
            title=ft.Text("Grace Lyrics" if st["v"]=="lyrics" else "Sacred Bible", weight="bold", color="white"),
            bgcolor="#1A237E", elevation=4
        )
        
        # NATIVE NAV BAR
        page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.MUSIC_NOTE, label="Lyrics"),
                ft.NavigationBarDestination(icon=ft.Icons.MENU_BOOK, label="Bible"),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings"),
            ],
            selected_index=0 if st["v"]=="lyrics" else 1 if st["v"]=="bible" else 2,
            on_change=lambda e: (st.update({"v": ["lyrics", "bible", "settings"][e.control.selected_index]}), render())
        )

        if st["v"] == "lyrics":
            body = ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.TextField(hint_text="Search lyrics...", prefix_icon=ft.Icons.SEARCH, bgcolor="white", border_radius=10, on_change=lambda e: (st.update({"q": e.control.value}), render())),
                        ft.Row([
                            ft.ElevatedButton("TAMIL", on_click=lambda _: (st.update({"l": "tamil"}), render()), expand=1),
                            ft.ElevatedButton("TELUGU", on_click=lambda _: (st.update({"l": "telugu"}), render()), expand=1),
                        ])
                    ]), padding=15
                ),
                ft.ListView([
                    ft.Container(
                        content=ft.ListTile(title=ft.Text("அசாத்தியங்கள் சாத்தியமே", weight="bold"), leading=ft.Icon(ft.Icons.MUSIC_VIDEO, color="#1A237E")),
                        bgcolor="white", border_radius=15, margin=ft.margin.symmetric(horizontal=15, vertical=5),
                        shadow=ft.BoxShadow(blur_radius=10, color="#00000011")
                    )
                ], expand=True)
            ], expand=True)
            page.add(wrap_with_logo(body))

        elif st["v"] == "bible":
            books = bible_eng.get_list()
            grid = ft.GridView(expand=True, runs_count=2, spacing=10, padding=15)
            for b in books:
                grid.controls.append(ft.Container(content=ft.Text(b["name"], weight="bold", text_align="center"), bgcolor="white", border_radius=12, alignment=ft.alignment.center, height=80, shadow=ft.BoxShadow(blur_radius=10, color="#00000011")))
            page.add(wrap_with_logo(grid))

        page.update()

    render()

ft.app(target=main)
