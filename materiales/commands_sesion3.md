# LAB 01 
## Describir un rol
gcloud iam roles describe roles/storage.admin
gcloud iam roles describe roles/editor

## role-definition.yaml
title: "Role Editor SD"
description: "Permisos para appEngine"
stage: "ALPHA"
includedPermissions:
- appengine.versions.create
- appengine.versions.delete

gcloud iam roles create EditorSDG12 --project smartdata-grupo-12-sesion-2 --file role-definition.yaml

## Para Windows
gcloud iam roles create EditorSD --project delta-suprstate-434802-r3 --file "C:\Users\brale\Documents\GCP\Clase 3 IAM\role-definition.yaml"

gcloud iam roles list --project smartdata-grupo-12-sesion-2

## No utilizar "\" en Windows. Borrarlos y poner todo en una sola línea
gcloud iam roles create ViewerSDG09 --project western-trilogy-429606-h1 \
--title "Role Viewer SD G09" \
--description "Custom role de SD." \
--stage ALPHA \
--permissions compute.instances.get,compute.instances.list 

gcloud iam roles describe EditorSD --project western-trilogy-429606-h1
gcloud iam roles describe ViewerSDG09 --project western-trilogy-429606-h1

gcloud iam roles describe ViewerSD --project nombre-de-tu-proyecto

gcloud iam roles update EditorSDG12 --project smartdata-grupo-12-sesion-2 \
--add-permissions storage.buckets.get,storage.buckets.list

gcloud iam roles update ViewerSD --project nombre-de-tu-proyecto \
--remove-permissions storage.buckets.list

# LAB 03 
## Creando la SA
gcloud iam service-accounts create sd-local-sa-01 --display-name sd-local-sa-01

gcloud iam service-accounts list  --filter "displayName=sd-local-sa-01"

gcloud iam service-accounts list --format="value(email)" --filter "displayName=sd-local-sa-01"

## Otorgando permisos
gcloud projects add-iam-policy-binding smartdata-grupo-12-sesion-2 --member serviceAccount:sd-local-sa-01@smartdata-grupo-12-sesion-2.iam.gserviceaccount.com --role=roles/iam.serviceAccountUser
gcloud projects add-iam-policy-binding smartdata-grupo-12-sesion-2 --member serviceAccount:sd-local-sa-01@smartdata-grupo-12-sesion-2.iam.gserviceaccount.com --role=roles/compute.instanceAdmin
gcloud projects add-iam-policy-binding smartdata-grupo-12-sesion-2 --member serviceAccount:sd-local-sa-01@smartdata-grupo-12-sesion-2.iam.gserviceaccount.com --role=roles/bigquery.user
gcloud projects add-iam-policy-binding smartdata-grupo-12-sesion-2 --member serviceAccount:sd-local-sa-01@smartdata-grupo-12-sesion-2.iam.gserviceaccount.com --role=roles/bigquery.dataViewer
gcloud projects add-iam-policy-binding smartdata-grupo-12-sesion-2 --member serviceAccount:sd-local-sa-01@smartdata-grupo-12-sesion-2.iam.gserviceaccount.com --role roles/bigquery.jobUser

## Creando una VM (En Windows, no funcionan los backslashs)
gcloud compute instances create sd-local-vm-02 \
--service-account=sd-local-sa-01@smartdata-grupo-12-sesion-2.iam.gserviceaccount.com \
--zone=us-east1-c \
--scopes=https://www.googleapis.com/auth/cloud-platform

## Para Windows
gcloud compute instances create sd-local-vm-02 --service-account=sd-local-sa-01@smartdata-grupo-12-sesion-2.iam.gserviceaccount.com --zone=us-east1-c --scopes=https://www.googleapis.com/auth/cloud-platform


## Conectar a la instancia creada
gcloud compute ssh sd-local-vm-02 --zone us-east1-c

## Instalamos librerías
sudo apt-get update
sudo apt-get install -y git python3-pip
pip3 install --upgrade pip
pip3 install google-cloud-bigquery
pip3 install pyarrow
pip3 install pandas
pip3 install db-dtypes

## Script en Python para conectarse a BigQuery
echo "
from google.auth import compute_engine
from google.cloud import bigquery
credentials = compute_engine.Credentials(
    service_account_email='sd-local-sa-01@smartdata-grupo-12-sesion-2.iam.gserviceaccount.com')
query = '''
SELECT name, SUM(number) as total_people
FROM bigquery-public-data.usa_names.usa_1910_2013
WHERE state = 'TX'
GROUP BY name, state
ORDER BY total_people DESC
LIMIT 20
'''
client = bigquery.Client(
    project='smartdata-grupo-12-sesion-2',
    credentials=credentials)
print(client.query(query).to_dataframe())
" > query.py

python3 query.py