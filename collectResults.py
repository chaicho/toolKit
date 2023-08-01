import os
import shutil

def collect_ds_results(target_directory, destination_directory):
    # Create the destination directory if it doesn't exist
    os.makedirs(destination_directory, exist_ok=True)

    for root, _, files in os.walk(target_directory):
        for filename in files:
            if filename == "DScheckerResult.txt":
                src_path = os.path.join(root, filename)
                dest_path = os.path.join(destination_directory, os.path.relpath(src_path, target_directory))
                print(f"Copying {src_path} to {dest_path}")
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(src_path, dest_path)

if __name__ == "__main__":
    target_directory = "/root/dependencySmell/evaluation/actualSmells/allProjects"  # Change this to the target directory you want to search
    destination_directory = os.path.join(target_directory,"/collectedResults/")  # Change this to the desired destination directory

    collect_ds_results(target_directory, destination_directory)
    print("All DScheckerResult.txt files have been collected and stored in", destination_directory)
