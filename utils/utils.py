import matplotlib.pyplot as plt

from fastapi.responses import RedirectResponse
from fastapi import HTTPException

import io
import base64
import numpy as np

import os
from PIL import Image

def format_time_mmssmmm(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:06.3f}"

def convert_img_to_bytes():
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.read()).decode('utf-8')
    plt.close()

    return {"image": f"data:image/png;base64,{img_base64}"}

def save_img():
    file_path = "./temp/plot_saved.png"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if os.path.exists(file_path):
        os.remove(file_path)
    fig = plt.gcf()
    if fig.get_axes():
        plt.savefig(file_path, dpi=fig.dpi, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return RedirectResponse(url="/temp/plot_saved.png")
        else:
            raise HTTPException(status_code=500, detail="Error al guardar la imagen")
    else:
        plt.close()
        raise HTTPException(status_code=500, detail="No hay gráfico para guardar")

def send_error_message(status_code, title, message):
    raise HTTPException(
        status_code= status_code,
        detail={
            "error": title,
            "message": message,
        }
    )

def get_info_drivers(pilotos_info):
    vueltas_pilotos_dict = {}
    if not pilotos_info: return vueltas_pilotos_dict

    strings_vualtas_pilotos = pilotos_info.split("/vs/")
    for string in strings_vualtas_pilotos:
        info = string.split("/")
        vueltas_pilotos_dict[info[0]] = list(map(int, info[1:]))
    
    return vueltas_pilotos_dict