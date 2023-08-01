import csv
import os

class CsvProjectHelper:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        if not os.path.isfile(self.csv_file):
            with open(self.csv_file, 'w+', newline='') as csvfile:
                fieldnames = ['project_name', 'version']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
    def is_downloaded(self, project_name, version):
        with open(self.csv_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['project_name'] == project_name and row['version'] == version:
                    return True
        return False

    def mark_downloaded(self, project_name, version):
        with open(self.csv_file, 'a', newline='') as csvfile:
            fieldnames = ['project_name', 'version']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'project_name': project_name, 'version': version})


if __name__ == '__main__':
    csv_helper = CsvProjectHelper('projects.csv')

    print(csv_helper.is_downloaded('a', '1'))  # Output: False

    csv_helper.mark_downloaded('a', '1')

    print(csv_helper.is_downloaded('a', '1'))  # Output: True
    print(csv_helper.is_downloaded('a', '2'))  # Output: False
