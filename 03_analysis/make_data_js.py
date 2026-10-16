import json

with open('03_analysis/books_200.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

js_content = f"window.BOOKS_DATA = {json.dumps(books, ensure_ascii=False)};\n"
with open('04_slides/data.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Created 04_slides/data.js successfully.")
