Cloud SQL 01
gcloud config set project <project-id>
gcloud sql connect <instance-name> --user=root
show DATABASES;
CREATE DATABASE <database-name>;
USE <database-name>;
CREATE TABLE entries (guestName VARCHAR(255), content VARCHAR(255), entryID INT NOT NULL AUTO_INCREMENT, PRIMARY KEY(entryID));
show tables;
INSERT INTO entries (guestName, content) values ("first guest", "I got here!");
INSERT INTO entries (guestName, content) values ("second guest", "Me too!");

curl -O https://raw.githubusercontent.com/hadley/data-baby-names/master/baby-names.csv
gsutil cp baby-names.csv gs://sd-consola-bucket-sql-1
select max(year) from baby_names;
select * from baby_names where year = 2008 and sex = 'boy' order by percent desc limit 1;
select sum(percent) from baby_names where year = 2007;

create table baby_names (year int, name varchar(255), percent double, sex varchar(255));

Clous SQL 02
curl -O https://raw.githubusercontent.com/GoogleCloudPlatform/data-science-on-gcp/main/03_sqlstudio/create_table.sql
curl -O https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2015_1.zip
unzip On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2015_1.zip
mv On_Time_Reporting_Carrier_On_Time_Performance_\(1987_present\)_2015_1.csv flights.csv
export PROJECT_ID=$(gcloud info --format='value(config.project)')
export BUCKET=${PROJECT_ID}-local-bucket-1
gsutil mb gs://$BUCKET
gsutil cp create_table.sql gs://$BUCKET/create_table.sql
gsutil cp flights.csv gs://$BUCKET/flights.csv

gcloud sql instances create sd-local-sql-pg-1 \
    --database-version=POSTGRES_13 --cpu=2 --memory=8GiB \
    --region="us-central1" --root-password=Passw0rd
export ADDRESS=$(curl -s http://ipecho.net/plain)/32
gcloud sql instances patch sd-local-sql-pg-1 --authorized-networks $ADDRESS
gcloud sql instances patch sd-local-sql-pg-1 --authorized-networks 35.247.19.160


Clous Firestore 01
gcloud firestore databases create \
--database=sd-local-firestore-1 \
--location=nam5 \
--type=firestore-native 
gcloud firestore databases describe --database=sd-local-firestore-1
gcloud alpha firestore databases update --database=sd-local-firestore-1 --delete-protection
gcloud alpha firestore databases update --database=ronny-test --no-delete-protection
gcloud alpha firestore databases delete --database=ronny-dev

MemoryStore 01
telnet
sudo apt-get install telnet
telnet 10.157.203.107 6379
python3 --version
pip3 --version
sudo apt-get install python3-pip
sudo apt install python3.11-venv
python3 -m venv venv_redis
source venv_redis/bin/activate
pip3 install redis
pip3 install python-memcache