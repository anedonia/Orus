# file_sync

Un simple srcipt qui synchronise un *dossier* local avec un bucket S3.

## Description

Ce script synchronise un dossier local avec un bucket S3:
- si un fichier sur le bucket n'existe pas dans le dossier local, il est supprimé du bucket.
- si un fichier est dans le dossier local mais pas sur le bucket, il est uploadé sur le bucket.
- si un fichier est présent dans les deux, on met à jour le fichier sur le bucket _si nécessaire_.

## Prérequis
1. Dépendances Python

    Python 3.7+ : Assurez-vous d'avoir Python installé.
    Boto3 : Bibliothèque pour interagir avec l'API AWS S3. Installez-la avec la commande :

    pip install boto3 python-dotenv

2. Lancez le container avec la commande 


docker run \
   -p 9000:9000 \
   -p 9001:9001 \
   --name minio \
   -v /tmp/minio-data:/data \
   -e "MINIO_ROOT_USER=VotreAccessKeyID" \
   -e "MINIO_ROOT_PASSWORD=VotreSecretAccessKey" \
   quay.io/minio/minio server /data --console-address ":9001"


3. Configuration .env

Créez un fichier .env dans le dossier script de votre projet pour définir vos variables d'environnement AWS :

AWS_ACCESS_KEY_ID=VotreAccessKeyID
AWS_SECRET_ACCESS_KEY=VotreSecretAccessKey
S3_BUCKET_NAME=NomDuBucket
LOCAL_DIRECTORY=CheminAbsoluVersLeDossierLocal

3. Lancez le script 

	python3 file_sync.py

## Piste d'amélioration

- gérer les permissions de fichier
- utiliser des chemins relatifs 
- unifier le parsing de local files et des bucket files
- normaliser les keys et file path 
- meilleure gestion d'erreur 
- meilleur check pour le .env


