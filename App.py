from flask import Flask, request, send_file
import io
from PIL import Image
from rembg import remove

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <h1>Upload une image</h1>
    <form method="post" action="/process" enctype="multipart/form-data">
        <input type="file" name="image">
        <input type="submit" value="Envoyer">
    </form>
    '''

@app.route('/process', methods=['POST'])
def process():
    if 'image' not in request.files:
        return 'Pas de fichier image', 400

    img_file = request.files['image']
    img = Image.open(img_file).convert("RGBA")

    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = remove(buffered.getvalue())

    img_rgba = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    background = Image.new("RGB", img_rgba.size, (255, 255, 255))
    background.paste(img_rgba, mask=img_rgba.split()[3])

    out_buffer = io.BytesIO()
    background.save(out_buffer, format="JPEG", quality=80)
    out_buffer.seek(0)

    return send_file(out_buffer, mimetype='image/jpeg', download_name='image_sans_fond.jpg')
