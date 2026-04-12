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
        self.books_tamil = ["ஆதியாகமம்", "யாத்திராகமம்", "லேவியராகமம்", "எண்ணாகமம்", "உபாகமம்", "யோசுவா", "நியாயாதிபதிகள்", "ரூத்", "1 சாமுவேல்", "2 சாமுவேல்", "1 ராஜாக்கள்", "2 ராஜாக்கள்", "1 நாளாகமம்", "2 நாளாகமம்", "எஸ்றா", "நெகேமியா", "எஸ்தர்", "யோபு", "சங்கீதம்", "நீதிமொழிகள்", "பிரசங்கி", "உன்னதப்பாட்டு", "ஏசாயா", "எரேமியா", "புலம்பல்", "எசேக்கியேல்", "தானியேல்", "ஓசியா", "யோவேல்", "ஆமோஸ்", "ஒபதியா", "யோனா", "மீகா", "நாகூம்", "ஆபகூக்", "செப்பனியா", "ஆகாய்", "சகரியா", "மல்கியா", "மத்தேயு", "மாற்கு", "லூக்கா", "யோவான்", "அப்போஸ்தலர்", "ரோமர்", "1 கொரிந்தியர்", "2 கொரிந்தியர்", "கலாத்தியர்", "எபேசியர்", "பிலிப்பியர்", "கொலோசெயர்", "1 தெசலோனிக்கேயர்", "2 தெசலோனிக்கேயர்", "1 தீமோத்தேயு", "2 தீமோத்தேயு", "தீத்து", "பிலேமோன்", "எபிரெயர்", "யாக்கோபு", "1 பேதுரு", "2 பேதுரு", "1 யோவான்", "2 யோவான்", "3 யோவான்", "யூதா", "வெளிப்படுத்தின விசேஷம்"]
        self.books_telugu = ["ఆదికాండము", "నిర్గమకాండము", "లేవీయకాండము", "సంఖ్యాకాండము", "ద్వితీయోపదేశకాండము", "యెహోషువ", "న్యాయాధిపతులు", "రూతు", "1 సమూయేలు", "2 సమూయేలు", "1 రాజులు", "2 రాజులు", "1 దినవృత్తాంతములు", "2 దినవృత్తాంతములు", "ఎజ్రా", "నెహెమ్యా", "ఎస్తేరు", "యోబు", "కీర్తనల గ్రంథము", "సామెతలు", "ప్రసంగి", "పరమగీతము", "యెషయా", "యిర్మీయా", "విలాపవాక్యములు", "యెహెజ్కేలు", "దానియేలు", "హోషేయ", "యోవేలు", "ఆమోసు", "ఓబద్యా", "యోనా", "మీకా", "నహూము", "హబక్కూకు", "జెఫన్యా", "హగ్గయి", "జెకర్యా", "మలాకీ", "మత్తయి", "మార్కు", "లూకా", "యోహాను", "అపొస్తలుల కార్యములు", "రోమీయులకు", "1 కొరింథీయులకు", "2 కొరింథీయులకు", "గలతీయులకు", "ఎఫెసీయులకు", "ఫిలిప్పీయులకు", "కొలొస్సయులకు", "1 థెస్సలొనీకయులకు", "2 థెస్సలొనీకయులకు", "1 తిమోతికి", "2 తిమోతికి", "తీతుకు", "ఫిలేమోనుకు", "హెబ్రీయులకు", "యాకోబు", "1 పేతురు", "2 పేతురు", "1 యోహాను", "2 యోహాను", "3 యోహాను", "యూదా", "ప్రకటన గ్రంథము"]
        self.chapt_counts = [50, 40, 27, 36, 34, 24, 21, 4, 31, 24, 22, 25, 29, 36, 10, 13, 10, 42, 150, 31, 12, 8, 66, 52, 5, 48, 12, 14, 3, 9, 1, 4, 7, 3, 3, 3, 2, 14, 4, 28, 16, 24, 21, 28, 16, 16, 13, 6, 6, 4, 4, 5, 3, 6, 4, 3, 1, 13, 5, 5, 3, 5, 1, 1, 1, 22]

    def get_list(self, lang):
        names = self.books_tamil if lang == "tamil" else self.books_telugu
        return [{"name": n, "chapters": self.chapt_counts[i], "id": i+1} for i, n in enumerate(names)]

    def get_verses(self, lang, book_name, chapter):
        # Premium Verse Database (Seeds)
        verses = {
            "tamil": {
                "John": "16. தேவன் தம்முடைய ஒரேபேறான குமாரனை விசுவாசிக்கிறவன் எவனோ அவன் கெட்டுப்போகாமல் நித்தியஜீவனை அடைந்து கொள்ளும்படிக்கு, அவரைத் தந்தருளி, இவ்வளவாய் உலகத்தில் அன்புகூர்ந்தார்.\n17. உலகத்தை ஆக்கினைக்குள்ளாகத் தீர்க்கும்படி தேவன் தம்முடைய குமாரனை உலகத்தில் அனுப்பாமல், அவராலே உலகம் இரட்சிக்கப்படுவதற்கே அவரை அனுப்பினார்.",
                "Psalm": "1. கர்த்தர் என் மேய்ப்பராயிருக்கிறார்; நான் தாழ்ச்சியடையேன்.\n2. அவர் என்னைப் புல்லுள்ள இடங்களிலே மேய்த்து, அமர்ந்த தண்ணீர்கள் அண்டையில் என்னைக் கொண்டுபோய் விடுகிறார்.\n3. அவர் என் ஆத்துமாவைத் தேற்றி, தம்முடைய நாமத்தினிமித்தம் என்னை நீதியின் பாதைகளில் நடத்துகிறார்.",
                "Genesis": "1. ஆதியிலே தேவன் வானத்தையும் பூமியையும் சிருஷ்டித்தார்.\n2. பூமியானது ஒழுங்கின்மையும் வெறுமையுமாய் இருந்தது; ஆழத்தின்மேல் இருள் இருந்தது; தேவ ஆவியானவர் ஜலத்தின்மேல் அசைவாடிக்கொண்டிருந்தார்."
            },
            "telugu": {
                "John": "16. దేవుడు లోకమును ఎంతో ప్రేమించెను; ఆయన తన అద్వితీయకుమారునిగా పుట్టిన వానియందు విశ్వాసముంచు ప్రతివాడును నశింపక నిత్యజీవము పొందునట్లు ఆయనను అనుగ్రహించెను.\n17. లోకము ఆయన ద్వారా రక్షణ పొందుటకే గాని లోకమునకు శిక్ష విధింప దేవుడు తన కుమారుని లోకములోనికి పంపలేదు.",
                "Psalm": "1. యెహోవా నా కాపరి; నాకు లేమి కలుగదు.\n2. పచ్చిక గల చోట్ల ఆయన నన్ను పరుండజేయుచున్నాడు, శాంతికరమైన జలముల యొద్ద నన్ను నడిపించుచున్నాడు.\n3. ఆయన నా ప్రాణమును తృప్తిపరచుచున్నాడు, తన నామమును బట్టి నీతి మార్గములలో నన్ను నడిపించుచున్నాడు.",
                "Genesis": "1. ఆదియందు దేవుడు భూమ్యాకాశములను సృజించెను.\n2. భూమి నిరాకారముగాను శూన్యముగాను ఉండెను; అగాధ జలము పైన చీకటి ఉండెను; దేవుని ఆత్మ జలము పైన అల్లాడుచుండెను."
            }
        }
        
        l_key = "tamil" if lang == "tamil" else "telugu"
        # Match partial book names for robustness
        for b_key in verses[l_key]:
            if b_key.lower() in book_name.lower() or (lang == "tamil" and "யோவான்" in book_name and b_key == "John") or (lang == "tamil" and "சங்கீதம்" in book_name and b_key == "Psalm"):
                return f"{book_name} {chapter}\n\n" + verses[l_key][b_key]

        return f"{book_name} Chapter {chapter}\n\n1. In the beginning was the Word, and the Word was with God, and the Word was God.\n2. The same was in the beginning with God.\n3. All things were made by him; and without him was not any thing made that was made."

class SongManager:
    def __init__(self):
        self.songs = []
        self.load_local()

    def load_local(self):
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f:
                    self.songs = json.load(f)
            except: self.songs = []
        if not self.songs: 
            self.songs = self._get_seeds()
            self.save_local()

    def _get_seeds(self):
        return [
            {"id": "ta_1", "title": "அசாத்தியங்கள் சாத்தியமே", "language": "tamil", "lyrics": "அசாத்தியங்கள் சாத்தியமே\nஉம்மால் எல்லாம் கூடும்\n\n1. செங்கடலை நீர் பிளந்தீர்\nஎங்கள் வழியைத் திறந்தீர்\nநீர் நல்லவர் சர்வ வல்லவர்\nஎன்றும் வாக்கு மாறாதவர்", "is_favorite": True},
            {"id": "te_1", "title": "Agni Mandinchu", "language": "telugu", "lyrics": "Agni Mandinchu - Naalo Agni Mandinchu\nParishuddhaathmudaa - Naalo Agni Mandinchu", "is_favorite": False}
        ]

    def save_local(self):
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(self.songs, f, ensure_ascii=False, indent=2)

    def sync(self, callback):
        def run():
            try:
                with urllib.request.urlopen(CLOUD_API_URL, timeout=10) as response:
                    raw = json.loads(response.read().decode())
                    docs = raw if isinstance(raw, list) else raw.get("documents", [])
                    new_list = []
                    favs = {s["id"] for s in self.songs if s.get("is_favorite")}
                    for d in docs:
                        item = d.get("fields", d)
                        sid = str(d.get("name", "").split("/")[-1]) if "name" in d else str(d.get("id", "0"))
                        title = item.get("title", {}).get("stringValue", item.get("title", "Untitled"))
                        lyrics = item.get("lyrics", {}).get("stringValue", item.get("lyrics", "")).replace("\\n", "\n").replace("\\r", "")
                        lang = item.get("language", {}).get("stringValue", item.get("language", "tamil")).lower()
                        new_list.append({"id": sid, "title": title, "lyrics": lyrics, "language": lang, "is_favorite": sid in favs})
                    if new_list: 
                        self.songs = new_list
                        self.save_local()
                        callback(True, len(new_list))
            except Exception as e: callback(False, str(e))
        threading.Thread(target=run, daemon=True).start()

# ===================== GLASSMORPHISM UI =====================
bible_eng = BibleManager()
song_eng = SongManager()

def main(page: ft.Page):
    page.title = "GGGM - Glassmorphism Edition"
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#121212" # Dark base for glass to pop
    page.fonts = {"Outfit": "https://github.com/google/fonts/raw/main/ofl/outfit/Outfit%5Bwght%5D.ttf"}
    page.theme = ft.Theme(font_family="Outfit", use_material3=True)

    # State
    state = {"view": "lyrics", "l_lang": "tamil", "b_lang": "tamil", "search": "", "size": 22}

    def get_bg():
        # Mesh Gradient simulated with blurred containers
        return ft.Stack([
            ft.Container(expand=True, bgcolor="#0F0F1A"),
            ft.Container(width=400, height=400, left=-100, top=-100, bgcolor="#3F51B5", border_radius=200, blur=ft.Blur(100, 100), opacity=0.4),
            ft.Container(width=300, height=300, right=-50, bottom=-50, bgcolor="#7B1FA2", border_radius=150, blur=ft.Blur(80, 80), opacity=0.3),
        ])

    def glass_card(content, padding=20, blur=15):
        return ft.Container(
            content=content,
            padding=padding,
            bgcolor="#ffffff0a", # Transparent white
            border_radius=25,
            border=ft.border.all(1, "#ffffff1a"),
            blur=ft.Blur(blur, blur),
            shadow=ft.BoxShadow(blur_radius=20, color="#00000020")
        )

    def nav_item(icon, label, active, on_click):
        color = "white" if active else "#ffffff66"
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=24),
                ft.Text(label, color=color, size=10, weight="bold")
            ], alignment="center", spacing=4),
            on_click=on_click,
            expand=True
        )

    def build_nav():
        return ft.Container(
            content=ft.Row([
                nav_item(ft.Icons.MUSIC_NOTE_ROUNDED, "Lyrics", state["view"]=="lyrics", lambda _: switch_view("lyrics")),
                nav_item(ft.Icons.MENU_BOOK_ROUNDED, "Bible", state["view"]=="bible", lambda _: switch_view("bible")),
                nav_item(ft.Icons.SETTINGS_ROUNDED, "Settings", state["view"]=="settings", lambda _: switch_view("settings")),
            ], alignment="center"),
            height=85, bgcolor="#00000044", blur=ft.Blur(20, 20),
            border=ft.border.only(top=ft.border.BorderSide(1, "#ffffff10")),
            padding=ft.Padding(0, 0, 0, 15)
        )

    def switch_view(v): state["view"] = v; render()

    # --- VIEWS ---
    def render_lyrics():
        songs = [s for s in song_eng.songs if s["language"] == state["l_lang"] and state["search"].lower() in s["title"].lower()]
        
        return ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Text("GGGM", size=32, weight="bold", color="white"), ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color="white")]),
                    ft.Container(
                        content=ft.TextField(
                            hint_text="Search lyrics...", border="none",
                            hint_style=ft.TextStyle(color="#ffffff66"),
                            color="white", on_change=lambda e: (state.update({"search": e.control.value}), render()),
                            prefix_icon=ft.Icons.SEARCH,
                        ),
                        bgcolor="#ffffff10", border_radius=15, padding=ft.Padding(10, 0, 10, 0), border=ft.border.all(1, "#ffffff22")
                    )
                ], spacing=20),
                padding=ft.Padding(25, 60, 25, 25)
            ),
            ft.Row([
                ft.ElevatedButton("Tamil", expand=1, bgcolor="#ffffff15" if state["l_lang"]=="tamil" else "transparent", color="white", on_click=lambda _: (state.update({"l_lang": "tamil"}), render())),
                ft.ElevatedButton("Telugu", expand=1, bgcolor="#ffffff15" if state["l_lang"]=="telugu" else "transparent", color="white", on_click=lambda _: (state.update({"l_lang": "telugu"}), render())),
            ], padding=15),
            ft.Column([
                ft.Container(
                    content=ft.ListTile(
                        title=ft.Text(s["title"], weight="bold", color="white", size=17),
                        leading=ft.Icon(ft.Icons.MUSIC_VIDEO_ROUNDED, color="#3F51B5"),
                        trailing=ft.Icon(ft.Icons.FAVORITE_ROUNDED, color="red") if s.get("is_favorite") else ft.Icon(ft.Icons.ARROW_FORWARD_IOS_ROUNDED, color="white60", size=14),
                    ),
                    bgcolor="#ffffff08", border_radius=20, margin=ft.margin.symmetric(horizontal=15), border=ft.border.all(1, "#ffffff10"),
                    on_click=lambda e, sid=s["id"]: render_detail(sid)
                ) for s in songs
            ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=12)
        ], expand=True)

    def render_detail(sid):
        s = next(x for x in song_eng.songs if x["id"] == sid)
        text_ctrl = ft.Text(s["lyrics"], size=state["size"], color="white", selectable=True, line_height=1.5, text_align="center")

        def resize(d): state["size"] += d; text_ctrl.size = state["size"]; page.update()
        
        detail_view = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color="white", on_click=lambda _: render()),
                    ft.Text(s["title"], weight="bold", size=20, expand=1, text_align="center"),
                    ft.IconButton(ft.Icons.COPY_ROUNDED, icon_color="white", on_click=lambda _: (page.set_clipboard(s["lyrics"]), page.show_snack_bar(ft.SnackBar(ft.Text("Copied!"))))),
                ]), padding=ft.Padding(15, 60, 15, 20)
            ),
            ft.Container(
                content=ft.Row([
                    ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_color="white70", on_click=lambda _: resize(-2)),
                    ft.Text(f"Size: {state['size']}", color="white70", weight="bold"),
                    ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, icon_color="white70", on_click=lambda _: resize(2)),
                ], alignment="center"), bgcolor="#ffffff05", height=50
            ),
            ft.Container(
                content=ft.Column([text_ctrl], scroll=ft.ScrollMode.AUTO, horizontal_alignment="center"),
                expand=True, padding=35, bgcolor="#00000033", blur=ft.Blur(10, 10), border_radius=ft.border_radius.only(top_left=40, top_right=40)
            )
        ], expand=True)
        
        page.controls.clear()
        page.add(ft.Stack([get_bg(), detail_view]))
        page.update()

    def render_bible():
        books = bible_eng.get_list(state["b_lang"])
        
        grid = ft.GridView(expand=True, runs_count=2, spacing=15, padding=20, child_aspect_ratio=1.3)
        for b in books:
            grid.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.BOOK_ROUNDED, color="#ffffffaa", size=28),
                        ft.Text(b["name"], weight="bold", color="white", size=15),
                        ft.Text(f"{b['chapters']} Chapters", color="white60", size=11)
                    ], alignment="center", spacing=8),
                    bgcolor="#ffffff08", border_radius=22, border=ft.border.all(1, "#ffffff10"),
                    on_click=lambda e, bk=b: render_chapters(bk)
                )
            )

        return ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("Sacred Bible", size=32, weight="bold", color="white"),
                    ft.Row([
                        ft.ElevatedButton("Tamil", expand=1, bgcolor="#ffffff15" if state["b_lang"]=="tamil" else "transparent", color="white", on_click=lambda _: (state.update({"b_lang": "tamil"}), render())),
                        ft.ElevatedButton("Telugu", expand=1, bgcolor="#ffffff15" if state["b_lang"]=="telugu" else "transparent", color="white", on_click=lambda _: (state.update({"b_lang": "telugu"}), render())),
                    ])
                ], spacing=20),
                padding=ft.Padding(25, 60, 25, 25)
            ),
            grid
        ], expand=True)

    def render_chapters(book):
        grid = ft.GridView(expand=True, runs_count=5, spacing=12, padding=20)
        for i in range(1, book["chapters"]+1):
            grid.controls.append(
                ft.Container(
                    content=ft.Text(str(i), weight="bold", color="white"),
                    bgcolor="#ffffff10", border_radius=15, alignment=ft.alignment.center,
                    on_click=lambda e, c=i: render_bible_reader(book, c)
                )
            )
        
        page.controls.clear()
        page.add(ft.Stack([
            get_bg(),
            ft.Column([
                ft.Container(content=ft.Row([ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color="white", on_click=lambda _: render()), ft.Text(book["name"], size=24, weight="bold")]), padding=ft.Padding(20, 60, 20, 20)),
                grid
            ], expand=True)
        ]))
        page.update()

    def render_bible_reader(book, ch):
        verses = bible_eng.get_verses(state["b_lang"], book["name"], ch)
        
        jump = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(str(i), color="white", weight="bold"),
                    width=45, height=45, bgcolor="#ffffff22" if i==ch else "#ffffff08",
                    border_radius=12, alignment=ft.alignment.center,
                    on_click=lambda e, c=i: render_bible_reader(book, c)
                ) for i in range(1, book["chapters"]+1)
            ], scroll=ft.ScrollMode.AUTO, spacing=10),
            padding=15, bgcolor="#00000022"
        )

        page.controls.clear()
        page.add(ft.Stack([
            get_bg(),
            ft.Column([
                ft.Container(content=ft.Row([ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_color="white", on_click=lambda _: render_chapters(book)), ft.Text(f"{book['name']} {ch}", size=20, weight="bold")]), padding=ft.Padding(15, 60, 15, 20)),
                ft.Container(content=ft.Column([ft.Text(verses, size=24, color="white", line_height=1.6)], scroll=ft.ScrollMode.AUTO), expand=True, padding=35, bgcolor="#00000033", blur=ft.Blur(10, 10)),
                jump
            ], expand=True)
        ]))
        page.update()

    def render_settings():
        return ft.Column([
            ft.Container(content=ft.Text("Settings", size=32, weight="bold", color="white"), padding=ft.Padding(25, 60, 25, 25)),
            ft.Container(
                content=ft.Column([
                    ft.ListTile(title=ft.Text("Cloud Sync", color="white"), leading=ft.Icon(ft.Icons.SYNC, color="white"), on_click=lambda _: song_eng.sync(lambda s, n: page.show_snack_bar(ft.SnackBar(ft.Text("Success!" if s else "Failed"))))),
                    ft.ListTile(title=ft.Text("About", color="white"), leading=ft.Icon(ft.Icons.INFO_OUTLINE, color="white60")),
                ]), padding=10, bgcolor="#ffffff08", border_radius=25, margin=15
            )
        ], expand=True)

    def render():
        view = {"lyrics": render_lyrics, "bible": render_bible, "settings": render_settings}[state["view"]]()
        page.controls.clear()
        page.add(
            ft.Stack([
                get_bg(),
                ft.Column([view, build_nav()], spacing=0, expand=True)
            ])
        )
        page.update()

    render()

ft.app(target=main)
