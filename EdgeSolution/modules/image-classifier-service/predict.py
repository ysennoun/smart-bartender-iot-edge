import json
import os
import subprocess
import random
import re
from PIL import Image

REGEX="(.*)\(score = (.*)\)"
# Define the JSON message to send to IoT Hub.
PREDICTION = "{\"prediction\": \"%r\",\"score\": %r}"

def initialize_model():
    model_cmd = 'python3 classify_image.py --model_dir=tmp_prediction'
    os.system(model_cmd)

def predict_image(image_file):
    model_cmd = 'python3 classify_image.py --model_dir=tmp_prediction --image_file=' + image_file
    process = subprocess.Popen(model_cmd, shell=True,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)
    out, err = process.communicate()
    errcode = process.returncode
    os.system('rm ' + image_file)
    result = []
    if out:
        outs = str(out).split('\n')
        for prediction in outs:
            res = re.search(REGEX, prediction)
            if res and len(res.groups()) == 2:
                result.append(PREDICTION % (res.group(1), res.group(2)))
        return [','.join(result)]
    else:
        return []
