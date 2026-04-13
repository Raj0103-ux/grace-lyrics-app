import flet as ft
import json
import urllib.request
import threading
import os

# ===================== CONFIGURATION =====================
CLOUD_API_URL = "https://firestore.googleapis.com/v1/projects/grace-lyrics-545a1/databases/(default)/documents/songs"
DB_PATH = "songs.json"

# ===================== DATA MODELS & LOGIC =====================
class BibleManager:
    def __init__(self):
        self.books_tamil = ["ஆதியாகமம்", "யாத்திராகமம்", "லேவியராகமம்", "எண்ணாகமம்", "உபாகமம்", "யோசுவா", "நியாயாதிபதிகள்", "ரூத்", "1 சாமுவேல்", "2 சாமுவேல்", "1 ராஜாக்கள்", "2 ராஜாக்கள்", "1 நாளாகமம்", "2 நாளாகமம்", "எஸ்றா", "நெகேமியா", "எஸ்தர்", "யோபு", "சங்கீதம்", "நீதிமொழிகள்", "பிரசங்கி", "உன்னதப்பாட்டு", "ஏசாயா", "எரேமியா", "புலம்பல்", "எசேக்கியேல்", "தானியேல்", "ஓசியா", "யோவேல்", "ஆமோస్", "ஒபதியా", "యోనా", "మీకా", "నహూము", "హబక్కూకు", "జెఫన్యా", "హగ్గయి", "జెకర్యా", "మలాకీ", "మత్తయి", "మార్కు", "లూకా", "యోహాను", "అపొస్తలుల కార్యములు", "రోమీయులకు", "1 కొరింథీయులకు", "2 కొరింథీయులకు", "గలతీయులకు", "ఎఫెసీయులకు", "ఫిలిప్పీయులకు", "కొలొస్సయులకు", "1 థెస్సలొనీకయులకు", "2 థెస్సలొనీకయులకు", "1 తిమోతికి", "2 తిమోతికి", "తీతుకు", "ఫిలేమోనుకు", "హెబ్రీయులకు", "యాకోబు", "1 పేతురు", "2 పేతురు", "1 యోహాను", "2 యోహాను", "3 యోహాను", "యూదా", "ప్రకటన గ్రంథము"]
        self.books_telugu = ["ఆదికాండము", "నిర్గమకాండము", "లేవీయకాండము", "సంఖ్యాకాండము", "ద్వితీయోపదేశకాండము", "యెహోషువ", "న్యాయాధిపతులు", "రూతు", "1 సమూయేలు", "2 సమూయేలు", "1 రాజులు", "2 రాజులు", "1 దినవృత్తాంతములు", "2 దినవృత్తాంతములు", "ఎజ్రా", "నెహెమ్యా", "ఎస్తేరు", "యోబు", "కీర్తనల గ్రంథము", "సామెతలు", "ప్రసంగి", "పరమగీతము", "యెషయా", "యిర్మీయా", "విలాపవాక్యములు", "యెహెజ్కేలు", "దానియేలు", "హోషేయ", "యోవేలు", "ఆమోసు", "ఓబద్యా", "యోనా", "మీకా", "నహూము", "హబక్కూకు", "జెఫన్యా", "హగ్గయి", "జెకర్యా", "మలాకీ", "మత్తయి", "మార్కు", "లూకా", "యోహాను", "అపొస్తలుల కార్యములు", "రోమీయులకు", "1 కొరింథీయులకు", "2 కొరింథీయులకు", "గలతీయులకు", "ఎఫెసీయులకు", "ఫిలిప్పీయులకు", "కొలొస్సయులకు", "1 థెస్సలొనీకయులకు", "2 థెస్సలొనీకయులకు", "1 తిమోతికి", "2 తిమోతికి", "తీతుకు", "ఫిలేమోనుకు", "హెబ్రీయులకు", "యాకోబు", "1 పేతురు", "2 పేతురు", "1 యోహాను", "2 యోహాను", "3 యోహాను", "యూదా", "ప్రకటన గ్రంథము"]
        self.chapt_counts = [50, 40, 27, 36, 34, 24, 21, 4, 31, 24, 22, 25, 29, 36, 10, 13, 10, 42, 150, 31, 12, 8, 66, 52, 5, 48, 12, 14, 3, 9, 1, 4, 7, 3, 3, 3, 2, 14, 4, 28, 16, 24, 21, 28, 16, 16, 13, 6, 6, 4, 4, 5, 3, 6, 4, 3, 1, 13, 5, 5, 3, 5, 1, 1, 1, 22]

    def get_list(self, lang):
        names = self.books_tamil if lang == "tamil" else self.books_telugu
        return [{"name": n, "chapters": self.chapt_counts[i], "id": i+1} for i, n in enumerate(names)]

    def get_verses(self, lang, book_name, chapter):
        # High quality starters for key books
        v_data = {
            "tamil": {"ஆதியா": "ஆதியிலே தேவன் வானத்தையும் பூமியையும் சிருஷ்டித்தார்.", "யோவா": "தேவன் தம்முடைய ஒரேபேறான குமாரனை விசுவாசிக்கிறவன் எவனோ அவன் கெட்டுப்போகாமல் நித்தியஜீவனை அடைந்து கொள்ளும்படிக்கு, அவரைத் தந்தருளி, இவ்வளவாய் உலகத்தில் அன்புகூர்ந்தார்.", "சங்கீ": "கர்த்தர் என் மேய்ப்பராயிருக்கிறார்; நான் தாழ்ச்சியடையேன்."},
            "telugu": {"ఆది": "ఆదియందు దేవుడు భూమ్యాకాశములను సృజించెను.", "యోహాను": "దేవుడు లోకమును ఎంతో ప్రేమించెను; ఆయన తన అద్వితీయకుమారునిగా పుట్టిన వానియందు విశ్వాసముంచు ప్రతివాడును నశింపక నిత్యజీవము పొందునట్లు ఆయనను అనుగ్రహించెను."}
        }
        l_key = "tamil" if lang == "tamil" else "telugu"
        content = ""
        for k, text in v_data[l_key].items():
            if k in book_name: content += f"1. {text}\n"
        if len(content) < 10: content += f"Viewing {book_name} Chapter {chapter}.\n\n1. In the beginning was the Word, and the Word was with God."
        return content

class SongManager:
    def __init__(self):
        self.songs = []

    def load_local(self):
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f: self.songs = json.load(f)
            except: pass
        if not self.songs: 
            self.songs = [{"id": "s1", "title": "அசாத்தியங்கள் சாத்தியமே", "language": "tamil", "lyrics": "அசாத்தியங்கள் சாத்தியமே\nஉம்மால் எல்லாம் கூடும்", "is_favorite": True}]

    def save_local(self):
        try:
            with open(DB_PATH, "w", encoding="utf-8") as f: json.dump(self.songs, f, ensure_ascii=False, indent=2)
        except: pass

# ===================== STABLE UI =====================
bible_eng = BibleManager()
song_eng = SongManager()
song_eng.load_local()

def main(page: ft.Page):
    page.title = "GGGM Super App"
    page.padding = 0
    page.bgcolor = "#0F0F1A"
    # REMOVED WEB FONTS TO FIX BLACK SCREEN
    page.theme = ft.Theme(use_material3=True)

    # State
    state = {"v": "lyrics", "l": "tamil", "b": "tamil", "q": "", "sz": 22}

    def get_bg():
        return ft.Stack([
            ft.Container(expand=True, bgcolor="#0F0F1A"),
            ft.Container(width=400, height=400, left=-150, top=-150, bgcolor="#3143A3", border_radius=200, blur=ft.Blur(60, 60), opacity=0.3),
            ft.Container(width=300, height=300, right=-100, bottom=-100, bgcolor="#6A1B9A", border_radius=150, blur=ft.Blur(40, 40), opacity=0.2),
        ])

    def build_nav():
        def nav_btn(icon, label, target):
            active = state["v"] == target
            return ft.Container(
                content=ft.Column([ft.Icon(icon, color="white" if active else "white54", size=24), ft.Text(label, color="white" if active else "white54", size=10, weight="bold")], alignment="center", spacing=2),
                on_click=lambda _: (state.update({"v": target}), render()), expand=True
            )
        return ft.Container(
            content=ft.Row([nav_btn(ft.Icons.MUSIC_NOTE, "Lyrics", "lyrics"), nav_btn(ft.Icons.MENU_BOOK, "Bible", "bible"), nav_btn(ft.Icons.SETTINGS, "Settings", "settings")], alignment="center"),
            height=70, bgcolor="#00000044", blur=ft.Blur(10, 10), border=ft.border.only(top=ft.border.BorderSide(1, "#ffffff11")),
            padding=ft.Padding(0, 0, 0, 10)
        )

    # --- CONTENT RENDERERS ---
    def render_lyrics():
        songs = [s for s in song_eng.songs if s["language"] == state["l"] and state["q"].lower() in s["title"].lower()]
        return ft.Column([
            ft.Container(content=ft.Column([
                ft.Row([ft.Text("Grace Lyrics", size=28, weight="bold", color="white")]),
                ft.TextField(hint_text="Search lyrics...", prefix_icon=ft.Icons.SEARCH, border_radius=15, bgcolor="#ffffff10", color="white", on_change=lambda e: (state.update({"q": e.control.value}), render()), content_padding=15)
            ]), padding=ft.Padding(20, 50, 20, 10)),
            ft.Row([ft.ElevatedButton("Tamil", expand=1, on_click=lambda _: (state.update({"l": "tamil"}), render())), ft.ElevatedButton("Telugu", expand=1, on_click=lambda _: (state.update({"l": "telugu"}), render()))], padding=10),
            ft.Column([ft.Container(content=ft.ListTile(title=ft.Text(s["title"], color="white", weight="bold"), on_click=lambda e, sid=s["id"]: show_lyrics_detail(sid)), bgcolor="#ffffff08", border_radius=15, margin=ft.margin.symmetric(horizontal=15)) for s in songs], scroll="auto", expand=True)
        ], expand=True)

    def show_lyrics_detail(sid):
        s = next(x for x in song_eng.songs if x["id"] == sid)
        page.controls.clear()
        page.add(ft.Stack([get_bg(), ft.Column([
            ft.Container(content=ft.Row([ft.IconButton(ft.Icons.ARROW_BACK_IOS, icon_color="white", on_click=lambda _: render()), ft.Text(s["title"], color="white", weight="bold", size=18, expand=1)]), bgcolor="#3F51B544", padding=ft.Padding(10, 50, 10, 10)),
            ft.Container(content=ft.Column([ft.Text(s["lyrics"], size=state["sz"], color="white", line_height=1.4)], scroll="auto"), expand=True, padding=30, bgcolor="#00000022", blur=ft.Blur(10, 10))
        ], expand=True)]))
        page.update()

    def render_bible():
        books = bible_eng.get_list(state["b"])
        grid = ft.GridView(expand=True, runs_count=2, spacing=15, padding=20)
        for b in books:
            grid.controls.append(ft.Container(content=ft.Column([ft.Icon(ft.Icons.BOOKMARK, color="white70"), ft.Text(b["name"], color="white", weight="bold", size=14)], alignment="center"), bgcolor="#ffffff08", border_radius=15, on_click=lambda e, bk=b: show_chapters(bk)))
        return ft.Column([ft.Container(content=ft.Text("Bible", size=28, color="white", weight="bold"), padding=ft.Padding(20, 50, 20, 10)), grid], expand=True)

    def show_chapters(book):
        page.controls.clear()
        grid = ft.GridView(expand=True, runs_count=5, spacing=10, padding=20)
        for i in range(1, book["chapters"]+1):
            grid.controls.append(ft.Container(content=ft.Text(str(i), weight="bold", color="white"), bgcolor="#ffffff10", border_radius=12, alignment=ft.alignment.center, on_click=lambda e, c=i: show_bible_reader(book, c)))
        page.add(ft.Stack([get_bg(), ft.Column([ft.Container(content=ft.Row([ft.IconButton(ft.Icons.ARROW_BACK_IOS, icon_color="white", on_click=lambda _: render()), ft.Text(book["name"], color="white", weight="bold", size=22)]), bgcolor="#3F51B544", padding=ft.Padding(15, 50, 15, 15)), grid], expand=True)]))
        page.update()

    def show_bible_reader(book, ch):
        verses = bible_eng.get_verses(state["b"], book["name"], ch)
        page.controls.clear()
        jump = ft.Container(content=ft.Row([ft.Container(content=ft.Text(str(i), color="white"), width=45, height=45, bgcolor="#ffffff22" if i==ch else "transparent", border_radius=10, alignment=ft.alignment.center, on_click=lambda e, c=i: show_bible_reader(book, c)) for i in range(1, book["chapters"]+1)], scroll="auto"), padding=10, bgcolor="#00000044")
        page.add(ft.Stack([get_bg(), ft.Column([
            ft.Container(content=ft.Row([ft.IconButton(ft.Icons.ARROW_BACK_IOS, icon_color="white", on_click=lambda _: show_chapters(book)), ft.Text(f"{book['name']} {ch}", color="white", weight="bold", size=18)]), bgcolor="#3F51B544", padding=ft.Padding(10, 50, 10, 10)),
            ft.Container(content=ft.Column([ft.Text(verses, size=state["sz"], color="white", line_height=1.5)], scroll="auto"), expand=True, padding=30, bgcolor="#00000022", blur=ft.Blur(10, 10)),
            jump
        ], expand=True)]))
        page.update()

    def render_settings():
        return ft.Column([ft.Container(content=ft.Text("Settings", size=28, color="white", weight="bold"), padding=ft.Padding(20, 50, 20, 10)), ft.Container(content=ft.ListTile(title=ft.Text("Version v1.0.8", color="white"), leading=ft.Icon(ft.Icons.INFO_OUTLINE, color="white")), margin=20, bgcolor="#ffffff08", border_radius=15)], expand=True)

    def render():
        view = {"lyrics": render_lyrics, "bible": render_bible, "settings": render_settings}[state["v"]]()
        page.controls.clear()
        page.add(ft.Stack([get_bg(), ft.Column([view, build_nav()], spacing=0, expand=True)]))
        page.update()

    render()

ft.app(target=main)
