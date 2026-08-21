import urllib.request
import re
import time

def find_trailer(movie_title):
    query = f"{movie_title} movie official trailer".replace(' ', '+').replace('&', 'and')
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

import ast

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# We extract the block of movies
movies_block = re.search(r'movies\s*=\s*\[(.*?)\]', content, re.DOTALL)
if movies_block:
    movies_text = movies_block.group(0)
    lines = movies_text.split('\n')
    new_lines = []
    for line in lines:
        if line.strip().startswith('(') and ')' in line:
            # simple parse
            matched = re.search(r'\("([^"]+)"', line)
            if matched:
                title = matched.group(1)
                print(f"Finding trailer for: {title}")
                new_url = find_trailer(title)
                if new_url:
                    # replace the last url
                    line = re.sub(r'"https://www\.youtube\.com/watch\?v=[^"]+"', f'"{new_url}"', line)
                time.sleep(0.5)
        new_lines.append(line)
    
    new_movies_text = '\n'.join(new_lines)
    content = content.replace(movies_text, new_movies_text)
    
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("app.py updated successfully!")
