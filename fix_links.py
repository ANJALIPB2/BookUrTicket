import sqlite3
import urllib.request
import re
import time

def check_link_valid(youtube_id):
    url = f"https://www.youtube.com/watch?v={youtube_id}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        if '"playabilityStatus":{"status":"ERROR"' in html or '"status":"UNPLAYABLE"' in html or 'Video unavailable' in html:
            return False
        return True
    except Exception as e:
        return False

def find_trailer(movie_title):
    query = f"{movie_title} official trailer".replace(' ', '+').replace('&', 'and')
    url = f"https://www.youtube.com/results?search_query={query}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        if video_ids:
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
    except Exception as e:
        print(f"Search failed for {movie_title}: {e}")
    return None

conn = sqlite3.connect('movies.db')
c = conn.cursor()
c.execute("SELECT id, title, trailer_url FROM movies")
movies = c.fetchall()

print("Checking and fixing trailer links...")
for m_id, title, url in movies:
    video_id = url.split("v=")[-1] if "v=" in url else ""
    if not video_id:
        video_id = url.split("/")[-1]
    
    is_valid = check_link_valid(video_id)
    if is_valid:
        print(f"[OK] {title} - {url}")
    else:
        print(f"[INVALID] {title} - {url} ... Searching for new one")
        new_url = find_trailer(title)
        if new_url:
            c.execute("UPDATE movies SET trailer_url = ? WHERE id = ?", (new_url, m_id))
            print(f"  -> Replaced with: {new_url}")
        else:
            print(f"  -> Could not find a replacement")
        time.sleep(1)

conn.commit()
conn.close()
print("Done!")
