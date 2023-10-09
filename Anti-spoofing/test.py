import os
import cv2
import numpy as np
import argparse
import warnings
import time
import base64
import json

from src.anti_spoof_predict import AntiSpoofPredict
from src.generate_patches import CropImage
from src.utility import parse_model_name
warnings.filterwarnings('ignore')


from flask import *
app = Flask(__name__)


def check_image(image):
    height, width, channel = image.shape
    if width/height != 3/4:
        print("Image is not appropriate!!!\nHeight/Width should be 4/3.")
        return False
    else:
        return True




def resize_image(image):
    # Resize the image to 480x640
    image_resized = cv2.resize(image, (480, 640))

    # Set the DPI to 96
    cv2.imwrite('resized_image.jpg', image_resized, [cv2.IMWRITE_JPEG_QUALITY, 100,
                                                      cv2.IMWRITE_JPEG_OPTIMIZE, 1,
                                                      cv2.IMWRITE_JPEG_PROGRESSIVE, 1,
                                                      cv2.IMWRITE_JPEG_RST_INTERVAL, 0,
                                                      cv2.IMWRITE_JPEG_LUMA_QUALITY, 0,
                                                      cv2.IMWRITE_JPEG_CHROMA_QUALITY, 0])
    # Read the resized image
    resized_image = cv2.imread('resized_image.jpg')
    
    return resized_image


def process_image(image_str, model_dir, device_id):
    model_test = AntiSpoofPredict(device_id)    
    image_cropper = CropImage()
    imgdata = base64.b64decode(image_str)
    nparr = np.frombuffer(imgdata, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    image_resized=resize_image(image)
    result = check_image(image_resized)
    if result is False:
        return "Image is not appropriate!!!\nHeight/Width should be 4/3."
    else:
        image_bbox = model_test.get_bbox(image)
        prediction = np.zeros((1, 3))
        test_speed = 0
        for model_name in os.listdir(model_dir):
            h_input, w_input, model_type, scale = parse_model_name(model_name)
            param = {
                "org_img": image,
                "bbox": image_bbox,
                "scale": scale,
                "out_w": w_input,
                "out_h": h_input,
                "crop": True,
            }
            if scale is None:
                param["crop"] = False
            img = image_cropper.crop(**param)
            start = time.time()
            prediction += model_test.predict(img, os.path.join(model_dir, model_name))
            test_speed += time.time()-start

        label = np.argmax(prediction)
        value = prediction[0][label]/2
        if label == 1:
            print("Image is Real Face. Score: {:.2f}.".format(value))
            result_text = "RealFace Score: {:.2f}".format(value)
            color = (255, 0, 0)
            return {
                "Status": "success",
                "Face": "Real Face",
                "Label": int(label),
                "Score": float(value),
            }
        else:
            print("Image is Fake Face. Score: {:.2f}.".format(value))
            result_text = "FakeFace Score: {:.2f}".format(value)
            color = (0, 0, 255)
            return {
                "Status": "success",
                "Face": "Fake Face",
                "Label": int(label),
                "Score": float(value),
            }

@app.route('/', methods=['GET','POST'])
def predict():
    print("\n")
    if request.method == 'POST':
        image_str = request.data
        json1 = json.loads(image_str)
        image_str = json1['image']
        model_dir = "./resources/anti_spoof_models"
        device_id = 0
        result = process_image(image_str, model_dir, device_id)
        return jsonify(result)
    
    else:
        return "get"

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=4000,debug=True, ssl_context=None)










