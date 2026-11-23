Dataproc

gcloud dataproc clusters create ssm-local-cluster-spark --enable-component-gateway --region us-central1 --master-machine-type e2-standard-2 --master-boot-disk-type pd-balanced --master-boot-disk-size 50 --num-workers 2 --worker-machine-type e2-standard-2 --worker-boot-disk-type pd-balanced --worker-boot-disk-size 50 --image-version 2.3-debian12 --project western-trilogy-429606-h1


gcloud config set dataproc/region us-central1


gcloud dataproc jobs submit spark --cluster sd-local-dataproc-01 \
  --class org.apache.spark.examples.SparkPi \
  --jars file:///usr/lib/spark/examples/jars/spark-examples.jar -- 1000
  
  
Dataflow

docker run -it -e PROJECT=western-trilogy-429606-h1 -v $(pwd)/dataflow_:/dataflow_ python:3.7 /bin/bash

pip install apache-beam[gcp]==2.24.0

cd dataflow_
    
python create_csv_from_bigquery.py \
    --project=western-trilogy-429606-h1 \
    --region=us-east4 \
    --runner=DataflowRunner \
    --staging_location=gs://sd-gcolab-bucket-2/staging \
    --temp_location gs://sd-gcolab-bucket-2/temp \
    --save_main_session  

python ingestion.py \
    --project=western-trilogy-429606-h1 \
    --region=us-east4 \
    --runner=DataflowRunner \
    --staging_location=gs://sd-consola-bucket-100/staging \
    --temp_location gs://sd-consola-bucket-100/temp \
    --save_main_session
