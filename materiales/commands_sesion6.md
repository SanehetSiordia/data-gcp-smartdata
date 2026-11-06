Lab 01.1
gsutil mb gs://ssm-consola-bucket-clase6
gsutil ls -L
curl https://cdn.mos.cms.futurecdn.net/BT4GR5JKJJTudF6kUGEqg7.jpg --output euler.jpg
gsutil cp euler.jpg gs://ssm-consola-bucket-clase6
rm ada.jpg
gsutil cp -r gs://ssm-consola-bucket-clase6/ada.jpg .
gsutil cp gs://ssm-consola-bucket-clase6/euler.jpg gs://ssm-consola-bucket-clase6/image-folder/
gsutil ls gs://ssm-consola-bucket-clase6
gsutil ls -l gs://ssm-consola-bucket-clase6/euler.jpg

gsutil acl ch -u AllUsers:R gs://ssm-consola-bucket-clase6/euler.jpg
https://storage.googleapis.com/ronny-bucket-nuevo/ada.jpg
gsutil acl ch -d AllUsers gs://ssm-consola-bucket-clase6/euler.jpg
gsutil rm gs://ssm-consola-bucket-clase6/euler.jpg

Lab 02
gcloud storage buckets update gs://ssm-consola-bucket-clase6 --lifecycle-file=lifecycle.json
gcloud storage buckets describe gs://ssm-consola-bucket-clase6 --format=default(lifecycle_config)
gcloud storage buckets update gs://ssm-consola-bucket-clase6 --clear-lifecycle

Lab 03

export BUCKET=<name of bucket> # Solo para MAC
gsutil mb gs://ssm-consola-bucket-clase6


gsutil retention set 10s gs://ssm-consola-bucket-clase6
gsutil retention get gs://ssm-consola-bucket-clase6
gsutil cp gs://spls/gsp297/dummy_transactions gs://ssm-consola-bucket-clase6/
gsutil ls -L gs://ssm-consola-bucket-clase6/dummy_transactions
gsutil retention lock gs://ssm-consola-bucket-clase6/
gsutil retention get gs://ssm-consola-bucket-clase6
gsutil retention temp set gs://ssm-consola-bucket-clase6/dummy_transactions
gsutil rm gs://ssm-consola-bucket-clase6/dummy_transactions
gsutil retention temp release gs://ssm-consola-bucket-clase6/dummy_transactions
gsutil rm gs://ssm-consola-bucket-clase6/dummy_transactions




