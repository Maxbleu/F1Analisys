from PIL import Image
from fastapi import Request
from .path_utils import get_path_temp_plot
from .fastf1_utils import get_request_data
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

def get_return(request: Request, convert_to_bytes: bool = False, get_url: bool = False):
    obj_return = None
    type_event, analisys, year, event, session = get_request_data(request=request)
    file_path = get_path_temp_plot(type_event=type_event,analisis=analisys,year=year,round=event,session=session)
    if (not convert_to_bytes) and (not get_url):
        obj_return = save_img(file_path)
    elif convert_to_bytes:
        obj_return = convert_img_to_bytes()
    elif get_url:
        file_name = file_path.split("/")[-1]
        obj_return = {"url":request.url_for("temp", path=file_name)._url}
    return obj_return