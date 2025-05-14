from flask import Flask, request, send_file
import io
from PIL import Image
from rembg import remove
import os  # Import pour gérer les variables d'environnement

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

    # Redimensionner l'image à une taille maximale de 1024x1024 pour économiser de la mémoire
    img.thumbnail((1024, 1024))

    # Sauvegarder l'image redimensionnée en mémoire avec une compression PNG
    buffered = io.BytesIO()
    img.save(buffered, format="PNG", optimize=True)
    img_bytes = buffered.getvalue()

    # Utiliser rembg pour retirer le fond de l'image
    img_bytes = remove(img_bytes)

    # Recharger l'image traitée
    img_rgba = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    
    # Créer un fond blanc et y insérer l'image sans fond
    background = Image.new("RGB", img_rgba.size, (255, 255, 255))
    background.paste(img_rgba, mask=img_rgba.split()[3])

    # Sauvegarder l'image sans fond en JPEG avec une compression de qualité 80
    out_buffer = io.BytesIO()
    background.save(out_buffer, format="JPEG", quality=80)
    out_buffer.seek(0)

    return send_file(out_buffer, mimetype='image/jpeg', download_name='image_sans_fond.jpg')

if __name__ == '__main__':
    # Récupérer le port depuis la variable d'environnement PORT
    port = int(os.environ.get("PORT", 5000))  # Si la variable PORT n'est pas définie, utiliser le port 5000 par défaut
    app.run(host="0.0.0.0", port=port)
