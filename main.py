import flet as ft
import json
import os
import time
import urllib.request

# ============= DATA STORAGE (pure Python, zero dependencies) =============
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "songs.json")

def load_songs():
    try:
        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_songs(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass

def seed_if_empty():
    data = load_songs()
    if len(data) == 0:
        data = [
            {"id": "ta_172", "title": "கர்த்தாவே தேவர்களில்", "language": "tamil", "number": "172", "is_favorite": False,
             "lyrics": "கர்த்தாவே தேவர்களில் உமக்கொப்பனவர் யார்?\nவானத்திலும் பூமியிலும் உமக்கொப்பானவர் யார்?\n\n1. செங்கடலை நீர் பிளந்து\nஉந்தன் ஜனங்களை நடத்திச் சென்றீர்\nநீர் நல்லவர் சர்வ வல்லவர்\nஎன்றும் வாக்கு மாறாதவர் (2)"},
            {"id": "te_1", "title": "అగ్ని మండించు - Agni Mandinchu", "language": "telugu", "number": "", "is_favorite": False,
             "lyrics": "అగ్ని మండించు – నాలో అగ్ని మండించు (2)\nపరిశుద్ధాత్ముడా – నాలో అగ్ని మండించు (2)\n\nAgni Mandinchu – Naalo Agni Mandinchu (2)\nParishuddhaathmudaa – Naalo Agni Mandinchu (2)"}
        ]
        save_songs(data)
    return data

FIRESTORE_URL = "https://firestore.googleapis.com/v1/projects/grace-lyrics-admin/databases/(default)/documents/songs"

def cloud_sync():
    count = 0
    try:
        req = urllib.request.Request(FIRESTORE_URL)
        with urllib.request.urlopen(req, timeout=10) as r:
            docs = json.loads(r.read().decode("utf-8")).get("documents", [])
            data = load_songs()
            existing_ids = {s["id"] for s in data}
            for doc in docs:
                sid = doc.get("name", "").split("/")[-1]
                fl = doc.get("fields", {})
                song = {"id": sid, "title": fl.get("title", {}).get("stringValue", ""), "language": fl.get("language", {}).get("stringValue", ""), "lyrics": fl.get("lyrics", {}).get("stringValue", "").replace("\\n", "\n"), "number": fl.get("number", {}).get("stringValue", ""), "is_favorite": False}
                if sid in existing_ids:
                    for i, s in enumerate(data):
                        if s["id"] == sid:
                            song["is_favorite"] = s.get("is_favorite", False)
                            data[i] = song
                            break
                else:
                    data.append(song)
                count += 1
            save_songs(data)
    except Exception:
        pass
    return count

# ============= MAIN APP =============
def main(page: ft.Page):
    page.title = "Grace Lyrics"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"

    try:
        all_songs = seed_if_empty()
    except Exception as e:
        page.add(ft.Text(f"Init error: {e}", color="red", selectable=True))
        return

    def get_songs(lang, query=""):
        data = load_songs()
        result = []
        for s in data:
            if s.get("language") == lang:
                if query and query.lower() not in s.get("title", "").lower():
                    continue
                result.append(s)
        return sorted(result, key=lambda x: x.get("title", ""))

    def go_song(e, song_id):
        page.session.set("song_id", song_id)
        show_song_page(song_id)

    def build_list(lang, query=""):
        songs = get_songs(lang, query)
        if not songs:
            return ft.Container(content=ft.Text(f"No {lang} songs yet. Sync from cloud.", color="grey"), alignment=ft.alignment.center, padding=30)
        lv = ft.ListView(expand=True, spacing=8, padding=10)
        for s in songs:
            lv.controls.append(
                ft.Card(content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.MUSIC_NOTE, color="grey"),
                    title=ft.Text(f"{s.get('number','')}. {s['title']}" if s.get("number") else s["title"], weight=ft.FontWeight.BOLD),
                    trailing=ft.Icon(ft.Icons.FAVORITE, color="red") if s.get("is_favorite") else ft.Icon(ft.Icons.CHEVRON_RIGHT),
                    on_click=lambda e, sid=s["id"]: go_song(e, sid))))
        return lv

    # --- SEARCH STATE ---
    search_visible = {"val": False}
    search_query = {"val": ""}

    def on_search(e):
        search_query["val"] = e.control.value
        refresh_home()

    search_field = ft.TextField(hint_text="Search song title...", on_change=on_search, expand=True, border_color="transparent")
    search_bar = ft.Container(content=search_field, visible=False, padding=10)

    tamil_content = ft.Container(expand=True)
    telugu_content = ft.Container(expand=True)

    def refresh_home():
        tamil_content.content = build_list("tamil", search_query["val"])
        telugu_content.content = build_list("telugu", search_query["val"])
        page.update()

    def toggle_search(e):
        search_visible["val"] = not search_visible["val"]
        search_bar.visible = search_visible["val"]
        if not search_visible["val"]:
            search_query["val"] = ""
            search_field.value = ""
        refresh_home()

    tabs = ft.Tabs(selected_index=0, animation_duration=300, expand=1, tabs=[
        ft.Tab(text="Tamil", content=tamil_content),
        ft.Tab(text="Telugu", content=telugu_content)])

    def show_home():
        page.controls.clear()
        refresh_home()
        page.add(
            ft.AppBar(title=ft.Text("Grace Lyrics", weight=ft.FontWeight.BOLD), bgcolor="#202A44", center_title=True, actions=[
                ft.IconButton(ft.Icons.SEARCH, on_click=toggle_search),
                ft.IconButton(ft.Icons.SETTINGS, on_click=lambda e: show_admin())]),
            search_bar, tabs)
        page.update()

    def show_song_page(song_id):
        data = load_songs()
        song = None
        for s in data:
            if s["id"] == song_id:
                song = s
                break
        if not song:
            return

        font_size = {"val": 18}
        lyrics_text = ft.Text(song["lyrics"], size=font_size["val"], selectable=True)

        def inc(e):
            if font_size["val"] < 40:
                font_size["val"] += 2
                lyrics_text.size = font_size["val"]
                page.update()
        def dec(e):
            if font_size["val"] > 12:
                font_size["val"] -= 2
                lyrics_text.size = font_size["val"]
                page.update()
        def fav(e):
            data2 = load_songs()
            for s2 in data2:
                if s2["id"] == song_id:
                    s2["is_favorite"] = not s2.get("is_favorite", False)
                    break
            save_songs(data2)
            show_song_page(song_id)

        is_fav = song.get("is_favorite", False)
        page.controls.clear()
        page.add(
            ft.AppBar(title=ft.Text(song["title"], size=14), bgcolor="#202A44", leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_home()), actions=[
                ft.IconButton(ft.Icons.TEXT_DECREASE, on_click=dec),
                ft.IconButton(ft.Icons.TEXT_INCREASE, on_click=inc),
                ft.IconButton(ft.Icons.FAVORITE if is_fav else ft.Icons.FAVORITE_BORDER, icon_color="red" if is_fav else "grey", on_click=fav)]),
            ft.Container(content=ft.Column([
                ft.Text(song["title"], size=22, weight=ft.FontWeight.BOLD, color="#7B8DB8"),
                ft.Divider(), lyrics_text], scroll=ft.ScrollMode.AUTO), padding=20, expand=True))
        page.update()

    def show_admin():
        status = ft.Text("Ready.", color="green")
        def do_sync(e):
            status.value = "Syncing..."
            status.color = "blue"
            page.update()
            try:
                c = cloud_sync()
                status.value = f"Synced {c} songs!"
                status.color = "green"
            except Exception as ex:
                status.value = f"Error: {ex}"
                status.color = "red"
            page.update()

        page.controls.clear()
        page.add(
            ft.AppBar(title=ft.Text("Cloud Sync", size=16), bgcolor="#202A44", leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_home())),
            ft.Container(content=ft.Column([
                ft.Text("Download Songs from Cloud", size=22, weight=ft.FontWeight.BOLD),
                ft.Text("Tap sync to get the latest songs pushed by the admin."),
                ft.ElevatedButton("Sync Now", on_click=do_sync),
                status]), padding=20, expand=True))
        page.update()

    show_home()

ft.app(target=main)
