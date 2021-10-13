import math
import random
import json
from .database import db
if "users" not in db:
    db["users"] = {}
if "servers" not in db:
    db["servers"] = {}

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

def calc_exp(level, growth, offset=0):
    if growth == 0:
        return level ** 3
    if growth == 3:
        return int(6/5 * level ** 3 - 15 * level ** 2 + 100 * level - 140)
    if growth == 4:
        return int(4/5 * level ** 3)
    if growth == 5:
        return int(5/4 * level ** 3)

def calc_exp_gain(trainer, poke1, poke2, wild):
    a = 1 if wild else 1.5
    t = 1.5 if trainer == poke1["ot"] else 1
    b = all_pokemon_data[str(poke2["species"])]["xp_yield"]
    return int(a * t * b * poke2["level"] / 7)

def gen_species(species, level, growth, types, moves, pp, base):
    poke = {"species": species, "level": level, "status": [], "types": types.copy(), "moves": moves, "ot": 0, "exp": calc_exp(level, growth), "ev": [0, 0, 0, 0, 0], "iv": [random.randint(0, 15) for _ in range(4)], "pp": pp}
    poke["stats"] = {"hp": calc_hp(base[0], poke["iv"], poke["ev"][0], level), "atk": calc_stat(base[1], poke["iv"][0], poke["ev"][1], level), "def": calc_stat(base[2], poke["iv"][1], poke["ev"][2], level), "spec": calc_stat(base[3], poke["iv"][2], poke["ev"][3], level), "spd": calc_stat(base[4], poke["iv"][3], poke["ev"][4], level)}
    poke["hp"] = poke["stats"]["hp"]
    return poke

def calc_stats(poke):
    base = all_pokemon_data[str(poke["species"])]["base"]
    level = poke["level"]
    diff = poke["stats"]["hp"] - poke["hp"]
    poke["stats"] = {"hp": calc_hp(base[0], poke["iv"], poke["ev"][0], level), "atk": calc_stat(base[1], poke["iv"][0], poke["ev"][1], level), "def": calc_stat(base[2], poke["iv"][1], poke["ev"][2], level), "spec": calc_stat(base[3], poke["iv"][2], poke["ev"][3], level), "spd": calc_stat(base[4], poke["iv"][3], poke["ev"][4], level)}
    poke["hp"] = poke["stats"]["hp"] - diff

def gen_pokemon(species, level):
    species = str(species)
    moves = all_pokemon_data[species]["moves"]
    moves = moves + [0] * (4 - len(moves))
    pp = [all_move_data[str(move)]["pp"] for move in all_pokemon_data[species]["moves"]]
    pp += [0] * (4 - len(pp))
    poke = gen_species(int(species), level, all_pokemon_data[species]["growth"], all_pokemon_data[species]["types"], moves, pp, all_pokemon_data[species]["base"])
    
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

def get_level(exp, growth):
    l = level_exp[growth]
    if exp in l:
        return l.index(exp)
    l.append(exp)
    l.sort()
    index = l.index(exp)
    l.remove(exp)
    return index

level_exp = [[calc_exp(i, j) for i in range(1, 101)] for j in (0, 3, 4, 5)]
level_exp = [level_exp[0], None, None, *level_exp[1:]]

items = ["Poké Ball", "Potion", "Antidote", "Paralyz Heal", "Burn Heal"]

example_poke = gen_pokemon(176, 34)
print(example_poke)
