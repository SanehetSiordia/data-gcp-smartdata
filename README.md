# data-gcp-smartdata

Comando en bash:

make all

comprobacion de firewall
docker exec gcp-docker gcloud compute firewall-rules describe allow-postgres-ingress --project=applied-primacy-512618-h7

Confirmacion de existencia de familia de procesador en GCP:
docker exec gcp-docker gcloud compute images describe-from-family ubuntu-2404-lts-amd64 --project=ubuntu-os-cloud

Verificar que Script python termino de crear VM con PostgresSQL
docker exec gcp-docker gcloud compute instances get-serial-port-output ssm-console-compute \
  --zone us-west1-b --project applied-primacy-512618-h7 | grep -i "startup-script"
