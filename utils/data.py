import math
import random

def calc_hp(base, ivs, ev, level):
    iv = ivs[0] & 8 + ivs[1] & 4 + ivs[2] & 2 + ivs[3] & 1
    return math.floor(((base + iv) * 2 + math.floor(math.sqrt(ev) / 4)) * level / 100) + level + 10

def calc_stat(base, iv, ev, level):
    return math.floor(((base + iv) * 2 + math.floor(math.sqrt(ev) / 4)) * level / 100) + 5

def calc_exp(level, offset=0):
    return int(6/5 * level ** 3 - 15 * level ** 2 + 100 * level - 140)

def gen_pokemon(species, level, types, moves, pp, base):
    poke = {"species": species, "level": level, "status": [], "type1": types[0], "type2": types[1], "moves": moves, "ot": 0, "exp": calc_exp(level), "ev": [0, 0, 0, 0, 0], "iv": [random.randint(0, 15) for _ in range(4)], "pp": pp}
    poke["stats"] = {"hp": calc_hp(base[0], poke["iv"], 0, level), "atk": calc_stat(base[1], poke["iv"][0], 0, level), "def": calc_stat(base[2], poke["iv"][1], 0, level), "spec": calc_stat(base[3], poke["iv"][2], 0, level), "spd": calc_stat(base[4], poke["iv"][3], 0, level)}
    poke["hp"] = poke["stats"]["hp"]
    return poke

def pokename(idx):
    if idx == 176:
        return "Charmander"
    return "Rattata"

items = ["pokéball", "potion", "antidote", "paralyz", "burn"]

example_poke = gen_pokemon(176, 5, ["fire", "fire"], [10, 45, 0, 0], [35, 40, 0, 0], [39, 52, 32, 50, 65])
print(example_poke)
