import os

def count_lines_of_code(directory):
    total_lines = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):  # consider only Python files, you can modify this condition accordingly
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    total_lines += sum(1 for line in f)
    return total_lines

if __name__ == "__main__":
    project_directory = os.path.dirname(os.path.realpath(__file__))  # get the directory of the current Python file
    lines_of_code = count_lines_of_code(project_directory)
    print("Total lines of code in the project:", lines_of_code)
