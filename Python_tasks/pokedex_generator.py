import json
import os
import time

import constants
from data_checks import get_average_time
from load_files import load_data
from pokemonUtils import GenForms, get_pokemon_info, get_pokemon_name, get_diff_form_dictionary

repo_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(repo_file_path, 'input')
debug_file_path = os.path.join(repo_file_path, "Python_tasks", "Debug")
output_file_path = os.path.join(repo_file_path, "Python_tasks", "output")
first_execution_list = []
second_execution_list = []

def get_form_format(monsNo, formNo):
    mon_zeros = 3 - len(str(monsNo))
    form_zeros = 3 - len(str(formNo))
    return f"ZKN_FORM_{mon_zeros*'0'}{monsNo}_{form_zeros*'0'}{formNo}"

def remove_duplicates(path_dictionary):
    new_path = []
    for path_element in path_dictionary:
        if path_element not in new_path:
            new_path.append(path_element)
    return new_path

def remove_duplicate_forms(evolution_paths):
    for pokemon in evolution_paths.keys():
        evolution_paths[pokemon]["path"] = remove_duplicates(evolution_paths[pokemon]["path"])

def add_forms(evolution_paths, graph):
    for form in forms:
        form_num = forms[form]
        pokemon_id = int(form[-7:-4])
        evolve_array = graph[form_num]["ar"]
        for pokemon in evolution_paths.keys():
            if int(pokemon) != pokemon_id:
                continue
            initial_evolution_path = evolution_paths[pokemon]["path"]
            form_evo_path = evolution_paths[form_num]["path"]
            first_form_evo = form_evo_path[0]

            for evolution in initial_evolution_path:
                if len(evolve_array) != 0:
                    continue
                if evolution in evolution_paths[first_form_evo]["path"]:
                    evolution_paths[evolution]["path"].append(form_num)
                if len(evolution_paths[form_num]["path"]) < 2:
                    evolution_path = evolution_paths[evolution]["path"] + form_evo_path
                    evolution_paths[form_num]["path"] = remove_duplicates(evolution_path)
                    evolution_paths[evolution]["path"] = remove_duplicates(evolution_path)

def process_next_mon(adjacent_nodes):
    next_mon = adjacent_nodes[2]
    next_form = adjacent_nodes[3]
    form_format = get_form_format(next_mon, next_form)

    if form_format in forms.keys():
        next_mon = forms[form_format]
        return next_mon, next_form
    return next_mon, next_form

def process_current_mon(queue):

    current_mon = queue.pop(0)
    current_form = queue.pop(0)
    form_format = get_form_format(current_mon, current_form)

    if form_format in forms.keys():
        current_mon = forms[form_format]
        return current_mon, current_form

    return current_mon, current_form

def filter_evolutions(evolution_paths, current_mon_path, mon_index):
    filtered_path = []

    for mon, index in enumerate(evolution_paths[current_mon_path[mon_index]]["path"]):
        if index not in evolution_paths[current_mon_path[mon_index]]["path"][:mon]:
            filtered_path.append(mon)

    evolution_paths[current_mon_path[mon_index]]["path"] = filtered_path

def update_evolve_paths(evolution_paths, current_mon, current_mon_path):
    evolution_paths[current_mon]["path"].append(current_mon)
    evolution_paths[current_mon]["path"] = list(dict.fromkeys(evolution_paths[current_mon]["path"]))

    for i in range(len(current_mon_path)):
        evolution_paths[current_mon_path[i]]["path"].append(current_mon)
        evolution_paths[current_mon_path[i]]["path"] = [
            x for j, x in enumerate(evolution_paths[current_mon_path[i]]["path"])
            if x not in set(evolution_paths[current_mon_path[i]]["path"][j + 1:])
        ]

def get_second_pathfind_targets(evolution_paths, previous_mon, current_mon, graph):
    '''
    This is for getting the target evolution paths for evolutions
    '''
    targets = evolution_paths[previous_mon]["targets"]
    current_mon_path = evolution_paths[current_mon]["path"]
    first_mon_path = evolution_paths[current_mon_path[0]]["path"]
    first_mon_array = graph[current_mon_path[0]]["ar"]

    if current_mon not in targets:
        if previous_mon == constants.WURMPLE or previous_mon == constants.GOOMY:
            evolution_paths[constants.WURMPLE]["targets"] = [constants.SILCOON, constants.CASCOON]
            evolution_paths[constants.GOOMY]["targets"] = [constants.SLIGGOO, constants.HISUI_SLIGGOO]

        if sum(first_mon_path) / len(first_mon_path) - current_mon > 3:
            # This checks if the difference between the average of the pokemonIDs and the current_mon is greater than 3
            # This is for pokemon that have branching paths for evolutions like Cubone or Exeggcute
            # The reason this needs to exist is because the evo array lists alt forms of the evolution pokemon first
            evolution_paths[previous_mon]["targets"].append(current_mon)
        elif len(first_mon_path) > 3:
            # This checks if the first mon's evo path is greater than 3
            # This is a usecase for mons like Eevee
            evolution_paths[previous_mon]["targets"].append(current_mon)
        elif len(first_mon_array) > 5:
            # This is just for Burmy, the bastard that has different forms but they only evolve into the final evo
            evolution_paths[previous_mon]["targets"].append(current_mon)

def second_pathfind(pokemon, evolution_paths, new_queue, graph):

    while new_queue:
        current_mon, current_form = process_current_mon(new_queue)

        evolution_paths[current_mon]["path"].append(pokemon)
        current_mon_path = evolution_paths[current_mon]["path"]
        update_evolve_paths(evolution_paths, current_mon, current_mon_path)
        get_second_pathfind_targets(evolution_paths, pokemon, current_mon, graph)

def first_pathfind(pokemon, evolution_paths, graph, queue, new_queue):

    while queue:
        current_mon, current_form = process_current_mon(queue)

        adjacent_nodes = graph[current_mon]["ar"]
        if len(adjacent_nodes) == 0:
            continue
        next_mon, next_form = process_next_mon(adjacent_nodes)

        targets = evolution_paths[current_mon]["targets"]
        if next_mon not in targets:
            evolution_paths[current_mon]["targets"].append(next_mon)

        evolution_paths[next_mon]["path"] = evolution_paths[current_mon]["path"] + [next_mon]
        for i in range(2, len(adjacent_nodes), 5):
            # Increments by 5 starting on the third value which is the target evolution
            new_queue.append(adjacent_nodes[i])
            new_queue.append(adjacent_nodes[i + 1])

            second_pathfind(pokemon, evolution_paths, new_queue, graph)

            new_queue.append(adjacent_nodes[i])
            new_queue.append(adjacent_nodes[i + 1])

        queue.append(next_mon)
        queue.append(next_form)

    for extra in evolution_paths[pokemon]["path"]:
        for i in range(0, len(graph[extra]["ar"]), 5):
            evolution_paths[pokemon]["method"].append(graph[extra]["ar"][i])
        evolution_paths[pokemon]["ar"].append(graph[extra]["ar"])

def start_pathfinding(evolution_paths, graph):

    for pokemon in evolution_paths.keys():
        start_time = time.time()
        queue = []
        queue.append(pokemon)
        queue.append(0)
        new_queue = []
        evo_path = evolution_paths[pokemon]["path"]
        if pokemon not in evo_path:
            evolution_paths[pokemon]["path"].append(pokemon)
        first_pathfind(pokemon, evolution_paths, graph, queue, new_queue)
        end_time = time.time()
        second_execution_list.append(end_time - start_time)

def evolution_pathfinding():
    with open(os.path.join(input_file_path, 'EvolveTable.json'), "r", encoding="utf-8") as f:
        graphing = json.load(f)
    graph = graphing["Evolve"]
    evolution_paths = {}
    for node in graph:
        evolution_paths[node["id"]] = {"path": [], "method": [], "ar": [], "targets": []}

    start_pathfinding(evolution_paths, graph)

    with open(os.path.join(debug_file_path, "evolution.json"), "w", encoding = "utf-8") as output:
        json.dump(evolution_paths, output, ensure_ascii=False, indent=2)

    add_forms(evolution_paths, graph)
    remove_duplicate_forms(evolution_paths)
    return evolution_paths

def get_mon_dex_info(pokemon, evolution_paths):
    poke_info = get_pokemon_info(pokemon)
    poke_name = get_pokemon_name(pokemon)

    dex_info = {
        "value": pokemon,
        "text": poke_name,
        "type": poke_info["type"].upper()
        }
    if "dualtype" in poke_info.keys() and poke_info["dualtype"] != 0:
        dex_info["dualtype"] = poke_info["dualtype"].upper()
    dex_info["evolve"] = evolution_paths
    dex_info["generation"] = 8
    dex_info["abilities"] = [poke_info['ability1'], poke_info['ability2'], poke_info['abilityH']]
    dex_info["dexNum"] = pokemon
    dex_info["form"] = 0
    if pokemon > 1010:
        for poke_form in diff_forms.keys():
            if poke_name in diff_forms[poke_form]:
                form_number = diff_forms[poke_form][4]
                og_num = diff_forms[poke_form][3]
        dex_info["dexNum"] = og_num
        dex_info["form"] = int(form_number)
        return dex_info

    return dex_info

def getPokedexInfo():
    pokedex = []
    start_time = time.time()
    evolutions = evolution_pathfinding()
    end_time = time.time()
    print("Pathfinding took:", end_time - start_time, "seconds")

    for pokemon in evolutions.keys():
        start_time = time.time()
        if pokemon >= 1456:
            continue
        evolution_path = evolutions[pokemon]["path"]
        if pokemon < 906 or pokemon > 1010:
            dex_info = get_mon_dex_info(pokemon, evolution_path)
        pokedex.append(dex_info)
        end_time = time.time()
        first_execution_list.append(end_time - start_time)

    with open(os.path.join(output_file_path, "pokedex_info.json"), "w", encoding="utf-8") as output:
        json.dump(pokedex, output, ensure_ascii=False, indent=2)
    return pokedex

def get_avg_time(times):
    return sum(times) / len(times)

if __name__ == "__main__":

    diff_forms = get_diff_form_dictionary()
    full_data = load_data()
    forms = GenForms()
    getPokedexInfo()

if __name__ != "__main__":
    diff_forms = get_diff_form_dictionary()
    full_data = load_data()