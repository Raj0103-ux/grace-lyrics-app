import flet as ft
import json
import os
import re
import sys
import threading
import time
import traceback
import urllib.error
import urllib.request


PROJECT_ID = "grace-lyrics-admin"
SONGS_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/songs"
USERS_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/users"
WHATSAPP_URL = "https://api.whatsapp.com/send?phone=918122003722"

TAMIL_BUCKETS = [
    "\u0B85", "\u0B86", "\u0B87", "\u0B88", "\u0B89", "\u0B8A",
    "\u0B8E", "\u0B8F", "\u0B90", "\u0B92", "\u0B93", "\u0B94",
    "\u0B95", "\u0B99", "\u0B9A", "\u0B9C", "\u0B9E", "\u0B9F",
    "\u0BA3", "\u0BA4", "\u0BA8", "\u0BAA", "\u0BAE", "\u0BAF",
    "\u0BB0", "\u0BB2", "\u0BB5", "\u0BB4", "\u0BB3", "\u0BB1",
    "\u0BA9", "\u0BB7", "\u0BB8", "\u0BB9", "#",
]
TELUGU_BUCKETS = [
    "\u0C05", "\u0C06", "\u0C07", "\u0C08", "\u0C09", "\u0C0A",
    "\u0C0B", "\u0C0E", "\u0C0F", "\u0C10", "\u0C12", "\u0C13",
    "\u0C14", "\u0C15", "\u0C16", "\u0C17", "\u0C18", "\u0C19",
    "\u0C1A", "\u0C1B", "\u0C1C", "\u0C1D", "\u0C1F", "\u0C20",
    "\u0C21", "\u0C22", "\u0C24", "\u0C25", "\u0C26", "\u0C27",
    "\u0C28", "\u0C2A", "\u0C2B", "\u0C2C", "\u0C2D", "\u0C2E",
    "\u0C2F", "\u0C30", "\u0C32", "\u0C35", "\u0C36", "\u0C37",
    "\u0C38", "\u0C39", "\u0C33", "\u0C15\u0C4D\u0C37", "#",
]
ENGLISH_BUCKETS = [chr(code) for code in range(ord("A"), ord("Z") + 1)] + ["#"]


def log(msg):
    print(f"[GGGM] {msg}", file=sys.stderr, flush=True)


class AppDataManager:
    def __init__(self):
        self.songs = []
        self.profile = {}
        self._songs_path = None
        self._profile_path = None

    def set_paths(self, data_dir):
        self._songs_path = os.path.join(data_dir, "songs.json")
        self._profile_path = os.path.join(data_dir, "profile.json")

    def load_songs(self):
        paths = []
        if self._songs_path:
            paths.append(self._songs_path)
        paths.extend(["assets/songs.json", "data/songs.json"])

        for path in paths:
            if not path or not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    self.songs = json.load(handle)
                log(f"Loaded {len(self.songs)} songs from {path}")
                if path != self._songs_path and self._songs_path:
                    self.save_songs()
                return
            except Exception as ex:
                log(f"Song load error ({path}): {ex}")

        self.songs = []
        log("No song database found.")

    def save_songs(self):
        if not self._songs_path:
            return
        try:
            os.makedirs(os.path.dirname(self._songs_path), exist_ok=True)
            with open(self._songs_path, "w", encoding="utf-8") as handle:
                json.dump(self.songs, handle, ensure_ascii=False)
            log(f"Saved {len(self.songs)} songs to {self._songs_path}")
        except Exception as ex:
            log(f"Song save error: {ex}")

    def load_profile(self):
        self.profile = {}
        if not self._profile_path or not os.path.exists(self._profile_path):
            return
        try:
            with open(self._profile_path, "r", encoding="utf-8") as handle:
                self.profile = json.load(handle)
            log("Loaded local profile.")
        except Exception as ex:
            log(f"Profile load error: {ex}")
            self.profile = {}

    def save_profile(self):
        if not self._profile_path:
            return
        try:
            os.makedirs(os.path.dirname(self._profile_path), exist_ok=True)
            with open(self._profile_path, "w", encoding="utf-8") as handle:
                json.dump(self.profile, handle, ensure_ascii=False)
            log("Saved local profile.")
        except Exception as ex:
            log(f"Profile save error: {ex}")

    def sync_songs_from_cloud(self):
        all_songs = []
        next_token = None

        while True:
            url = SONGS_BASE_URL + "?pageSize=300"
            if next_token:
                url += f"&pageToken={next_token}"

            with urllib.request.urlopen(url, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))

            for doc in data.get("documents", []):
                fields = doc.get("fields", {})
                raw_lyrics = fields.get("lyrics", fields.get("Lyric", {})).get("stringValue", "")
                all_songs.append(
                    {
                        "title": fields.get("title", fields.get("Title", {})).get("stringValue", "No Title").strip(),
                        "lyrics": raw_lyrics.replace("\\n", "\n").replace("\\r", "\n").replace("\r\n", "\n").strip(),
                        "language": fields.get("language", fields.get("Language", {})).get("stringValue", "tamil").lower().strip(),
                    }
                )

            next_token = data.get("nextPageToken")
            if not next_token:
                break

        return all_songs

    def sync_user_to_cloud(self, profile, first_login=False):
        mobile = re.sub(r"\D", "", profile.get("mobile", ""))
        if not mobile:
            return

        now = time.strftime("%Y-%m-%d %H:%M:%S")
        body = {
            "fields": {
                "name": {"stringValue": profile.get("name", "").strip()},
                "mobile": {"stringValue": mobile},
                "created_at": {"stringValue": profile.get("created_at", now)},
                "last_seen": {"stringValue": now},
            }
        }
        data = json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json"}

        if first_login:
            create_url = f"{USERS_BASE_URL}?documentId={mobile}"
            request = urllib.request.Request(create_url, data=data, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(request, timeout=20):
                    return
            except urllib.error.HTTPError as ex:
                if ex.code != 409:
                    raise

        update_url = f"{USERS_BASE_URL}/{mobile}"
        request = urllib.request.Request(update_url, data=data, headers=headers, method="PATCH")
        with urllib.request.urlopen(request, timeout=20):
            return


dm = AppDataManager()


def normalize_title_start(text):
    for char in (text or "").strip():
        if char.isalnum() or "\u0B80" <= char <= "\u0BFF" or "\u0C00" <= char <= "\u0C7F":
            return char
    return "#"


def get_title_variants(title):
    separators = [" - ", " | ", "/", "(", "["]
    variants = []
    seen = set()

    def add_variant(value):
        cleaned = (value or "").strip(" -|/()[]{}")
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            variants.append(cleaned)

    add_variant(title)
    for separator in separators:
        if separator in (title or ""):
            for piece in title.split(separator):
                add_variant(piece)
    return variants or [title or ""]


def contains_native_char(text, language):
    if language == "tamil":
        return any("\u0B80" <= char <= "\u0BFF" for char in text or "")
    if language == "telugu":
        return any("\u0C00" <= char <= "\u0C7F" for char in text or "")
    return False


def is_heading_line(text, language):
    lowered = (text or "").strip().lower()
    generic = {
        "tamil lyrics",
        "telugu lyrics",
        "english lyrics",
        "english transliteration",
        "translation",
        "transliteration",
        "chorus",
        "verse",
        "bridge",
    }
    if not lowered:
        return True
    stripped = lowered.strip("= -:_")
    if stripped in generic:
        return True
    if lowered.startswith("===") and lowered.endswith("==="):
        return True
    if stripped in {"(2)", "(3)", "(4)", "2", "3", "4"}:
        return True
    if "lyrics" in stripped and not contains_native_char(text, language):
        return True
    return False


def is_english_heading_line(text):
    lowered = (text or "").strip().lower().strip("= -:_")
    return lowered in {
        "english lyrics",
        "english transliteration",
        "transliteration",
        "translation",
        "english translation",
    }


def is_metadata_label(text):
    lowered = (text or "").strip().lower().strip("= -:_")
    if not lowered:
        return False
    if lowered.endswith(":"):
        return True
    direct = {
        "audio",
        "video",
        "track",
        "lyrics",
        "lyricist",
        "music",
        "composer",
        "singer",
        "singers",
        "album",
        "credits",
        "vocals",
        "tune",
        "male",
        "female",
        "duet",
        "songs of zion",
    }
    if lowered in direct:
        return True
    return any(token in lowered for token in ["lyricist", "lyrics by", "music by", "singer", "composer", "audio", "video"])


def is_credit_value_line(text):
    line = (text or "").strip()
    if not line or contains_native_char(line, "tamil") or contains_native_char(line, "telugu"):
        return False
    words = [word for word in line.replace("-", " ").split() if word]
    if not words or len(words) > 4:
        return False
    return all(word[:1].isupper() for word in words if word[:1].isalpha())


def get_native_browse_text(song):
    language = song.get("language", "").strip().lower()
    for variant in get_title_variants(song.get("title", "")):
        if contains_native_char(variant, language):
            return variant

    for raw_line in song.get("lyrics", "").replace("\r\n", "\n").split("\n"):
        line = raw_line.strip()
        if not line or is_heading_line(line, language):
            continue
        if contains_native_char(line, language):
            return line

    return song.get("title", "")


def get_english_browse_text(song):
    for variant in get_title_variants(song.get("title", "")):
        first = normalize_title_start(variant)
        if "A" <= first.upper() <= "Z":
            return variant

    lines = [raw.strip() for raw in song.get("lyrics", "").replace("\r\n", "\n").split("\n") if raw.strip()]
    in_english_section = False
    previous_was_metadata = False

    for line in lines:
        if is_english_heading_line(line):
            in_english_section = True
            previous_was_metadata = False
            continue
        if not in_english_section:
            continue
        if is_metadata_label(line):
            previous_was_metadata = True
            continue
        if previous_was_metadata and is_credit_value_line(line):
            previous_was_metadata = False
            continue
        previous_was_metadata = False
        first = normalize_title_start(line)
        if "A" <= first.upper() <= "Z":
            return line
        if contains_native_char(line, song.get("language", "").strip().lower()):
            break

    previous_was_metadata = False
    for line in lines:
        if is_heading_line(line, song.get("language", "").strip().lower()) or is_english_heading_line(line):
            previous_was_metadata = False
            continue
        if is_metadata_label(line):
            previous_was_metadata = True
            continue
        if previous_was_metadata and is_credit_value_line(line):
            previous_was_metadata = False
            continue
        previous_was_metadata = False
        first = normalize_title_start(line)
        if "A" <= first.upper() <= "Z":
            return line

    return song.get("title", "")


def get_display_title(song, mode):
    if mode == "english":
        return get_english_browse_text(song)
    return get_native_browse_text(song)


def get_display_preview(song, mode):
    language = song.get("language", "").strip().lower()
    title_line = get_display_title(song, mode).strip()
    lines = [raw.strip() for raw in song.get("lyrics", "").replace("\r\n", "\n").split("\n") if raw.strip()]

    if mode == "english":
        in_english_section = False
        for line in lines:
            if is_english_heading_line(line):
                in_english_section = True
                continue
            if not in_english_section:
                continue
            if line == title_line or is_metadata_label(line):
                continue
            if "A" <= normalize_title_start(line).upper() <= "Z":
                return line
            if contains_native_char(line, language):
                break
    else:
        for line in lines:
            if is_heading_line(line, language) or is_english_heading_line(line):
                continue
            if line == title_line:
                continue
            if contains_native_char(line, language):
                return line

    return ""


def classify_letter(char, language):
    if "A" <= char.upper() <= "Z":
        return char.upper()
    if language == "telugu" and char in TELUGU_BUCKETS:
        return char
    if language == "tamil" and char in TAMIL_BUCKETS:
        return char
    return "#"


def get_song_buckets(song, mode):
    language = song.get("language", "").strip().lower()
    source = get_display_title(song, mode)
    buckets = set()
    for variant in get_title_variants(source):
        buckets.add(classify_letter(normalize_title_start(variant), language))
    return buckets or {"#"}


def get_initials(name):
    parts = [part for part in (name or "").strip().split() if part]
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    compact = "".join(parts) if parts else "U"
    return compact[:3].upper()


def format_now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def main(page: ft.Page):
    try:
        page.assets_dir = "assets"
        page.title = "GGGM"
        page.bgcolor = "#F3F4F8"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0

        data_dir = os.environ.get("FLET_APP_STORAGE_DATA") or os.path.join(os.getcwd(), "data")
        os.makedirs(data_dir, exist_ok=True)
        dm.set_paths(data_dir)
        dm.load_songs()
        dm.load_profile()

        st = {
            "lang": "tamil",
            "font_size": 22,
            "selected_letter": None,
            "search_query": "",
            "search_open": False,
            "syncing": False,
            "alphabet_mode": {"tamil": "native", "telugu": "native"},
            "profile_syncing": False,
        }

        page.appbar = ft.AppBar(visible=False)
        page.scroll = ft.ScrollMode.AUTO

        def get_active_mode():
            return st["alphabet_mode"][st["lang"]]

        def get_letters_for_language():
            if get_active_mode() == "english":
                return ENGLISH_BUCKETS
            return TELUGU_BUCKETS if st["lang"] == "telugu" else TAMIL_BUCKETS

        def song_matches_query(song):
            query = st["search_query"].strip().lower()
            if not query:
                return True
            display_title = get_display_title(song, get_active_mode())
            return query in (display_title or "").lower()

        def build_avatar(size, clickable=False):
            image_path = dm.profile.get("image_path", "")
            if image_path and os.path.exists(image_path):
                content = ft.Image(src=image_path)
            else:
                content = ft.Text(
                    get_initials(dm.profile.get("name", "GGGM")),
                    size=max(14, int(size * 0.28)),
                    weight="bold",
                    color="white",
                )
            avatar = ft.Container(
                width=size,
                height=size,
                bgcolor="#22C55E" if image_path and os.path.exists(image_path) else "#1A237E",
                border_radius=size / 2,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                alignment=ft.alignment.Alignment(0, 0),
                content=content,
            )
            if clickable:
                avatar.on_click = lambda e: show_profile()
                avatar.ink = True
            return avatar

        def build_footer():
            if st["selected_letter"] or st["search_query"].strip():
                return ft.Container(visible=False, height=0)

            footer_text = (
                "கர்த்தருக்காக அன்பும் விசுவாசத்தோடும் உருவாக்கப்பட்டது."
                if st["lang"] == "tamil"
                else "ప్రభువుకై ప్రేమతో మరియు విశ్వాసంతో రూపొందించబడింది."
            )
            footer_name = "ஹானோக் A B" if st["lang"] == "tamil" else "హనోక్ A B"
            footer_font = 13 if st["lang"] == "tamil" else 15
            name_font = 16 if st["lang"] == "tamil" else 18

            return ft.Container(
                margin=ft.margin.only(left=12, right=12, bottom=10, top=6),
                padding=ft.padding.symmetric(horizontal=16, vertical=14),
                bgcolor="#FFFFFF",
                border_radius=22,
                border=ft.border.all(1, "#DDE3F2"),
                shadow=ft.BoxShadow(blur_radius=12, spread_radius=0, color="#18000000", offset=ft.Offset(0, 4)),
                content=ft.Column(
                    [
                        ft.Text(
                            footer_text,
                            size=footer_font,
                            color="#334155",
                            weight="bold",
                            max_lines=2,
                            no_wrap=False,
                        ),
                        ft.Row(
                            [
                                ft.Text(footer_name, size=name_font, weight="bold", color="#1E293B"),
                                ft.IconButton(
                                    icon=ft.Image(src="whatsapp_logo.svg", width=54, height=54),
                                    padding=0,
                                    tooltip="WhatsApp queries",
                                    url=WHATSAPP_URL,
                                    on_click=lambda e: None,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    spacing=8,
                ),
            )

        def build_song_list():
            active_query = st["search_query"].strip()
            selected_letter = st["selected_letter"]
            active_mode = get_active_mode()

            if not selected_letter and not active_query:
                return ft.Container(
                    padding=30,
                    alignment=ft.alignment.Alignment(0, -0.2),
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.MY_LIBRARY_MUSIC_OUTLINED, size=44, color="#94A3B8"),
                            ft.Text("Choose a letter to browse songs", size=18, weight="bold", color="#334155"),
                            ft.Text(
                                "Only matching titles will be shown, so the app stays fast.",
                                size=13,
                                color="#64748B",
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                )

            results = [song for song in dm.songs if song.get("language", "").strip().lower() == st["lang"]]
            if selected_letter:
                results = [song for song in results if selected_letter in get_song_buckets(song, active_mode)]
            if active_query:
                results = [song for song in results if song_matches_query(song)]
            results.sort(key=lambda song: get_display_title(song, active_mode).lower())

            if not results:
                empty_title = f"No songs under {selected_letter}"
                empty_text = "Try another letter."
                if active_query:
                    empty_title = "No songs found"
                    empty_text = f'No songs match "{active_query}".'
                return ft.Container(
                    padding=30,
                    alignment=ft.alignment.Alignment(0, -0.2),
                    content=ft.Column(
                        [
                            ft.Text(empty_title, size=18, weight="bold", color="#334155"),
                            ft.Text(empty_text, size=13, color="#64748B", text_align=ft.TextAlign.CENTER),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                )

            list_view = ft.ListView(
                expand=True,
                padding=ft.padding.only(left=16, right=16, top=4, bottom=20),
                spacing=8,
            )
            for song in results:
                preview = get_display_preview(song, active_mode).strip()
                list_view.controls.append(
                    ft.Container(
                        bgcolor="white",
                        border_radius=16,
                        margin=ft.margin.symmetric(vertical=2),
                        shadow=ft.BoxShadow(blur_radius=6, spread_radius=0, color="#12000000", offset=ft.Offset(0, 2)),
                        content=ft.ListTile(
                            leading=ft.Container(
                                width=40,
                                height=40,
                                alignment=ft.alignment.Alignment(0, 0),
                                bgcolor="#EEF1FB",
                                border_radius=20,
                                content=ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED, color="#3949AB", size=20),
                            ),
                            title=ft.Text(get_display_title(song, active_mode), weight="bold", color="#121212", size=18),
                            subtitle=ft.Text(
                                preview,
                                size=12,
                                color="#6B7280",
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            on_click=lambda e, item=song: show_reader(item),
                        ),
                    )
                )
            return list_view

        def build_letter_rows(letters):
            if st["selected_letter"]:
                return ft.Row(
                    [
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=18, vertical=12),
                            bgcolor="#1A237E",
                            border_radius=16,
                            content=ft.Text(st["selected_letter"], color="white", weight="bold"),
                        ),
                        ft.TextButton("Change", on_click=lambda e: clear_letter_selection()),
                    ],
                    spacing=10,
                )

            rows = []
            chunk_size = 6 if len(letters) > 30 else 7
            for start in range(0, len(letters), chunk_size):
                chunk = letters[start:start + chunk_size]
                row = ft.Row(spacing=8)
                for letter in chunk:
                    row.controls.append(
                        ft.Container(
                            width=44,
                            height=44,
                            alignment=ft.alignment.Alignment(0, 0),
                            bgcolor="white",
                            border_radius=14,
                            border=ft.border.all(1, "#D9DEEA"),
                            content=ft.Text(letter, color="#475569", weight="bold", size=15),
                            on_click=lambda e, value=letter: select_letter(value),
                        )
                    )
                rows.append(row)
            return ft.Column(rows, spacing=8)

        def build_alphabet_selector():
            active_search = st["search_query"].strip()
            search_button = ft.Container(
                bgcolor="#EEF1FB" if st["search_open"] else "white",
                border_radius=14,
                border=ft.border.all(1, "#D9DEEA"),
                content=ft.IconButton(
                    ft.Icons.SEARCH,
                    icon_color="#1A237E",
                    tooltip="Search song names",
                    on_click=lambda e: toggle_search(),
                ),
            )

            selector_row = ft.Row(
                [
                    ft.ElevatedButton(
                        "TELUGU" if st["lang"] == "telugu" else "TAMIL",
                        bgcolor="#1A237E" if get_active_mode() == "native" else "white",
                        color="white" if get_active_mode() == "native" else "#64748B",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14), elevation={"": 0}),
                        on_click=lambda e: change_alphabet_mode("native"),
                    ),
                    ft.ElevatedButton(
                        "ENGLISH",
                        bgcolor="#1A237E" if get_active_mode() == "english" else "white",
                        color="white" if get_active_mode() == "english" else "#64748B",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14), elevation={"": 0}),
                        on_click=lambda e: change_alphabet_mode("english"),
                    ),
                    search_button,
                ],
                spacing=10,
            )

            selected_text = st["selected_letter"] if st["selected_letter"] else "None"
            search_controls = ft.Container()
            if st["search_open"]:
                search_field.hint_text = "Search song name in this letter" if st["selected_letter"] else "Search song name in this tab"
                search_controls = ft.Container(
                    margin=ft.margin.only(top=10),
                    content=ft.Row(
                        [
                            search_field,
                            ft.ElevatedButton(
                                "Clear" if active_search else "Go",
                                bgcolor="#1A237E",
                                color="white",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14), elevation={"": 0}),
                                on_click=lambda e: clear_search() if active_search else apply_search(),
                            ),
                        ],
                        spacing=10,
                    ),
                )

            browser_content = build_letter_rows(get_letters_for_language())
            if active_search:
                browser_content = ft.Container(
                    padding=ft.padding.only(top=6, bottom=2),
                    content=ft.Text("Search results", size=13, color="#64748B"),
                )

            return ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Browse by alphabet", size=16, weight="bold", color="#1E293B"),
                            ft.Text(f"Selected: {selected_text}", size=12, color="#64748B"),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(height=8),
                    selector_row,
                    search_controls,
                    ft.Container(height=10),
                    browser_content,
                ],
                spacing=0,
            )

        def build_lang_switch():
            return ft.Row(
                [
                    ft.ElevatedButton(
                        "TAMIL",
                        expand=1,
                        bgcolor="#1A237E" if st["lang"] == "tamil" else "white",
                        color="white" if st["lang"] == "tamil" else "#7A7A7A",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=18), elevation={"": 0}),
                        on_click=lambda e: change_lang("tamil"),
                    ),
                    ft.ElevatedButton(
                        "TELUGU",
                        expand=1,
                        bgcolor="#1A237E" if st["lang"] == "telugu" else "white",
                        color="white" if st["lang"] == "telugu" else "#7A7A7A",
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=18), elevation={"": 0}),
                        on_click=lambda e: change_lang("telugu"),
                    ),
                ],
                spacing=15,
            )

        def build_header():
            return ft.Container(
                gradient=ft.LinearGradient(begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1), colors=["#1A237E", "#283593"]),
                padding=ft.padding.only(top=26, left=20, right=20, bottom=14),
                content=ft.Row(
                    [
                        ft.Row(
                            [
                                ft.Container(
                                    width=48,
                                    height=48,
                                    border_radius=14,
                                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                    content=ft.Image(src="icon.png", error_content=ft.Icon(ft.Icons.MUSIC_NOTE, color="white")),
                                ),
                                ft.Text("GGGM", color="white", size=22, weight="bold"),
                            ],
                            spacing=12,
                        ),
                        ft.Row(
                            [
                                ft.Container(
                                    bgcolor="#FFFFFF22",
                                    border_radius=14,
                                    padding=6,
                                    content=build_avatar(42, clickable=True),
                                ),
                                ft.Container(
                                    bgcolor="#FFFFFF22",
                                    border_radius=14,
                                    content=ft.IconButton(ft.Icons.SETTINGS, icon_color="white", on_click=lambda e: show_settings()),
                                ),
                            ],
                            spacing=10,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            )

        def refresh_home():
            header_container.content = build_header().content
            lang_row.content = build_lang_switch()
            alphabet_container.content = build_alphabet_selector()
            list_container.content = build_song_list()
            footer_container.content = build_footer()
            page.update()

        def select_letter(letter):
            st["selected_letter"] = letter
            refresh_home()

        def clear_letter_selection():
            st["selected_letter"] = None
            refresh_home()

        def change_alphabet_mode(mode):
            st["alphabet_mode"][st["lang"]] = mode
            st["selected_letter"] = None
            st["search_query"] = ""
            search_field.value = ""
            refresh_home()

        def apply_search():
            st["search_query"] = (search_field.value or "").strip()
            refresh_home()

        def clear_search():
            st["search_query"] = ""
            search_field.value = ""
            refresh_home()

        def toggle_search():
            st["search_open"] = not st["search_open"]
            if not st["search_open"]:
                clear_search()
                return
            refresh_home()

        def change_lang(language):
            st["lang"] = language
            st["selected_letter"] = None
            st["search_query"] = ""
            search_field.value = ""
            refresh_home()

        def sync_user_async(first_login=False):
            if st["profile_syncing"]:
                return
            st["profile_syncing"] = True

            def _task():
                try:
                    dm.sync_user_to_cloud(dm.profile, first_login=first_login)
                except Exception as ex:
                    log(f"User sync error: {ex}")
                finally:
                    st["profile_syncing"] = False

            threading.Thread(target=_task, daemon=True).start()

        def render_home():
            page.appbar.visible = False
            body_container.content = home_view
            body_container.bgcolor = "#F3F4F8"
            refresh_home()

        def show_reader(song):
            page.appbar.title = ft.Text(get_display_title(song, get_active_mode()), color="white")
            page.appbar.bgcolor = "#1A237E"
            page.appbar.leading = ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda e: render_home())
            page.appbar.actions = [
                ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_color="white", on_click=lambda e: zoom(-2)),
                ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, icon_color="white", on_click=lambda e: zoom(2)),
            ]
            page.appbar.visible = True
            lyrics_view = ft.ListView(expand=True, padding=30)

            def refresh_reader():
                lyrics_view.controls.clear()
                for line in song.get("lyrics", "").split("\n"):
                    if line.strip():
                        lyrics_view.controls.append(ft.Text(line.strip(), size=st["font_size"], color="#2C3E50", weight="500"))
                    else:
                        lyrics_view.controls.append(ft.Container(height=14))
                page.update()

            def zoom(delta):
                st["font_size"] = max(12, min(44, st["font_size"] + delta))
                refresh_reader()

            body_container.content = lyrics_view
            body_container.bgcolor = "#FFF9E1"
            refresh_reader()

        def show_settings():
            page.appbar.title = ft.Text("Settings", color="white")
            page.appbar.bgcolor = "#1A237E"
            page.appbar.leading = ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda e: render_home())
            page.appbar.visible = True
            page.appbar.actions = []

            sync_status = ft.Text("Downloads the latest songs from Firebase.", color="grey")
            song_count = ft.Text(f"Local songs: {len(dm.songs)}", color="grey", size=14)
            sync_button = ft.ElevatedButton("SYNC NOW", icon=ft.Icons.SYNC, bgcolor="#1A237E", color="white", height=60)

            def sync_act(e):
                if st["syncing"]:
                    return
                st["syncing"] = True
                sync_button.disabled = True
                sync_status.value = "Syncing songs from Firebase..."
                sync_status.color = "#1D4ED8"
                page.update()

                def _bg_sync():
                    try:
                        songs = dm.sync_songs_from_cloud()
                        dm.songs = songs
                        dm.save_songs()
                        st["selected_letter"] = None
                        st["search_query"] = ""
                        search_field.value = ""
                        sync_status.value = f"Success! {len(songs)} songs synced."
                        sync_status.color = "#15803D"
                        song_count.value = f"Local songs: {len(songs)}"
                        sync_button.disabled = False
                        st["syncing"] = False
                        page.update()
                        render_home()
                    except Exception as ex:
                        log(f"Sync error: {traceback.format_exc()}")
                        sync_status.value = f"Sync failed: {ex}"
                        sync_status.color = "#DC2626"
                        sync_button.disabled = False
                        st["syncing"] = False
                        page.update()

                threading.Thread(target=_bg_sync, daemon=True).start()

            sync_button.on_click = sync_act

            body_container.content = ft.Container(
                padding=30,
                content=ft.Column(
                    [
                        ft.Image(src="icon.png", width=120, height=120, error_content=ft.Icon(ft.Icons.MUSIC_NOTE, size=100)),
                        ft.Container(height=20),
                        ft.Text("Cloud Sync", size=24, weight="bold", color="black"),
                        ft.Text(f"Project: {PROJECT_ID}", color="grey"),
                        song_count,
                        ft.Container(height=20),
                        sync_button,
                        ft.Container(height=12),
                        sync_status,
                        ft.Divider(),
                        ft.Text("GGGM v8.0.0", color="grey", size=12),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
            body_container.bgcolor = "#F5F5F5"
            page.update()

        def on_profile_image_result(e: ft.FilePickerResultEvent):
            if not e.files:
                return
            file_path = e.files[0].path
            if not file_path:
                return
            dm.profile["image_path"] = file_path
            dm.save_profile()
            show_profile()

        def show_profile():
            page.appbar.title = ft.Text("Profile", color="white")
            page.appbar.bgcolor = "#1A237E"
            page.appbar.leading = ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda e: render_home())
            page.appbar.visible = True
            page.appbar.actions = []

            body_container.content = ft.Container(
                padding=24,
                content=ft.Column(
                    [
                        ft.Container(height=10),
                        build_avatar(110),
                        ft.TextButton("Change Photo", on_click=lambda e: profile_picker.pick_files(allow_multiple=False, allowed_extensions=["jpg", "jpeg", "png", "webp"])),
                        ft.Container(height=8),
                        ft.Text(dm.profile.get("name", "User"), size=24, weight="bold", color="#0F172A"),
                        ft.Text(dm.profile.get("mobile", ""), size=16, color="#475569"),
                        ft.Container(height=12),
                        build_footer(),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
            )
            body_container.bgcolor = "#F5F5F5"
            page.update()

        def finish_login():
            dm.profile.setdefault("created_at", format_now())
            dm.profile.setdefault("image_path", "")
            dm.save_profile()
            sync_user_async(first_login=True)
            render_home()

        def show_login(error_message=""):
            page.appbar.visible = False
            login_name = ft.TextField(label="Name", border_radius=16, autofocus=True)
            login_mobile = ft.TextField(label="Mobile Number", keyboard_type=ft.KeyboardType.NUMBER, border_radius=16, max_length=10)
            error_text = ft.Text(error_message, color="#DC2626", size=13)

            def submit_login(e):
                name = (login_name.value or "").strip()
                mobile = re.sub(r"\D", "", login_mobile.value or "")
                if not name:
                    error_text.value = "Please enter your name."
                    page.update()
                    return
                if len(mobile) != 10:
                    error_text.value = "Please enter a correct 10 digit mobile number."
                    page.update()
                    return

                dm.profile = {
                    "name": name,
                    "mobile": mobile,
                    "created_at": format_now(),
                    "image_path": "",
                }
                finish_login()

            body_container.content = ft.Container(
                expand=True,
                padding=24,
                content=ft.Column(
                    [
                        ft.Container(height=28),
                        ft.Container(
                            width=72,
                            height=72,
                            border_radius=22,
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            content=ft.Image(src="icon.png", error_content=ft.Icon(ft.Icons.MUSIC_NOTE, color="white")),
                        ),
                        ft.Text("Welcome to GGGM", size=28, weight="bold", color="#0F172A"),
                        ft.Text("Login once to continue into the app.", size=14, color="#64748B", text_align=ft.TextAlign.CENTER),
                        ft.Container(height=12),
                        ft.Container(
                            bgcolor="white",
                            border_radius=22,
                            padding=22,
                            shadow=ft.BoxShadow(blur_radius=12, spread_radius=0, color="#12000000", offset=ft.Offset(0, 4)),
                            content=ft.Column(
                                [
                                    login_name,
                                    login_mobile,
                                    error_text,
                                    ft.ElevatedButton(
                                        "LOGIN",
                                        bgcolor="#1A237E",
                                        color="white",
                                        height=52,
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16), elevation={"": 0}),
                                        on_click=submit_login,
                                    ),
                                ],
                                spacing=14,
                            ),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
            )
            body_container.bgcolor = "#F3F4F8"
            page.update()

        search_field = ft.TextField(
            value="",
            expand=True,
            hint_text="Search song name in this tab",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=16,
            bgcolor="white",
            border_color="#D9DEEA",
            content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
            on_submit=lambda e: apply_search(),
        )

        profile_picker = ft.FilePicker(on_result=on_profile_image_result)
        page.overlay.append(profile_picker)

        header_container = ft.Container()
        lang_row = ft.Container(padding=15)
        alphabet_container = ft.Container(padding=ft.padding.only(left=16, right=16, bottom=8))
        list_container = ft.Container(expand=True)
        footer_container = ft.Container()
        home_view = ft.Column([header_container, lang_row, alphabet_container, list_container, footer_container], spacing=0, expand=True)
        body_container = ft.Container(content=home_view, expand=True, bgcolor="#F3F4F8")
        page.add(body_container)

        if dm.profile.get("name") and re.fullmatch(r"\d{10}", dm.profile.get("mobile", "")):
            sync_user_async(first_login=False)
            render_home()
        else:
            show_login()

    except Exception:
        err_msg = traceback.format_exc()
        log(f"FATAL ERROR: {err_msg}")
        page.add(
            ft.Container(
                padding=20,
                bgcolor="red",
                expand=True,
                content=ft.Text(f"INTERNAL ERROR:\n{err_msg}", color="white"),
            )
        )


ft.app(target=main)
