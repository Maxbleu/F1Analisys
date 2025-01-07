import matplotlib.pyplot as plt
import io
import base64

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

    return img_base64