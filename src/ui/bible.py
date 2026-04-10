import flet as ft
import json
import os

class BibleReader:
    def __init__(self, page: ft.Page, history_stack):
        self.page = page
        self.history_stack = history_stack
        self.selected_lang = "tamil"
        self.selected_book = None
        self.selected_chapter = 1
        
        # Load Metadata
        try:
            with open("assets/bible/metadata.json", "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        except:
            self.metadata = {"tamil": [], "telugu": []}

    def show_library(self):
        self.page.controls.clear()
        
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Text("GGGM Bible", size=24, color="white", weight=ft.FontWeight.BOLD),
                ft.SegmentedButton(
                    segments=[
                        ft.Segment(value="tamil", label=ft.Text("Tamil")),
                        ft.Segment(value="telugu", label=ft.Text("Telugu")),
                    ],
                    selected={"tamil"},
                    on_change=self.on_lang_change,
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#3F51B5", padding=20, width=float("inf")
        )

        books_list = self.metadata.get(self.selected_lang, [])
        
        grid = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=150,
            child_aspect_ratio=1.0,
            spacing=10,
            padding=20,
        )

        for book in books_list:
            grid.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.MENU_BOOK, color="#3F51B5"),
                        ft.Text(book["name"], size=14, weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor="white",
                    border_radius=15,
                    on_click=lambda e, b=book: self.open_chapters(b),
                    shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12)
                )
            )

        self.page.add(
            ft.SafeArea(content=ft.Column([header, grid], spacing=0, expand=True), expand=True)
        )
        self.page.update()

    def on_lang_change(self, e):
        self.selected_lang = list(e.selection)[0]
        self.show_library()

    def open_chapters(self, book):
        self.selected_book = book
        # Here we would load actual chapter count from files
        # For now, let's assume a few chapters
        self.show_reading_view(1)

    def show_reading_view(self, chapter):
        self.page.controls.clear()
        self.selected_chapter = chapter
        
        # Sacred UI Reader Header
        header = ft.Container(
            content=ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, icon_color="white", on_click=lambda _: self.show_library()),
                ft.Text(f"{self.selected_book['name']} {chapter}", size=20, color="white", weight=ft.FontWeight.BOLD),
                ft.IconButton(ft.Icons.SHARE, icon_color="white"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#3F51B5", padding=ft.Padding(10, 5, 10, 5), width=float("inf")
        )

        # Verse Reader Content (Sacred UI Theme)
        verses_col = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=15, expand=True)
        
        # Load Verses from local file
        # In a real scenario, we load assets/bible/{lang}/{book}.json
        verses_col.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(f"Verse {v}: Sample sacred text for {self.selected_book['name']} chapter {chapter}...", size=16, color="#5D4037")
                    for v in range(1, 21) # Placeholder for now
                ]),
                padding=20
            )
        )

        # THE QUICK-JUMP STRIP (Horizontal Scroll)
        jump_strip = ft.Row(
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            controls=[
                ft.Container(
                    content=ft.Text(str(i), weight=ft.FontWeight.BOLD, color="white" if i == chapter else "#3F51B5"),
                    bgcolor="#3F51B5" if i == chapter else "white",
                    width=40, height=40, border_radius=10,
                    alignment=ft.alignment.center,
                    on_click=lambda e, ch=i: self.show_reading_view(ch),
                    border=ft.border.all(1, "#3F51B5")
                ) for i in range(1, 21) # Placeholder for chapters
            ]
        )

        jump_container = ft.Container(
            content=jump_strip,
            padding=10,
            bgcolor="white",
            border=ft.border.only(top=ft.border.BorderSide(1, "#E8EAF6"))
        )

        self.page.add(
            ft.SafeArea(
                content=ft.Column([
                    header,
                    ft.Container(
                        content=verses_col,
                        bgcolor="#FFF9E1", # Sacred UI Parchment Color
                        expand=True,
                        padding=ft.Padding(15, 0, 15, 0)
                    ),
                    jump_container
                ], spacing=0),
                expand=True
            )
        )
        self.page.update()
