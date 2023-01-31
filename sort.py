import shutil
import sys
from pathlib import Path

from rename import normalize


SORTING_DICT = {
    "images": [".jpeg", ".png", ".jpg", ".svg"],
    "video": [".avi", ".mp4", ".mov", ".mkv"],
    "documents": [".doc", ".docx", ".txt", ".pdf", ".xlsx", ".pptx"],
    "music": [".mp3", ".ogg", ".wav", ".amr"],
    "archives": [".zip", ".gz", ".tar"],
}

def move_category_file(dir: Path, file: Path, category: str):
  category_path = dir.joinpath(category)
  if not category_path.exists():
    category_path.mkdir()
  file.replace(category_path.joinpath(f'{normalize(file.stem)}{file.suffix}'))



def sort_and_move_files(
    directory: Path, sorting_dictionary: dict
) -> None:

    """Function checks if a file belongs to any category in a sorting_dictionary and moves it to the sorting folder.

    If the file isn't in any category, does nothing.
    """

    for file in directory.glob('**/*.*'):
      transfer = False
      
      for k, v in sorting_dictionary.items():
        if file.suffix.lower() in v:
          move_category_file(directory, file, k)
          transfer =True
          break
        
      if not transfer:
        move_category_file(directory, file, 'other')
        
        
def get_sort_dir() -> Path:
  try:
    path = Path(sys.argv[1])
  except IndexError:
    raise IndexError('Sorry, you did not enter the path to the folder.')
  
  if not path.exists():
      raise TypeError("Sorry, this folder dos not exist")

  return path
  

def main():

    """Script renames the files and folders, sorts the files in the given directory to folders specified as keys in a sorting dictionary, removes empty folders and prints the found files and their extentions by categories.

    By default it ignores the sorting folders, but you may include them in a sorting process by changing flag to False.
    """
    try:
      sort_dir = get_sort_dir()
    except IndexError as e:
      return e
    except TypeError as e:
      return e

    sort_and_move_files(sort_dir, SORTING_DICT)

if __name__ == "__main__":
    print(main())
