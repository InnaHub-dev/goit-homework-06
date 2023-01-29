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

SORTING_DICT = {'images':['jpeg', 'png', 'jpg', 'svg', 'psd',],'video':['avi', 'mp4', 'mov', 'mkv'],'documents':['doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx'],'music':['mp3', 'ogg', 'wav', 'amr'], ARCHIVES:['zip', 'gz', 'tar']}



def categorize_files(sorting_dictionary: dict, file_path_list: list) -> dict:

  '''Function categorizes files.
  
  Function takes a sorting dictionary with keys as categories in format {key:[extention1, extention2, etc.]}, and a list of files. Adds 'unknown' category if the category isn't in the sorting dictionary.

  Returns a sorted dictionary with all the files by categories and a list of all found extentions.
  '''

  sorted_dict = {}
  sorted_dict.update({'unknown':[[],[]]})

  for key in sorting_dictionary.keys():
    sorted_dict.update({key:[[],[]]})

  for path in file_path_list:

    file_cat = file_category(path, sorting_dictionary)
    extention = get_extention(path)

    if file_cat == None:  
      file_cat = 'unknown'

    sorted_dict[file_cat][0].append(os.path.basename(path))
    sorted_dict[file_cat][1].append(extention)
  
  return sorted_dict
         
  
def create_folder(directory, folder_name):
  
  folder_path = directory/folder_name
  folder_path.mkdir()

  return folder_path


def file_category(path, sorting_dict):

  '''Function gets the file category by extention in keys of sorting_dict.

  Returns category name.
  '''

  extention = path.suffix.split('.')[1]

  for key,values in sorting_dict.items():

    if extention in values: 
        return key 
    

def rename_tree(directory, sorting_folders):


  '''Function iterates through files and folders in a given directory

  Parameters: Flag = True ignores folders that have same names and keys in sorting dictionary

  Unlike os.walk() it may exclude not only certain folders but also their subfolders.

  Returns 2 dictionaris of filenames and their paths and folders and their paths.
  '''

  files_list = []
  folders_list = []
  dir_content = directory.iterdir()

  if sorting_folders:

    dir_content = set(dir_content) - set(sorting_folders)
  
  for obj in dir_content:

    if not obj.stem.startswith('.'):

      new_obj = rename_object(obj, directory, CYRILLIC, TRANSLATION)
   
      if new_obj.is_file(): 
          files_list.append(new_obj)
    
      elif new_obj.is_dir():
        folders_list.append(new_obj)
        files,folders = rename_tree(new_obj, sorting_folders)
        files_list.extend(files)
        folders_list.extend(folders)
    
  return files_list, folders_list


def is_extention_in_cat(sorting_dictionary, category, object):

  obj_extention = object.suffix.split('.')[1]

  if obj_extention in sorting_dictionary[category]:

    return obj_extention
  

def normalize(string, translist1, translist2):

  '''Function normalizes the string according to regex and translates the string using two lists.

  Returns translated string.
  '''
 
  letter_string = re.sub(REG_NORMALIZE, '_', string)
  TRANS = {ord(c.upper()): l.upper() for c, l in zip(translist1, translist2)}
  TRANS.update({ord(c) : l for c, l in zip(translist1, translist2)})
  trans_string = letter_string.translate(TRANS)

  return trans_string 


def rename_object(path, directory, translist1, translist2): 
  
  '''Function renames an iterable object.

  Returns a new object path to a file with changed name.
  '''

  new_name = normalize(path.stem, translist1, translist2)
  new_obj_path = directory/f'{new_name}{path.suffix}'
  path.rename(new_obj_path)

  return new_obj_path
  

def unpack_archive_to_subfolder(archive_folder, archive_name, extention):


  folder_to_unpack = archive_folder/archive_name.split(f'.{extention}')[0]
  folder_to_unpack.mkdir()
  shutil.unpack_archive(archive_name,folder_to_unpack,extention)


def main():

  '''Script renames the files and folders, sorts the files in the given directory to folders specified as keys in a sorting dictionary, removes empty folders and prints the found files and their extentions by categories.

  By default it ignores the sorting folders, but you may include them in a sorting process by changing Flag to False in get_path_from_user().
  '''

  directory = Path('/Users/inna/Documents/Test-folder')

  sorting_folders = {}

  for key in SORTING_DICT.keys():
    
    try:  
        create_folder(directory, key)
      
    except FileExistsError:
        print(f'Folder "{key}" exists')

    folder_path = directory/key
    sorting_folders.update({key:folder_path})
  
  folders_paths = sorting_folders.values()
 
  #directory = sys.argv[1]
  files,folders = rename_tree(directory, folders_paths) 
  print(folders)
  

  # sorted_dict = categorize_files(SORTING_DICT, files)
  # print(sorted_dict)


  # move files to folders

  for path in files:

    file_cat = file_category(path, SORTING_DICT)
    
    if not file_cat == None:

      try: 

          shutil.move(path, sorting_folders[file_cat])
        
      except FileExistsError:
          print(f"An object with {path} already exists.")

      except FileNotFoundError:
          print(f'No "{file_cat}" folder in {directory}')
      
      except TypeError:
          print(f'{file_cat} category is unknown')

      except shutil.Error:
          print(f'Destination {sorting_folders[file_cat]}/{path} already exists')


  #remove empty folders
  folders.sort(key = lambda f: -len(list(f.parents)))
  print(list(folders))
  for path in folders:
    
    print(len(os.listdir(path)))
    content = os.listdir(path)
    if len(os.listdir(path)) == 0 or all(c.startswith('.') for c in content):
        shutil.rmtree(path)

  # #unpack archives

  # archive_folder = os.path.join(directory, ARCHIVES)

  # for obj in os.listdir(archive_folder):
    
  #   obj_extention = is_extention_in_cat(SORTING_DICT, ARCHIVES, obj)
  #   path = os.path.join(directory,obj)

  #   try:
  #       unpack_archive_to_subfolder(archive_folder, obj, obj_extention)

  #   except FileExistsError:
  #     print(f"This {obj} folder already exists")
      

if __name__ == '__main__':
   main()


