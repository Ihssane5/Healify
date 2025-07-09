import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image

class SkinDiseasePredictor:
    def __init__(self, model_path):
        self.model = tf.keras.models.load_model(model_path)
        self.class_names = ['bcc', 'df', 'mel', 'nv', 'vasc']
        self.class_names_dict = {
            'bcc': 'Basal Cell Carcinoma',
            'df': 'Dermatofibroma',
            'mel': 'Melanoma',
            'nv': 'Melanocytic Nevus',
            'vasc': 'Vascular Lesion'
        }

    def predict(self, img_path):
        img = image.load_img(img_path, target_size=(300, 300))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        
        predictions = self.model.predict(img_array)
        predicted_class_idx = np.argmax(predictions[0])
        predicted_class_abbr = self.class_names[predicted_class_idx]
        
        return {
            'class': self.class_names_dict[predicted_class_abbr],
            'class_abbr': predicted_class_abbr,
            'confidence': float(round(100 * np.max(predictions[0]), 2))
        }

# Instance globale pour ne charger le modèle qu'une fois
predictor = SkinDiseasePredictor('assistant_medical/models/MediScan.h5')