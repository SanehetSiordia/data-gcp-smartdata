from datetime import datetime
import random
import json
import uuid
from faker import Faker
from google.cloud import storage

def campanas_ingesta(request):
    request_json = request.get_json()
    
    if request_json and 'quantity' in request_json:
        quantity = request_json['quantity']
    else:
        return json.dumps({"error": "Missing 'quantity'"}), 400

    fecha = datetime.now()
    fecha_archivo = fecha.strftime('%Y%m%d')
    uuid_4_digitos = str(uuid.uuid4().hex)[:4]
    bucket_name = 'sd-gcolab-bucket-1'
    
    fake = Faker()
    lines = []

    destination_blob_name = f'ingested/txt/campanas_{fecha_archivo}_{uuid_4_digitos}.txt'

    for _ in range(quantity):            
        nro_campania = fake.random_number(digits=8)
        costo = round(random.uniform(10, 1000), 2)
        pais = fake.country()
        fecha = fake.date_time_between_dates(datetime_start=datetime(2023, 5, 1))
        line = f'{nro_campania}\t{costo}\t{pais}\t{fecha}\n'
        lines.append(line)


    text_content = ''.join(lines)
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(text_content, content_type='text/plain')

    message = f'Object created at {bucket_name} with name {destination_blob_name}'
        
    return json.dumps({"message": message})
