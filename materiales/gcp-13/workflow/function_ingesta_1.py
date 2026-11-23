import functions_framework
from datetime import datetime
import random
import json
import uuid
from faker import Faker
from google.cloud import storage
import logging

@functions_framework.http
def campanas_ingesta(request):
    try:
        request_json = request.get_json(silent=True)
        request_args = request.args
        
        if request_args and 'quantity' in request_args:
            quantity = int(request_args['quantity'])
        else:
            return json.dumps({"error": "Missing 'quantity'"}), 400

        fecha = datetime.now()
        fecha_archivo = fecha.strftime('%Y%m%d')
        uuid_4_digitos = str(uuid.uuid4().hex)[:4]
        bucket_name = 'sd-local-bucket-g21-gcs'
        
        fake = Faker()
        lines = []

        destination_blob_name = f'ingested/txt/campanas_{fecha_archivo}_{uuid_4_digitos}.txt'

        for _ in range(quantity):
            nro_campania = fake.random_number(digits=8)
            costo = round(random.uniform(10, 1000), 2)
            pais = fake.country()
            fecha = fake.date_time_between_dates(datetime_start=datetime(2023, 5, 1))
            fecha_str = fecha.strftime('%Y-%m-%d %H:%M:%S')
            line = f'{nro_campania}\t{costo}\t{pais}\t{fecha_str}\n'
            lines.append(line)

        text_content = ''.join(lines)
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(text_content, content_type='text/plain')

        message = f'Object created at {bucket_name} with name {destination_blob_name}'
        
        return json.dumps({"message": message})
    
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return json.dumps({"error": "Internal Server Error", "details": str(e)}), 500
