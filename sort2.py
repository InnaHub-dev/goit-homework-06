import os
import re
import shutil
import sys 
from pathlib import Path
import glob 


REG_NORMALIZE = re.compile(r'(?!(\.[a-z0-9]{3,4}))[^0-9a-zA-Za-яА-Яіїґ_]')
REG_EXTENTION = re.compile(r'(?!\.)\w+$') 

CYRILLIC = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

ARCHIVES = 'archives'

SORTING_DICT = {'images':['jpeg', 'png', 'jpg', 'svg'],'video':['avi', 'mp4', 'mov', 'mkv'],'documents':['doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx'],'music':['mp3', 'ogg', 'wav', 'amr'], ARCHIVES:['zip', 'gz', 'tar']}


def normalize(string: str, translist1: list, translist2: list) -> str:

  '''Function normalizes the string according to regex and translates the string using two lists.

  Returns translated string.
  '''
 
  letter_string = re.sub(REG_NORMALIZE, '_', string)
  TRANS = {ord(c.upper()): l.upper() for c, l in zip(translist1, translist2)}
  TRANS.update({ord(c) : l for c, l in zip(translist1, translist2)})
  trans_string = letter_string.translate(TRANS)

  return trans_string 




directory = Path('/Users/inna/Documents/Test-folder')

exclude_list = []

for key in SORTING_DICT.keys():

    folder_path = directory/key
    exclude_list.append(folder_path)
    

exclude = '|'.join(key for key in SORTING_DICT.keys())

print(exclude)

files_folders = list(directory.rglob('[!.]*'))


folders = [p for p in directory.rglob('*') if p.is_dir()]



all_files = directory.rglob('[!.]*')

all_files_string = [str(f) for f in all_files]

# multiple conditions are joined with | in re. eg a|b matches a and b.
# filter the results using re.
filtered_list = list(filter(lambda x: not re.search(exclude, x), all_files_string))


x = re.search('inna', str(directory))
print(x)


