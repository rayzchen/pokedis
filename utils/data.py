import math
import random
import json

with open("utils/datafiles/pokedata.json") as f:
    all_pokemon_data = json.loads(f.read())
with open("utils/datafiles/movedata.json") as f:
    all_move_data = json.loads(f.read())
with open("utils/datafiles/effective.json") as f:
    effective_table = json.loads(f.read())

def calc_hp(base, ivs, ev, level):
    iv = ivs[0] & 8 + ivs[1] & 4 + ivs[2] & 2 + ivs[3] & 1
    return math.floor(((base + iv) * 2 + math.floor(math.sqrt(ev) / 4)) * level / 100) + level + 10

def calc_stat(base, iv, ev, level):
    return math.floor(((base + iv) * 2 + math.floor(math.sqrt(ev) / 4)) * level / 100) + 5

def calc_exp(level, offset=0):
    return int(6/5 * level ** 3 - 15 * level ** 2 + 100 * level - 140)

def gen_species(species, level, types, moves, pp, base):
    poke = {"species": species, "level": level, "status": [], "types": types.copy(), "moves": moves, "ot": 0, "exp": calc_exp(level), "ev": [0, 0, 0, 0, 0], "iv": [random.randint(0, 15) for _ in range(4)], "pp": pp}
    poke["stats"] = {"hp": calc_hp(base[0], poke["iv"], 0, level), "atk": calc_stat(base[1], poke["iv"][0], 0, level), "def": calc_stat(base[2], poke["iv"][1], 0, level), "spec": calc_stat(base[3], poke["iv"][2], 0, level), "spd": calc_stat(base[4], poke["iv"][3], 0, level)}
    poke["hp"] = poke["stats"]["hp"]
    return poke

def gen_pokemon(species, level):
    species = str(species)
    moves = all_pokemon_data[species]["moves"]
    moves = moves + [0] * (4 - len(moves))
    pp = [all_move_data[str(move)]["pp"] for move in all_pokemon_data[species]["moves"]]
    pp += [0] * (4 - len(pp))
    poke = gen_species(species, level, all_pokemon_data[species]["types"], moves, pp, all_pokemon_data[species]["base"])
    
    for i in range(1, level + 1):
        if str(i) in all_pokemon_data[species]["learnset"]:
            if 0 in poke["moves"]:
                idx = poke["moves"].index(0)
                poke["moves"].pop(idx)
                poke["moves"].insert(idx, all_pokemon_data[species]["learnset"][str(i)])
            else:
                poke["moves"].pop(0)
                poke["moves"].append(all_pokemon_data[species]["learnset"][str(i)])
    return poke

def get_damage(poke1, poke2, move):
    movedata = all_move_data[str(move)]
    a = (2 * poke1["level"] / 5 + 2) * movedata["power"]
    if movedata["special"]:
        a *= poke1["stats"]["spec"] / poke2["stats"]["spec"]
    else:
        a *= poke1["stats"]["atk"] / poke2["stats"]["def"]
    b = a / 50 + 2
    if movedata["type"] in poke1["types"]:
        b *= 1.5
    return b

def is_crit(poke1):
    return int(random.randint(0, 255) < math.floor(poke1["stats"]["spd"] / 2)) + 1

def get_effective(move, poke2):
    movedata = all_move_data[str(move)]
    effective = effective_table[movedata["type"]][poke2["types"][0]]
    if poke2["types"][1] != poke2["types"][0]:
        effective *= effective_table[movedata["type"], poke2["types"][1]]
    return effective

def pokename(idx):
    return all_pokemon_data[str(idx)]["name"]

def movename(idx):
    return all_move_data[str(idx)]["name"]

items = ["pokéball", "potion", "antidote", "paralyz", "burn"]

example_poke = gen_pokemon(176, 34)
print(example_poke)
