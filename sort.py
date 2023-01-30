import glob 
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

SORTING_DICT = {'images':['jpeg', 'png', 'jpg', 'svg'],'video':['avi', 'mp4', 'mov', 'mkv'],'documents':['doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx'],'music':['mp3', 'ogg', 'wav', 'amr'], ARCHIVES:['zip', 'gz', 'tar']}


def categorize_files(files: list[Path], sorting_dictionary: dict) -> tuple[dict, dict]:

  """Function categorizes files by sorting_dictionary categories.
  
  Returns two dictionaries: sorted_dict - with all the files by categories, \
  and extentions - known and unknown extentions."""
    
  sorted_dict = create_sorted_dict(sorting_dictionary)
  extentions = {'known':set(), 'unknown':set()}

  for file in files:
      
      file_cat = file_category(file, sorting_dictionary)
      extention = file.suffix.split('.')[1]

      if file_cat != None:
        sorted_dict.update({file_cat:file.name})
        extentions['known'].add(extention)

      else: 
        sorted_dict.update({'unknown':file.name})
        extentions['unknown'].add(extention)
  
  return sorted_dict, extentions


def create_sorted_dict(sorting_dictionary: dict) -> dict:

  """Function creates a dictionary for sorted files."""
   
  sorted_dict = {}

  for key in sorting_dictionary.keys():
    sorted_dict.update({key:[]})
  
  sorted_dict.update({'unknown':[]})
  
  return sorted_dict


def create_sorting_folders(directory: Path, names: list) -> None:

  """Function creates new folders."""

  for name in names:
    
    try: 

      folder_path = directory/name
      folder_path.mkdir()
      
    except FileExistsError:
        print(f'Folder "{name}" exists')


def exclude_directories(paths: list, sorting_dictionary: dict) -> list:

  exclude = '|'.join(key for key in sorting_dictionary.keys())  
  paths = [str(f) for f in paths]
  filtered_path_strings = list(filter(lambda x: not re.search(exclude, x), paths))
  filtered_paths = [Path(f) for f in filtered_path_strings]

  return filtered_paths
          

def file_category(path: Path, sorting_dictionary: dict) -> str:

  '''Function gets the file category by extention in keys of sorting_dictionary.

  Returns category name.
  '''

  extention = path.suffix.split('.')[1]

  for key,values in sorting_dictionary.items():

    if extention in values: 
        return key
  
def get_objects_in_dir(directory: Path, type_of_obj: str, Flag: bool) -> list:
    
    """Function gets a list of objects from a given directory.
    
  Parameters:
    directory: a path to a directory to create folders in
    type_of_obj: can take two forms - 'files' or 'folders'.
  """
    match type_of_obj:
       
      case 'files':
          objects = [p for p in directory.rglob('?*.*') if p.is_file()]
      case 'folders':
          objects = [p for p in directory.rglob('*') if p.is_dir()]
    
    if Flag == True:
       objects = exclude_directories(objects, SORTING_DICT)

    return objects
    

def normalize(string: str, translist1: list, translist2: list) -> str:

  '''Function normalizes the string according to regex and translates the string using two lists.

  Returns translated string.
  '''
 
  letter_string = re.sub(REG_NORMALIZE, '_', string)
  TRANS = {ord(c.upper()): l.upper() for c, l in zip(translist1, translist2)}
  TRANS.update({ord(c) : l for c, l in zip(translist1, translist2)})
  trans_string = letter_string.translate(TRANS)

  return trans_string 


def remove_empty_folders(folder_paths_list: list[Path]) -> None:

  '''Function sorts the folders by their depth and removes the empty deepest ones first. 
  
  Ignores the hidden files.
  '''

  folder_paths_list.sort(key = lambda f: -len(list(f.parents))) 

  for path in folder_paths_list:

    if len(list(path.glob('?*.*'))) == 0:
        shutil.rmtree(path)


def rename_tree(directory: Path, Flag) -> None:

  '''Function iterates through files and folders in a given directory.

  Flag = True ignores folders that have the same names as keys in a sorting dictionary.
  '''

  dir_content = list(directory.rglob('[!.]*'))

  if Flag == True:
     
     dir_content = exclude_directories(dir_content, SORTING_DICT)
  
  dir_content.sort(key = lambda f: -len(f.parents))

  for f in dir_content:
      new_name = normalize(f.stem, CYRILLIC, TRANSLATION)
      new_obj_path = f.parent/f'{new_name}{f.suffix}'
      f.rename(new_obj_path)


def sort_and_move_files(files: list[Path], directory: Path, sorting_dictionary: dict) -> None:

  """Function checks if a file belongs to any category in a sorting_dictionary and moves it to the sorting folder.

  If the file isn't in any category, does nothing.
  """

  for path in files:
    file_cat = file_category(path, sorting_dictionary)
    
    if not file_cat == None:

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


def unpack_archive_to_subfolder(directory: Path, archive_name: Path, extention: str) -> None:


  folder_to_unpack = directory/archive_name.stem
  folder_to_unpack.mkdir()
  shutil.unpack_archive(archive_name, folder_to_unpack, extention)


def unpack_archives_in_dir(directory: Path, extentions: list) -> None:
  
  for obj in directory.glob('?*.*'):
    extention = obj.suffix.split('.')[1]

    if extention in extentions:

      try:
          unpack_archive_to_subfolder(directory, obj, extention)

      except FileExistsError:
        print(f"This {obj} folder already exists")

      except shutil.ReadError:
        print("This archive couldn't be unpacked.")


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

  names = list(SORTING_DICT.keys())
  create_sorting_folders(directory, names)

  rename_tree(directory, Flag) 

  files = get_objects_in_dir(directory, 'files', Flag)
  folders = get_objects_in_dir(directory, 'folders', Flag)

  sort_and_move_files(files, directory, SORTING_DICT)

  remove_empty_folders(folders)

  archive_folder = directory/ARCHIVES 
  extentions = SORTING_DICT[ARCHIVES]
  unpack_archives_in_dir(archive_folder, extentions)

  sorted_dict, extentions = categorize_files(files, SORTING_DICT)

  print(sorted_dict)
  print(extentions)

if __name__ == '__main__':
   main()


