import flet as ft
import os
import json
import base64
from typing import List

# Identity
APP_NAME = "GGGM - Admin Hub"

class WebAdminApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = APP_NAME
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.bgcolor = "#F8F9FE"
        self.songs = []
        self.init_ui()

    def init_ui(self):
        # Header
        self.header = ft.Container(
            content=ft.Row([
                ft.Image(src="icon.png", width=40, height=40, border_radius=8),
                ft.Text(APP_NAME, size=22, weight=ft.FontWeight.BOLD, color="white"),
            ], alignment=ft.MainAxisAlignment.START),
            padding=20,
            bgcolor="#3F51B5",
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
        )

        # Status text
        self.status = ft.Text("Ready to upload.", color=ft.Colors.GREY_700)

        # File Picker
        self.file_picker = ft.FilePicker(on_result=self.on_file_result)
        self.page.overlay.append(self.file_picker)

        # Upload Button
        self.upload_btn = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CLOUD_UPLOAD_ROUNDED, size=50, color="#3F51B5"),
                ft.Text("CLICK TO SELECT FILES", weight=ft.FontWeight.BOLD, color="#3F51B5"),
                ft.Text("Supports .txt and .pptx files", size=12, color=ft.Colors.GREY_500),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(2, "#E0E0E0"),
            border_radius=15,
            padding=40,
            on_click=lambda _: self.file_picker.pick_files(allow_multiple=True),
            ink=True,
            alignment=ft.alignment.center,
        )

        # Preview Area
        self.preview_list = ft.ListView(expand=True, spacing=10, padding=20)

        # Main Layout
        self.page.add(
            self.header,
            ft.Container(
                content=ft.Column([
                    ft.Text("Bulk Song Upload", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Add new lyrics to the GGGM cloud database instantly.", color=ft.Colors.GREY_600),
                    ft.Divider(height=40),
                    self.upload_btn,
                    ft.Container(height=20),
                    ft.Row([
                        ft.Text("SELECTED SONGS", size=12, weight=ft.FontWeight.W_500),
                        self.status,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(
                        content=self.preview_list,
                        expand=True,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=10,
                        border=ft.border.all(1, "#EEEEEE"),
                    ),
                    ft.FilledButton(
                        text="PUBLISH TO CLOUD",
                        icon=ft.Icons.SEND,
                        on_click=self.publish_to_cloud,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                        height=50,
                    )
                ], expand=True),
                padding=40,
                expand=True,
            )
        )

    def on_file_result(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        
        self.status.value = f"Processing {len(e.files)} files..."
        self.page.update()

        for f in e.files:
            # In a real web environment, we'd handle the file bytes
            # For local testing, we look at the name
            name = f.name.rsplit(".", 1)[0]
            self.songs.append({
                "title": name,
                "language": "tamil" if "ta" in name.lower() else "telugu",
                "lyrics": "File content goes here...",
                "status": "Pending"
            })
        
        self.refresh_preview()
        self.status.value = f"{len(self.songs)} songs ready."
        self.page.update()

    def refresh_preview(self):
        self.preview_list.controls.clear()
        for s in self.songs:
            self.preview_list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, color="#3F51B5"),
                    title=ft.Text(s["title"]),
                    subtitle=ft.Text(f"Target: {s['language'].capitalize()}"),
                    trailing=ft.Text(s["status"], color=ft.Colors.BLUE if s["status"] == "Pending" else ft.Colors.GREEN),
                )
            )

    def publish_to_cloud(self, e):
        if not self.songs:
            self.status.value = "Nothing to publish!"; self.status.color = ft.Colors.RED
            self.page.update(); return

        self.status.value = "Connecting to Cloudflare..."; self.page.update()
        # Integration logic with Cloudflare D1 / Worker goes here
        # For now, we simulate success
        for s in self.songs:
            s["status"] = "Published ✅"
        
        self.refresh_preview()
        self.status.value = "All songs published to GGGM Cloud!"; self.status.color = ft.Colors.GREEN
        self.page.update()

def main(page: ft.Page):
    WebAdminApp(page)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
