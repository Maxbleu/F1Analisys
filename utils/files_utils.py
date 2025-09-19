import os

def remove_all_temp_plots():
    directory_path = "./temp/"
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

def is_temp_under_limits():
    directory_path = "./temp/"
    try:
        files = [f for f in os.listdir(directory_path) 
                if os.path.isfile(os.path.join(directory_path, f))]
        return len(files) == 25
    except FileNotFoundError:
        return False

def delete_first_plot():
    directory_path = "./temp/"
    os.remove(os.path.join(directory_path, os.listdir(directory_path)[0]))