from flask import Blueprint, request, send_file
from PIL import Image
from io import BytesIO
from .data import get_image

bp = Blueprint("bp", __name__)

@bp.route("/image")
def image():
    img1 = get_image(int(request.args["a"])).transpose(Image.FLIP_LEFT_RIGHT)
    img2 = get_image(int(request.args["b"]))
    img = Image.new("RGBA", (360, 180))
    img.paste(img1.resize((180, 180)), (0, 0))
    img.paste(img2.resize((180, 180)), (180, 0))

    fp = BytesIO()
    img.save(fp, "PNG")
    fp.seek(0)
    return send_file(fp, mimetype="image/png")
