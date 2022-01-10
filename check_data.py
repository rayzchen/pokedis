import json

with open("utils/datafiles/pokedata.json") as f:
    pokemon = json.load(f)

with open("utils/datafiles/movedata.json") as f:
    moves = json.load(f)

with open("utils/datafiles/special_moves.json") as f:
    special = json.load(f)

for poke in pokemon.values():
    for movenum in poke["learnset"].values():
        if str(movenum) not in moves:
            print(f"Move number {movenum} not in movedata.json")
            continue

        if moves[str(movenum)]["effect"] == 1 and str(movenum) not in special:
            print(f"Move number {movenum} not in special_moves.json ")
