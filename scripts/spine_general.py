import os
import re
import shutil
import sys

source_directory = sys.argv[1] if sys.argv[1] else '.'

for item in os.listdir(source_directory):
    item_path = os.path.join(source_directory, item)

    # Delete files that have a # in their name
    if os.path.isfile(item_path) and '#' in item:
        print(f"Deleting file: {item}")
        os.remove(item_path)
        continue
    
    # Remove .prefab from all filenames
    if item.endswith(".prefab"):
        new_filename = item.rsplit(".prefab", 1)[0]
        old_path = os.path.join(source_directory, item)
        new_path = os.path.join(source_directory, new_filename)
        os.rename(old_path, new_path)
        print(f"Renamed: {item} to {new_filename}")
        item = new_filename

    # Organize files into their respective enemy folders
    enemy_name = re.split('[\.\[]', item)[0]
    enemy_folder = os.path.join(source_directory, enemy_name)
    if not os.path.exists(enemy_folder):
        os.makedirs(enemy_folder)
    source_path = os.path.join(source_directory, item)
    destination_path = os.path.join(enemy_folder, item)
    shutil.move(source_path, destination_path)

print("Files organized into respective enemy folders.")
