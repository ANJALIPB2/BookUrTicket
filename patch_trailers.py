import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace Kalki trailer link
content = re.sub(
    r'\("Kalki 2898 AD",\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*"https://www\.youtube\.com/watch\?v=[a-zA-Z0-9_-]+"\)',
    r'("Kalki 2898 AD", \1, \2, \3, \4, \5, "https://www.youtube.com/watch?v=vnXho7kmlPw")',
    content
)

# Replace Animal trailer link
content = re.sub(
    r'\("Animal",\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*"https://www\.youtube\.com/watch\?v=[a-zA-Z0-9_-]+"\)',
    r'("Animal", \1, \2, \3, \4, \5, "https://www.youtube.com/watch?v=S7i50IGdnNs")',
    content
)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
print("done")
