import os
import re
import shutil
import sys 
from pathlib import Path


REG_NORMALIZE = re.compile(r'(?!(\.[a-z0-9]{3,4}))[^0-9a-zA-Za-яА-Яіїґ_]')
REG_EXTENTION = re.compile(r'(?!\.)\w+$') 

CYRILLIC = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

ARCHIVES = 'archives'

SORTING_DICT = {'images':['jpeg', 'png', 'jpg', 'svg', 'psd'],'video':['avi', 'mp4', 'mov', 'mkv'],'documents':['doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx'],'music':['mp3', 'ogg', 'wav', 'amr'], ARCHIVES:['zip', 'gz', 'tar']}


def create_sorted_dict(sorting_dictionary: dict) -> dict:

  """Function createds a dictionary for sorted files ."""
   
  sorted_dict = {}

  for key in sorting_dictionary.keys():
    sorted_dict.update({key:[]})
  
  return sorted_dict


def exclude_directories(paths: list, sorting_dictionary) -> list:

  exclude = '|'.join(key for key in sorting_dictionary.keys())  
  paths = [str(f) for f in paths]
  filtered_path_strings = list(filter(lambda x: not re.search(exclude, x), paths))
  filtered_paths = [Path(f) for f in filtered_path_strings]

  return filtered_paths
          

def file_category(path: Path, sorting_dict: dict) -> str:

  '''Function gets the file category by extention in keys of sorting_dict.

  Returns category name.
  '''

  extention = path.suffix.split('.')[1]

  for key,values in sorting_dict.items():

    if extention in values: 
        return key 
    

def normalize(string: str, translist1: list, translist2: list) -> str:

  '''Function normalizes the string according to regex and translates the string using two lists.

  Returns translated string.
  '''
 
  letter_string = re.sub(REG_NORMALIZE, '_', string)
  TRANS = {ord(c.upper()): l.upper() for c, l in zip(translist1, translist2)}
  TRANS.update({ord(c) : l for c, l in zip(translist1, translist2)})
  trans_string = letter_string.translate(TRANS)

  return trans_string 


def remove_empty_folders(folder_paths_list: list) -> None:

  '''Function sorts the folders by their depth and removes the empty deepest ones first. 
  
  Ignores the hidden files.
  '''

  folder_paths_list.sort(key = lambda f: -len(list(f.parents))) 

  for path in folder_paths_list:

    if len(list(path.glob('?*.*'))) == 0:
        shutil.rmtree(path)


def rename_tree(directory: Path, Flag) -> None:


  '''Function iterates through files and folders in a given directory

  Flag = True ignores folders that have same names and keys in sorting dictionary.
  '''

  dir_content = list(directory.rglob('[!.]*'))

  if Flag == True:
     
     dir_content = exclude_directories(dir_content, SORTING_DICT)
  
  dir_content.sort(key = lambda f: -len(f.parents))

  for f in dir_content:
      new_name = normalize(f.stem, CYRILLIC, TRANSLATION)
      new_obj_path = f.parent/f'{new_name}{f.suffix}'
      f.rename(new_obj_path)

def unpack_archive_to_subfolder(archive_folder: Path, archive_name: Path, extention: str) -> None:


  folder_to_unpack = archive_folder/archive_name.stem
  folder_to_unpack.mkdir()
  shutil.unpack_archive(archive_name, folder_to_unpack, extention)


def main(Flag = True):

  '''Script renames the files and folders, sorts the files in the given directory to folders specified as keys in a sorting dictionary, removes empty folders and prints the found files and their extentions by categories.

  By default it ignores the sorting folders, but you may include them in a sorting process by changing Flag to False.
  '''

  #directory = Path('/Users/inna/Documents/Test-folder')

  directory = sys.argv[1]
  directory = Path(directory)

  if not directory.exists():
     print("Sorry, such directory doesn't exist")
     return 

  for key in SORTING_DICT.keys():
    
    try: 

      folder_path = directory/key
      folder_path.mkdir()
      
    except FileExistsError:
        print(f'Folder "{key}" exists')

  rename_tree(directory, Flag) 

  files = [p for p in directory.rglob('?*.*') if p.is_file()]
  folders = [p for p in directory.rglob('*') if p.is_dir()]
   
  if Flag == True:
      
      files = exclude_directories(files, SORTING_DICT)
      folders = exclude_directories(folders, SORTING_DICT)

 # move files to folders and sort

  sorted_dict = create_sorted_dict(SORTING_DICT)
  known_extentions = set()
  unknown_extentions = set()

  for path in files:

    file_cat = file_category(path, SORTING_DICT)
    extention = path.suffix.split('.')[1]
    
    if not file_cat == None:
      known_extentions.add(extention)
      sorted_dict[file_cat].append(path.name)

      try: 

          shutil.move(path, directory/file_cat)
        
      except FileExistsError:
          print(f"An object with {path} already exists.")

      except FileNotFoundError:
          print(f'No "{file_cat}" folder in {directory}')
      
      except TypeError:
          print(f'{file_cat} category is unknown')

      except shutil.Error:
          print(f'Destination {directory/file_cat}/{path} already exists')
    
    else:
      unknown_extentions.add(extention)

  remove_empty_folders(folders)

  archive_folder = directory/ARCHIVES

  for obj in archive_folder.glob('?*.*'):

    extention = obj.suffix.split('.')[1]

    if extention in SORTING_DICT[ARCHIVES]:
  
      try:
          unpack_archive_to_subfolder(archive_folder, obj, extention)

      except FileExistsError:
        print(f"This {obj} folder already exists")

      except shutil.ReadError:
         print("This archive couldn't be unpacked.")

  print('Known extentions: ', known_extentions)
  print('Unknown extentions: ', unknown_extentions)
  print('Files by categories: ', sorted_dict)

if __name__ == '__main__':
   main()


