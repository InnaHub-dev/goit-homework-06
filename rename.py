import re
from pathlib import Path

REG_NORMALIZE = re.compile(r'(?!(\.[a-z0-9]{3,4}))[^0-9a-zA-Za-яА-Яіїґ_]')

CYRILLIC = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")


def exclude_directories(paths: list, sorting_dictionary: dict) -> list:

  exclude = '|'.join(key for key in sorting_dictionary.keys())  
  paths = [str(f) for f in paths]
  filtered_path_strings = list(filter(lambda x: not re.search(exclude, x), paths))
  filtered_paths = [Path(f) for f in filtered_path_strings]

  return filtered_paths


def normalize(string: str, translist1: list, translist2: list) -> str:

  '''Function normalizes the string according to regex and translates the string using two lists.

  Returns translated string.
  '''
 
  letter_string = re.sub(REG_NORMALIZE, '_', string)
  TRANS = {ord(c.upper()): l.upper() for c, l in zip(translist1, translist2)}
  TRANS.update({ord(c) : l for c, l in zip(translist1, translist2)})
  trans_string = letter_string.translate(TRANS)

  return trans_string 


def rename_tree(directory: Path, *sorting_dictionary: dict, Flag = False) -> None:

  '''Function iterates through files and folders in a given directory.

  Flag = True ignores folders that have the same names as keys in a sorting dictionary.
  '''

  dir_content = list(directory.rglob('[!.]*'))

  if Flag == True:
     
     dir_content = exclude_directories(dir_content, sorting_dictionary)
  
  dir_content.sort(key = lambda f: -len(f.parents))

  for f in dir_content:
      new_name = normalize(f.stem, CYRILLIC, TRANSLATION)
      new_obj_path = f.parent/f'{new_name}{f.suffix}'
      f.rename(new_obj_path)


