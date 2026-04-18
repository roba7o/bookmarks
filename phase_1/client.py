import httpx

BASE = "http://localhost:8000"

# todo, understand dict structures, set structures, list of dicts etc and when to use

new_bookmarks = [
    {"book": "Grokking Algorithms", "Page": 54},
    {"book": "DSA with Python", "Page": 4},
    {"book": "Database Internals", "Page": "144"},
]

for book_mark in new_bookmarks:
    r = httpx.post(f"{BASE}/bookmarks/", json=book_mark)
    print(r.status_code, r.text)


get_response = httpx.get(f"{BASE}/bookmarks/")
print(get_response, (get_response.text))

delete_response = httpx.delete(f"{BASE}/bookmarks/2")

get_response2 = httpx.get(f"{BASE}/bookmarks/")
print(get_response2, (get_response2.text))

assert httpx.get(f"{BASE}/bookmarks/2").status_code == 404
print("404 confirmed after delete")
