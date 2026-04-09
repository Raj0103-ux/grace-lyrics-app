# GGGM App

A production-ready Android App for Christian Song Lyrics built with Python (Flet/Flutter) and SQLite. 

## Features Currently Implemented
1. **Bilingual Support:** Dedicated Tamil and Telugu tabs.
2. **Offline-First Architecture:** A robust `db.py` layer acting as a "Read-Through Cache". It intercepts requests, pulls from local SQLite instantly if available, and prepares the groundwork to fetch from your upcoming Admin Cloud API if missing.
3. **Smart Search:** Real-time filtering by Song Title.
4. **Interactive Viewer:** Adjustable font sizing (`+ A` and `- A`) across the lyrics screen.
5. **Favorites System:** Persistent local state for favorited songs.
6. **Secret Admin Hub:** An access point for running local import pipelines during development/offline phases.

## Technology Stack
- **Framework:** Flet (Generates native Flutter code from Python logic).
- **Storage:** Local SQLite (Ready to be upgraded to SQLCipher for encrypted proprietary caching).
- **Target OS:** Android.

---

## 🛠 How to Build the `.apk` file for Android

Because this app is written in Flet, you can compile it natively into an Android `.apk` straight from this folder without writing a single line of Java or Kotlin!

### Prerequisite 1: Flutter SDK
1. Download and install [Flutter SDK](https://docs.flutter.dev/get-started/install/windows).
2. Run `flutter doctor` in your terminal to ensure you have no missing Android components (Android Studio/SDK tools are usually required).

### Prerequisite 2: Flet Packaging Tools
Open your terminal in this repository (`grace_lyrics`) and install the Flet build pipeline:
```bash
pip install flet
```

### The Build Command
Once Flutter is installed and recognized by your system, run this exact command to package the app into a release Android bundle:

```bash
flet build apk
```

**Customizing the Build:**
If you want to customize the bundle name, version, and organization, run it like this:
```bash
flet build apk --project "GGGM" --org com.gggm --version 1.0.0
```

### Applying the Logo
I have placed two generated logos in the `assets/` folder of our workspace. To apply it, name your chosen logo `icon.png` and place it in an `assets` folder directly next to `main.py`. Flet automatically binds the Android App Icon to `assets/icon.png`.

## Future Expansion: The Admin Cloud API
The backend logic is stubbed out inside `src/models/db.py`. 
When you build your admin dashboard:
1. Upload your new lyrics via the Admin Portal to your Cloudflare D1 / Firestore.
2. Update the `fetch_from_cloud_api(song_id)` Python function in `db.py` to hit your server's endpoint.
3. Everything else handles itself magically! The app checks local storage -> fetches from the cloud if missing -> saves to phone instantly -> returns to user.
