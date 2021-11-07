import requests

r = requests.get("https://pokedis.rayzchen.repl.co/db")
with open("db.json", "w+") as f:
    f.write(r.text)
