gcloud auth login
gcloud auth list
gcloud config list
gcloud config set account srebeca.yanez@gmail.com
gcloud config set project smart-data-pub-sub

gcloud pubsub topics create topic-local
gcloud pubsub topics create topic-local-1
gcloud pubsub topics create topic-local-2
gcloud pubsub topics list
gcloud pubsub topics delete topic-local-2
gcloud pubsub topics list

gcloud pubsub subscriptions create --topic topic-local subs-local
gcloud pubsub subscriptions create --topic topic-local subs-local-1
gcloud pubsub subscriptions create --topic topic-local subs-local-2
gcloud pubsub subscriptions list
gcloud pubsub subscriptions delete subs-local-2
gcloud pubsub subscriptions delete subs-local-1

gcloud pubsub topics publish topic-local --message "Mensaje desde el topic-local"
gcloud pubsub topics publish topic-local --message "Mensaje desde el topic-local, numero 2"
gcloud pubsub topics publish topic-local --message "Mensaje desde el topic-local, numero 3"
gcloud pubsub topics publish topic-local --message "Mensaje desde el topic-local, numero 4"

gcloud pubsub subscriptions list
gcloud pubsub subscriptions pull subs-local --auto-ack
gcloud pubsub subscriptions pull subs-local --auto-ack
gcloud pubsub subscriptions pull subs-local --auto-ack --limit=2
gcloud pubsub subscriptions pull subs-local --auto-ack
gcloud pubsub subscriptions pull subs-local --auto-ack
gcloud pubsub topics publish topic-local --message "Mensaje desde el topic-local"
gcloud pubsub topics publish topic-local --message "Mensaje desde el topic-local 2"
gcloud pubsub topics publish topic-local --message "Mensaje desde el topic-local 3"
gcloud pubsub topics publish topic-local --message "Mensaje desde el topic-local 4"
gcloud pubsub subscriptions pull subs-local --auto-ack --limit=4
gcloud pubsub subscriptions pull subs-local --auto-ack

gcloud pubsub topics list
gcloud pubsub schemas list
gcloud pubsub topics update sd-local-topic-01 --schema=sd-consola-schema-01 --message-encoding=json
gcloud pubsub topics update topic-local-1 --schema=smartdata-schema-1 --message-encoding=json
gcloud pubsub topics publish topic-local-1 --message "Mensaje desde el topic-local 2"
gcloud pubsub topics publish topic-local-1 --message "{\"NombreProducto\":\"Televisor50\",\"Cantidad\":210,\"Disponible\":true}"

gcloud pubsub subscriptions create --topic=topic-local-1 subs-local-w-schema
gcloud pubsub subscriptions list
gcloud pubsub subscriptions pull subs-local-w-schema --auto-ack
gcloud pubsub topics publish topic-local-1 --message "{\"NombreProducto\":\"Televisor50\",\"Cantidad\":100,\"Disponible\":true}"
gcloud pubsub subscriptions pull subs-local-w-schema --auto-ack

-- Laboratorio 03

gcloud pubsub subscriptions pull my-subscription --auto-ack
gcloud pubsub topics publish sd-gcolab-topic-01 --message "Hola"
gcloud pubsub topics publish sd-gcolab-topic-01 --message "como estas"
gcloud pubsub topics publish sd-gcolab-topic-01 --message "yo estoy muy bien"
gcloud pubsub topics publish sd-gcolab-topic-01 --message "tú qué tal?"
gcloud pubsub subscriptions list
