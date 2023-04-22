from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from PIL import Image
import qrcode
import os
import io

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    message = request.form.get('message')

    if uploaded_file and message:
        filename = uploaded_file.filename
        filepath = os.path.join('uploads', filename)
        uploaded_file.save(filepath)

        # Create a QR code with the message as the link
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(message)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_size = (300, 300)  # Adjust the size of the QR code if necessary
        qr_img = qr_img.resize(qr_size)
        margin = 3  # Add a margin around the QR code
        qr_img_with_margin = Image.new('RGB', (qr_size[0] + margin * 2, qr_size[1] + margin * 2), color='white')
        qr_img_with_margin.paste(qr_img, (margin, margin))

        # Open the uploaded image and overlay the QR code on the right bottom corner
        image = Image.open(filepath)
        image.paste(qr_img, (image.width - qr_img.width, image.height - qr_img.height))

        # Save the modified image to a BytesIO buffer
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        os.remove('./uploads/'+filename)
        # Return the modified image as a downloadable file
        return send_file(buffer, mimetype="image/png", as_attachment=True, download_name="image_with_qr.png")
    else:
        return jsonify(error="Invalid file or message"), 400

if __name__ == '__main__':
    app.run(debug=True)
