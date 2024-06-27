from flask import Flask, request, jsonify
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image
import os
import requests
from io import BytesIO

app = Flask(__name__)

# Output folder for intermediate images
output_folder = 'F:\Document data\Income Proof Testing Data\All Match\combined_image'
os.makedirs(output_folder, exist_ok=True)

def process_pdf(pdf_input):
    if os.path.isfile(pdf_input):  # Local file
        images = convert_from_path(pdf_input)
    else:  # Assume it's a URL
        response = requests.get(pdf_input)
        pdf_bytes = BytesIO(response.content)
        images = convert_from_bytes(pdf_bytes)

    return images

@app.route('/convert', methods=['POST'])
def convert_pdfs_to_image():
    pdf_files = request.files.getlist('files')
    pdf_urls = request.form.getlist('urls')

    all_images = []

    # Process local files
    for pdf_file in pdf_files:
        pdf_file.save(os.path.join(output_folder, pdf_file.filename))
        pdf_input = os.path.join(output_folder, pdf_file.filename)
        images = process_pdf(pdf_input)
        all_images.extend(images)

    # Process URLs
    for pdf_url in pdf_urls:
        try:
            images = process_pdf(pdf_url)
            all_images.extend(images)
        except Exception as e:
            return jsonify({'error': f'Error processing URL: {pdf_url}, {str(e)}'}), 500

    # Combine images vertically
    combined_image = combine_images(all_images)

    # Save the combined image
    combined_image_filename = 'combined_image.png'
    combined_image_path = os.path.join(output_folder, combined_image_filename)
    combined_image.save(combined_image_path)

    return jsonify({'combined_image_path': combined_image_path}), 200

def combine_images(images):
    if not images:
        raise ValueError('No images provided to combine.')

    # Determine maximum width and total height
    max_width = max(image.width for image in images)
    total_height = sum(image.height for image in images)

    # Create a new blank image with the calculated width and height
    combined_image = Image.new('RGB', (max_width, total_height))

    # Paste each image into the combined image
    current_y = 0
    for image in images:
        combined_image.paste(image, (0, current_y))
        current_y += image.height

    return combined_image

if __name__ == '__main__':
    app.run(debug=True)
