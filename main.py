import flet as ft
import json
import urllib.request
import threading
import os

# ===================== CONFIGURATION =====================
CLOUD_API_URL = "https://firestore.googleapis.com/v1/projects/grace-lyrics-545a1/databases/(default)/documents/songs"
DB_PATH = "songs.json"

# ===================== BIBLE ENGINE =====================
class BibleManager:
    def __init__(self):
        self.books_tamil = ["ஆதியாகமம்", "யாத்திராகமம்", "லேவியராகமம்", "எண்ணாகமம்", "உபாகமம்", "யோசுவா", "நியாயாதிபதிகள்", "ரூத்", "1 சாமுவேல்", "2 சாமுவேல்", "1 ராஜாக்கள்", "2 ராஜாக்கள்", "1 நாளாகமம்", "2 நாளாகமம்", "எஸ்றா", "நெகேமியா", "எஸ்தர்", "யோபு", "சங்கீதம்", "நீதிமொழிகள்", "பிரசங்கி", "உன்னதப்பாட்டு", "ஏசாயா", "எரேமியா", "புலம்பல்", "எசேக்கியேல்", "தானியேல்", "ஓசியா", "யோவேல்", "ஆமோஸ்", "ஒபதியா", "யோனா", "மீகா", "நாகூம்", "ஆபகூக்", "செப்பனியா", "ஆகாய்", "சகரியா", "மல்கியா", "மத்தேயு", "மாற்கு", "லூக்கா", "யோவான்", "அப்போஸ்தலர்", "ரோமர்", "1 கொரிந்தியர்", "2 கொரிந்தியர்", "கலாத்தியர்", "எபேசியர்", "பிலிப்பியர்", "கொலோசெயர்", "1 தெசலோனிக்கேயர்", "2 தெசலோனிக்கேயர்", "1 தீமோத்தேயு", "2 தீமோத்தேயு", "தீத்து", "பிலேமோன்", "எபிரெயர்", "யாக்கோபு", "1 பேதுரு", "2 பேதுரு", "1 யோவான்", "2 யோவான்", "3 யோவான்", "யூதா", "வெளிப்படுத்தின விசேஷம்"]
        self.chapt_counts = [50, 40, 27, 36, 34, 24, 21, 4, 31, 24, 22, 25, 29, 36, 10, 13, 10, 42, 150, 31, 12, 8, 66, 52, 5, 48, 12, 14, 3, 9, 1, 4, 7, 3, 3, 3, 2, 14, 4, 28, 16, 24, 21, 28, 16, 16, 13, 6, 6, 4, 4, 5, 3, 6, 4, 3, 1, 13, 5, 5, 3, 5, 1, 1, 1, 22]

    def get_list(self):
        return [{"name": n, "chapters": self.chapt_counts[i], "id": i+1} for i, n in enumerate(self.books_tamil)]

    def get_verses(self, book_name, chapter):
        return f"{book_name} {chapter}\n\n1. ஆதியிலே தேவன் வானத்தையும் பூமியையும் சிருஷ்டித்தார்.\n2. பூமியானது ஒழுங்கின்மையும் வெறுமையுமாய் இருந்தது."

class SongManager:
    def __init__(self):
        self.songs = [{"id": "s1", "title": "அசாத்தியங்கள் சாத்தியமே", "language": "tamil", "lyrics": "அசாத்தியங்கள் சாத்தியமே\nஉம்மால் எல்லாம் கூடும்"}]

# ===================== CLEAN UI =====================
bible_eng = BibleManager()
song_eng = SongManager()

def main(page: ft.Page):
    page.title = "GGGM - Safe Edition"
    page.padding = 0
    # SOLID BG COLOR - NO STACK - NO BLUR - NO FONTS
    page.bgcolor = "#3F51B5"
    page.theme_mode = ft.ThemeMode.LIGHT

    state = {"tab": "lyrics", "q": ""}

    def nav_bar():
        return ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.MUSIC_NOTE, label="Lyrics"),
                ft.NavigationBarDestination(icon=ft.Icons.MENU_BOOK, label="Bible"),
                ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings"),
            ],
            selected_index=0 if state["tab"]=="lyrics" else 1 if state["tab"]=="bible" else 2,
            on_change=lambda e: switch_tab(e.control.selected_index),
            bgcolor="white"
        )

    def switch_tab(idx):
        state["tab"] = ["lyrics", "bible", "settings"][idx]
        render()

    def render_lyrics():
        songs = [s for s in song_eng.songs if state["q"].lower() in s["title"].lower()]
        return ft.View(
            "/",
            [
                ft.Container(content=ft.Column([
                    ft.Text("Grace Lyrics", size=24, color="white", weight="bold"),
                    ft.TextField(hint_text="Search lyrics...", bgcolor="white", border_radius=10, on_change=lambda e: (state.update({"q": e.control.value}), render()))
                ]), padding=20, bgcolor="#3F51B5"),
                ft.ListView([ft.ListTile(title=ft.Text(s["title"]), leading=ft.Icon(ft.Icons.MUSIC_VIDEO), on_click=lambda e, s=s: show_detail(s)) for s in songs], expand=True)
            ],
            navigation_bar=nav_bar()
        )

    def show_detail(s):
        page.views.clear()
        page.views.append(ft.View(
            "/detail",
            [
                ft.AppBar(title=ft.Text(s["title"]), bgcolor="#3F51B5", color="white", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render())),
                ft.Container(content=ft.Text(s["lyrics"], size=22), padding=30, expand=True, bgcolor="#FFF9E1", scroll="auto")
            ]
        ))
        page.update()

    def render_bible():
        books = bible_eng.get_list()
        grid = ft.GridView(expand=True, runs_count=2, spacing=10, padding=10)
        for b in books:
            grid.controls.append(ft.Container(content=ft.Text(b["name"], weight="bold", text_align="center"), bgcolor="white", border_radius=10, alignment=ft.alignment.center, height=80, on_click=lambda e, bk=b: show_bible_read(bk)))
        return ft.View(
            "/bible",
            [
                ft.Container(content=ft.Text("Sacred Bible", size=24, color="white", weight="bold"), padding=20, bgcolor="#3F51B5"),
                grid
            ],
            navigation_bar=nav_bar()
        )

    def show_bible_read(book):
        verses = bible_eng.get_verses(book["name"], 1)
        page.views.clear()
        page.views.append(ft.View(
            "/read",
            [
                ft.AppBar(title=ft.Text(book["name"]), bgcolor="#3F51B5", color="white", leading=ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: render())),
                ft.Container(content=ft.Text(verses, size=22), padding=30, expand=True, bgcolor="#FFF9E1", scroll="auto")
            ]
        ))
        page.update()

    def render():
        page.views.clear()
        if state["tab"] == "lyrics": page.views.append(render_lyrics())
        elif state["tab"] == "bible": page.views.append(render_bible())
        elif state["tab"] == "settings": 
            page.views.append(ft.View("/", [ft.AppBar(title=ft.Text("Settings")), ft.Text("Safe Mode active")], navigation_bar=nav_bar()))
        page.update()

    render()

ft.app(target=main)
