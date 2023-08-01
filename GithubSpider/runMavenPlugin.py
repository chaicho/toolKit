import os
import subprocess
from database.csvHelper import *
from logger.loggerHelper import *
def remove_common_prefix(strings_list):
    if not strings_list:
        return strings_list

    common_prefix = os.path.commonprefix(strings_list)
    if common_prefix:
        return [s[len(common_prefix):] for s in strings_list]
    else:
        return strings_list

def get_all_folders(directory):
    folders = [folder for folder in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder))]
    return folders
  
def run_maven_command(project_dir, command):
    """
    Run a Maven command inside the given project directory.
    """
    try:
      mvn_command = f"mvn {command}"
      logging.info(f"Running maven command: {mvn_command} in project: {project_dir}")
      subprocess.run(mvn_command, shell=True, cwd=project_dir, check=True)
      return True
    except:
      print(f"Error in running maven command for project: {mvn_command}")
      return False
def has_maven_pom(project_dir):
    """
    Check if the directory contains a Maven POM file (pom.xml).
    """
    return "pom.xml" in os.listdir(project_dir)
def has_compiled_classes(project_dir):
    """
    Check if /target directory contains compiled classes.
    """
    target_dir = os.path.join(project_dir, 'target','classes')
    # print(target_dir)
    if not os.path.exists(target_dir):
        logging.warn("The 'target' directory does not exist.")
        return False

    # Recursively search for compiled class files in the 'target' directory and its subdirectories
    class_files_found = False
    for root, _, files in os.walk(target_dir):
        # print(files)
        class_files = [file for file in files if file.endswith('.class')]
        if class_files:
            logging.info(f"Found compiled class files in: {target_dir}")
            return True
    # logging.error(f"Compiled class files not found in the 'target' directory or its subdirectories.")
    # print("Compiled class files found in the 'target' directory or its subdirectories.")
    return False
             
    
def find_leaf_projects(root_dir):
    """
    Find leaf projects (directories with pom.xml and no child directories with pom.xml).
    """
    leaf_projects = []
    if not has_maven_pom(root_dir):
        return leaf_projects
    # print(f"Processing project in: {root_dir}")
    has_child_pom = False
    for sub_dir in get_all_folders(root_dir):
        # print(f"Processing project in subproject: {sub_dir}")
        if not has_maven_pom(os.path.join(root_dir, sub_dir)):
            continue
        has_child_pom = True
        leaf_projects.extend(find_leaf_projects(os.path.join(root_dir, sub_dir)))
    if not has_child_pom:
        leaf_projects.append(os.path.join(root_dir))    
    
    return leaf_projects

def main(root_dir):
    """
    Main function to traverse the directory and run Maven commands on leaf projects.
    """
    for project_dir in get_all_folders(root_dir):
      # print(f"dirs: {dirs}")
        # print(os.path.join(root_dir, project_dir))
        if not has_maven_pom(os.path.join(root_dir, project_dir)):
          print(f"Project {project_dir} does not have pom.xml.")
          continue
        if not has_compiled_classes(os.path.join(root_dir, project_dir)):
          print(f"Project {project_dir} does not have compiled classes.")
          continue
        run_maven_command(os.path.join(root_dir, project_dir), "install -DskipTests")
    
        leaf_projects = find_leaf_projects(os.path.join(root_dir, project_dir))
        leaf_projects = remove_common_prefix(leaf_projects)
        print(f"Found leaf projects: {leaf_projects}")

        for leaf_project_dir in leaf_projects:
            # print(f"Processing project in: {project_dir}")
            run_maven_command(os.path.join(root_dir, project_dir), f"-pl {leaf_project_dir}   DSchecker:DScheck")

def runOnRealProjects(root_root_dir):
    """
    Main function to traverse the directory and run Maven commands on leaf projects.
    """
    for root_dir in get_all_folders(root_root_dir):
      root_dir = os.path.join(root_root_dir, root_dir)
      for project_dir in get_all_folders(root_dir):
        logging.info(f"dirs: {project_dir}")
        # continue
        # print(f"dirs: {dirs}")
        # print(os.path.join(root_dir, project_dir))
        if not has_maven_pom(os.path.join(root_dir, project_dir)):
          continue
        install_result = run_maven_command(os.path.join(root_dir, project_dir), "install -DskipTests")
        if install_result == False:
          continue
        leaf_projects = find_leaf_projects(os.path.join(root_dir, project_dir))
        leaf_projects = remove_common_prefix(leaf_projects)
        logging.info(f"Found leaf projects: {leaf_projects}")
        
        for leaf_project_dir in leaf_projects:
            # print(f"Processing project in: {project_dir}")
            run_maven_command(os.path.join(root_dir, project_dir), f"-pl {leaf_project_dir}   DSchecker:DScheck")

  
if __name__ == "__main__":
    loggingconfig()
    # Replace 'your_root_dir_here' with the path to the directory containing your Java projects.
    # main("/root/dependencySmell/evaluation/actualSmells/maven")
    # main("")
    # print(has_compiled_classes("/root/dependencySmell/evaluation/actualSmells/libraryVersionConflict/matsim-libs-e88c281b5356597b1a889b16854fa43f61496873/examples"))
    runOnRealProjects("/root/dependencySmell/evaluation/realProjects/projectsDir/")
