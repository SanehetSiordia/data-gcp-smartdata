from airflow import DAG
from airflow import models

from airflow.operators.dummy import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectsWithPrefixExistenceSensor
from airflow.operators.bash_operator import BashOperator
from airflow.utils.task_group import TaskGroup

from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocDeleteClusterOperator,
    DataprocSubmitJobOperator,
)

from datetime import timedelta, datetime
import requests
import logging
import json

#variables_globales
BUCKET = models.Variable.get('bucket')
PROJECT_ID = models.Variable.get('project_id')
REGION = 'us-central1'
FECHA_FORMATO = datetime.now().strftime("%Y%m%d")
CLUSTER_NAME = f'sd-composer-dataproc-{FECHA_FORMATO}'
JAR_URI = models.Variable.get('jar_uri')
PYSPARK_URI = models.Variable.get('pyspark_uri')

DEFAULT_ARGS = {
    'owner': 'dyanez',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'email_on_failure': False,
    'email_on_retry': False
}

TASK_ARGUMENTS = {
    'url' : models.Variable.get('url'),
    'source_cmp' : 'cmp',
    'source_trx' : 'trx'
}

CLUSTER_CONFIG = {
    "master_config": {
        "num_instances": 1,
        "machine_type_uri": "n1-standard-2",
        "disk_config": {"boot_disk_type": "pd-standard", "boot_disk_size_gb": 128},
    },
    "worker_config": {
        "num_instances": 2,
        "machine_type_uri": "n1-standard-2",
        "disk_config": {"boot_disk_type": "pd-standard", "boot_disk_size_gb": 128},
    },
}

PYSPARK_JOB ={
    "reference" : {"project_id": PROJECT_ID},
    "placement" : {"cluster_name": CLUSTER_NAME},
    "pyspark_job" : {
        "main_python_file_uri": PYSPARK_URI,
        "jar_file_uris": [JAR_URI]
                     }
}

PATHS = {
    'path_campanas' : 'gs://sd-local-bucket-g19-x900/ingested_2/txt/campanas_*.txt',
    'path_transacciones' : 'gs://sd-local-bucket-g19-x900/ingested_2/txt/transacciones_*.txt',
    'target': 'gs://sd-local-bucket-g19-x900/loaded'
}


def _ingesta_endpoint(url, source):
    headers = {
        'Content-Type': 'application/json'
    }
    data = json.dumps({"source":source})

    try:
        # response = requests.post(url, headers=headers, data=data)
        response = requests.get(url, params={"source": source})
        response.raise_for_status()
        logging.info('Request successful')
        logging.info(f'Response text: {response.text}')
        return response.text
    except requests.exceptions.RequestException as e:
        error_message = f'Request failed: {str(e)}'
        logging.error(error_message)
        raise Exception(error_message)
    

with DAG(
    'laboratorio_cloud_composer',
    default_args = DEFAULT_ARGS,
    description = 'Ejecucion de un datapipeline con un Cluster Efimero',
    catchup = False,
    start_date = datetime(2023, 9, 28),
    schedule_interval = '@once',
    tags = ['laboratorio_cloud_composer']

) as dag:    
    
    with TaskGroup('etapa_ingesta') as etapa_ingesta:
        ingesta_campanas = PythonOperator(
        task_id = 'ingesta_campanas',
        python_callable = _ingesta_endpoint,
        op_args = [TASK_ARGUMENTS['url'],
                   TASK_ARGUMENTS['source_cmp']]
    )

        ingesta_transacciones = PythonOperator(
        task_id = 'ingesta_transacciones',
        python_callable = _ingesta_endpoint,
        op_args = [TASK_ARGUMENTS['url'],
                   TASK_ARGUMENTS['source_trx']]
    )

    with TaskGroup('etapa_validacion') as etapa_validacion:
        sensor_campanas = GCSObjectsWithPrefixExistenceSensor(
        task_id = 'sensor_campanas',
        bucket = BUCKET,
        prefix = 'ingested_2/txt/campanas_{{ ds_nodash }}_',
        google_cloud_conn_id = 'google_cloud_default',
        timeout = 15
    )

        sensor_transacciones = GCSObjectsWithPrefixExistenceSensor(
        task_id = 'sensor_transacciones',
        bucket = BUCKET,
        prefix = 'ingested_2/txt/transacciones_{{ ds_nodash }}_',
        google_cloud_conn_id = 'google_cloud_default',
        timeout = 15
    )
        
    with TaskGroup('etapa_etl') as etapa_etl:
        create_cluster = DataprocCreateClusterOperator(
        task_id = 'create_cluster',
        project_id = PROJECT_ID,
        cluster_config = CLUSTER_CONFIG,
        region = REGION,
        cluster_name = CLUSTER_NAME
    )

        ejecutar_job = DataprocSubmitJobOperator(
        task_id = 'ejecutar_job',
        job = PYSPARK_JOB,
        region = REGION,
        project_id = PROJECT_ID
    )

        delete_cluster = DataprocDeleteClusterOperator(
        task_id = 'delete_cluster',
        project_id = PROJECT_ID,
        cluster_name = CLUSTER_NAME,
        region = REGION
    )
        create_cluster >> ejecutar_job >> delete_cluster

        
    with TaskGroup('etapa_reubicacion') as etapa_reubicacion:
        smart_cleaner = BashOperator(
        task_id = 'smart_cleaner',
        bash_command = """
            gsutil mv {{ params.path_campanas }} {{ params.target }} && 
            gsutil mv {{ params.path_transacciones }} {{ params.target }}
        """,
        params = {
            'path_campanas': PATHS['path_campanas'],
            'path_transacciones': PATHS['path_transacciones'],
            'target': PATHS['target']
        }
    )
            

    #orden ejecuciones
    etapa_ingesta >> etapa_validacion >> etapa_etl >> etapa_reubicacion