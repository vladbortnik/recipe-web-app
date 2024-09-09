import os
# from google.cloud import vision
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from . import db
from .models import ImgSet

def process_imgset(path_to_imgset_dir):
    endpoint = os.getenv('AZURE_COMPUTERVISION_ENDPOINT')
    key = os.getenv('AZURE_COMPUTERVISION_KEY')

    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

    detected_products = []

    for filename in os.listdir(path_to_imgset_dir):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(path_to_imgset_dir, filename)

            with open(file_path, 'rb') as image_file:
                analysis = client.tag_image_in_stream(image_file)

            for tag in analysis.tags:
                detected_products.append(tag.name)

    detected_products_str = ', '.join(set(detected_products))

    # Update the ImgSet entry in the database
    img_set = ImgSet.query.filter_by(folder_path=path_to_imgset_dir).first()
    if img_set:
        img_set.products = detected_products_str
        db.session.commit()






#     key = os.getenv('AZURE_COMPUTERVISION_KEY')
#     endpoint = os.getenv('AZURE_COMPUTERVISION_ENDPOINT')

# def process_imgset(path_to_imgset_dir):
#     client = vision.ImageAnnotatorClient()

#     detected_products = []

#     for filename in os.listdir(path_to_imgset_dir):
#         if filename.endswith(('.jpg', '.jpeg', '.png')):
#             file_path = os.path.join(path_to_imgset_dir, filename)

#             with open(file_path, 'rb') as image_file:
#                 content = image_file.read()

#             image = vision.Image(content=content)
#             response = client.label_detection(image=image)
            
#             labels = response.label_annotations

#             for label in labels:
#                 detected_products.append(label.description)

#             if response.error.message:
#                 raise Exception(f'{response.error.message}')
    
#     detected_products_str = ', '.join(set(detected_products))

#     # Update the ImgSet entry in the database
#     img_set = ImgSet.query.filter_by(folder_path=path_to_imgset_dir).first()
#     if img_set:
#         img_set.products = detected_products_str
#         db.session.commit()
