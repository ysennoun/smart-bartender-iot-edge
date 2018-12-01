import json
import io
import random
import logging

# Imports for the REST API
from flask import Flask, request

# Import for the image to treat
from PIL import Image

# Import prediction model
from predict import initialize_model, predict_image

app = Flask(__name__)

# 4MB Max image size limit
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024 

# Default route just shows simple text
@app.route('/')
def index():
    app.logger.info('index function in flask')
    return 'Tensorflow.ai model host harness'

# Like the image-classifier-service.ai Prediction service /image route handles either
#     - octet-stream image file 
#     - a multipart/form-data with files in the imageData parameter
@app.route('/image', methods=['POST'])
def predict_image_handler():
    app.logger.info('predict_image_handler function in flask')
    try:
        imageData = None
        if ('imageData' in request.files):
            imageData = request.files['imageData']
        else:
            imageData = io.BytesIO(request.get_data())
        image_file = str(random.randint(0, 100000)) + '.jpg'       
        image = Image.open(imageData)
        image.save(image_file, 'JPEG')
        return json.dumps(predict_image(image_file))
    except Exception as e:
        app.logger.error('EXCEPTION:'+ str(e))
        return 'Error processing image', 500

if __name__ == '__main__':
    # Initialize model
    initialize_model()

    # Run the server
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=80)