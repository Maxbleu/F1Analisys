import matplotlib.pyplot as plt
from fastapi.responses import RedirectResponse

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
    if os.path.exists(file_path):
        os.remove(file_path)

    fig = plt.gcf()
    fig_size_inch = fig.get_size_inches()
    fig_size_px = fig_size_inch * fig.dpi
    fig_size_px = fig_size_px.astype(np.int32)
    image = Image.new('RGB', (fig_size_px[0],fig_size_px[1]), color = (255, 255, 255))
    image.save(file_path)

    plt.savefig(file_path)
    plt.close()
    return RedirectResponse(url="/temp/plot_saved.png")

def format_time_mmssmmm(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:06.3f}"