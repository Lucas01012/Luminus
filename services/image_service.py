import tensorflow as tf
import numpy as np
import cv2

model = tf.keras.applications.MobileNetV2(weights = 'imagenet')

def process_imagem(image_file):
    npimg = np.frombuffer(image_file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    resized = cv2.resize(img, (224, 224))
    array = tf.keras.applications.mobilenet_v2.preprocess_input(
        np.expand_dims(resized, axis= 0)
    )
    predictions = model.predict(array)
    decoded = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top = 3)[0]

    return [{"objeto": obj[1], "confianca": float(obj[2])} for obj in decoded]