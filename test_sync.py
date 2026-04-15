import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

base = 'https://firestore.googleapis.com/v1/projects/grace-lyrics-admin/databases/(default)/documents/songs'
total = 0
next_token = None
lang_count = {}
pages = 0

while True:
    url = base
    if next_token:
        url += f'?pageToken={next_token}'
    r = urllib.request.urlopen(url)
    d = json.load(r)
    docs = d.get('documents', [])
    total += len(docs)
    for doc in docs:
        lang = doc['fields']['language']['stringValue']
        lang_count[lang] = lang_count.get(lang, 0) + 1
    next_token = d.get('nextPageToken')
    pages += 1
    print(f'Page {pages}: {len(docs)} docs, hasNext={bool(next_token)}')
    if not next_token:
        break

print(f'\nTotal: {total} songs')
print(f'Languages: {lang_count}')
