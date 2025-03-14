from flask import Flask, request, jsonify, send_file, render_template, url_for
import os
import cv2
import numpy as np
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'static/processed'  # Store processed images in `static/processed/`
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Function to preprocess image and detect document
def process_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    if len(contours) == 0:
        return None

    document_contour = contours[0]

    # Approximate contour to get 4 corners
    epsilon = 0.02 * cv2.arcLength(document_contour, True)
    corners = cv2.approxPolyDP(document_contour, epsilon, True)

    if len(corners) != 4:
        return None

    # Perspective transform
    return warp_perspective(image, corners)

# Function to apply perspective transformation
def warp_perspective(image, corners):
    corners = np.squeeze(corners)
    rect = np.array([corners[0], corners[1], corners[2], corners[3]], dtype="float32")

    width, height = 600, 800
    dst = np.array([[0, 0], [width-1, 0], [width-1, height-1], [0, height-1]], dtype="float32")

    # Compute the perspective transform matrix
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (width, height))

    return warped

# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle image upload and processing
@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({"message": "No image file received"}), 400

    image_file = request.files['image']
    file_path = os.path.join(UPLOAD_FOLDER, 'captured_book.jpg')
    image_file.save(file_path)

    processed_image = process_image(file_path)
    if processed_image is None:
        return jsonify({"message": "No book page detected. Try again!"})

    # Save the processed image
    processed_path = os.path.join(PROCESSED_FOLDER, 'scanned_document.jpg')
    cv2.imwrite(processed_path, processed_image)

    # Convert OpenCV image to PIL and save as PDF
    processed_pil = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
    pdf_path = os.path.join(PROCESSED_FOLDER, 'scanned_document.pdf')
    processed_pil.save(pdf_path)

    return jsonify({
        "message": "Book page scanned successfully!",
        "pdf_url": url_for('download', _external=True),
        "processed_image_url": url_for('static', filename='processed/scanned_document.jpg', _external=True)
    })

# Route to download the scanned PDF
@app.route('/download')
def download():
    return send_file(os.path.join(PROCESSED_FOLDER, 'scanned_document.pdf'), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
