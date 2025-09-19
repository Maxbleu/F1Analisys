import os

def get_info_drivers(pilotos_info):
    vueltas_pilotos_dict = {}
    if not pilotos_info: return vueltas_pilotos_dict

    strings_vualtas_pilotos = pilotos_info.split("/vs/")
    for string in strings_vualtas_pilotos:
        info = string.split("/")
        vueltas_pilotos_dict[info[0]] = list(map(int, info[1:]))
    
    return vueltas_pilotos_dict

def get_path_temp_plot(type_event:str, analisis:str, year:int, round:int, session:str):
    return f"./temp/plot_{type_event}_{analisis}_{year}_{round}_{session}.png"

def exists_plot_in_temp(file_path):
    return os.path.exists(path=file_path)