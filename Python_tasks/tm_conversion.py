import os
import json
import constants

from moveUtils import (
  get_tech_machine_learnset,
  convert_int_to_bit,
  personal_data
)
from pokemonUtils import get_mons_no_and_form_no

parent_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_file_path = os.path.join(parent_file_path, constants.INPUT_NAME)
debug_file_path = os.path.join(parent_file_path, "Python_tasks", constants.DEBUG_NAME)

def create_converted_tm_list():
  for pokemon in personal_data["Personal"]:
    if pokemon["id"] == 0:
      continue

    pokemonID = pokemon["id"]
    monsNo, formNo = get_mons_no_and_form_no(pokemonID)
    LearnedList = get_tech_machine_learnset(pokemonID, True)
    convertedInts = convert_int_to_bit(LearnedList)

    outputObj = {
      "set01" : 0,
      "set02" : 0,
      "set03" : 0,
      "set04" : 0,
      "set05" : 0,
      "set06" : 0,
      "set07" : 0,
      "set08" : 0,
    }

    outputObj["set01"] = convertedInts["machine1"]
    outputObj["set02"] = convertedInts["machine2"]
    outputObj["set03"] = convertedInts["machine3"]
    outputObj["set04"] = convertedInts["machine4"]

    current_filepath = os.path.join(debug_file_path, "tm_conversion", f'monsno_{monsNo}_formno_{formNo}.json')
    with open( current_filepath, 'w') as file:
      json.dump(outputObj, file, ensure_ascii=False, indent = 2)

if __name__ == "__main__":
  create_converted_tm_list()