from PIL import Image
from fastapi.responses import RedirectResponse
import base64, io, numpy as np, matplotlib.pyplot as plt
from .files_utils import is_temp_under_limits, delete_first_plot

def convert_img_to_bytes():
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.read()).decode('utf-8')
    plt.close()

    return {"image": f"data:image/png;base64,{img_base64}"}

def save_img(file_path:str):

    if is_temp_under_limits(): delete_first_plot()

    fig = plt.gcf()
    fig_size_inch = fig.get_size_inches()
    fig_size_px = fig_size_inch * fig.dpi
    fig_size_px = fig_size_px.astype(np.int32)
    image = Image.new('RGB', (fig_size_px[0],fig_size_px[1]), color = (255, 255, 255))
    image.save(file_path)

    plt.savefig(file_path)
    plt.close()
    return RedirectResponse(url=file_path[1:])