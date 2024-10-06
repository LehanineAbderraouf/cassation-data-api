import os
import requests
from bs4 import BeautifulSoup
import tarfile
import xml.etree.ElementTree as ET
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import io

# Charger les variables d'environnement du fichier .env
load_dotenv()

# Récupérer les configurations depuis .env
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# URL de la page contenant les liens
url = "https://echanges.dila.gouv.fr/OPENDATA/CASS/"

# output folder for all downloaded and extracted data
output_dir = "/app/data"

# Connexion à MongoDB
client = MongoClient(mongo_uri)
db = client['cour_cassation']
collection = db['decisions']

# Fonction pour télécharger un fichier
def download_archive(archive_url, dest_folder):
    file_name = os.path.join(dest_folder, archive_url.split("/")[-1])
    
    # Télécharger le fichier
    response = requests.get(archive_url, stream=True)
    if response.status_code == 200:
        with open(file_name, "wb") as file:
            file.write(response.content)
        return file_name
    else:
        raise Exception(f"Erreur lors du téléchargement du fichier : {response.status_code}")

# Fonction pour extraire un fichier tar.gz et traiter les fichiers XML directement
def extract_and_parse_archive(file_path, db_collection):
    if file_path.endswith("tar.gz"):
        with tarfile.open(file_path, "r:gz") as tar:
            for member in tar.getmembers():
                if member.isfile() and member.name.endswith(".xml"):
                    f = tar.extractfile(member)
                    if f is not None:
                        parse_and_store_xml(f, db_collection)

# Fonction pour récupérer tous les liens .tar.gz sur la page
def get_tar_gz_links(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Erreur lors de la récupération de la page : {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")  # trouver tous les <a>

    # Filtrer pour ne garder que les liens finissant par .tar.gz
    tar_gz_links = [
        url + link["href"] for link in links if link["href"].endswith("tar.gz")
    ]

    return tar_gz_links

# Fonction pour parser un fichier XML et extraire les informations <TITRE>, <FORMATION>, <ID>, <CONTENU>
def parse_and_store_xml(xml_file, db_collection):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        titre = root.findtext(".//TITRE")
        formation = root.findtext(".//FORMATION")
        id_ = root.findtext(".//ID")

        for contenu_element in root.findall('.//CONTENU'):
            # Get the text directly inside <contenu>
            contenu = contenu_element.text or ''  # Start with text inside <contenu>
            
            # Append all the text from child elements
            contenu += ''.join(contenu_element.itertext()).replace("<br/>","")  # Get all text including children
        

        # Nettoyer les balises internes
        data = {
            "titre": titre if titre else None,
            "formation": formation if formation else None,
            "id": id_ if id_ else None,
            "contenu": contenu if contenu else None
        }

        # Stocker les données dans MongoDB
        db_collection.insert_one(data)
        print(f"Données insérées pour un fichier XML.")

    except ET.ParseError:
        print(f"Erreur de parsing XML dans le fichier {xml_file}")

# Main function
def main():
    # Connexion à MongoDB
    client = MongoClient("mongodb://mongo:27017/")
    db = client['cour_cassation']
    collection = db['decisions']

    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Récupérer tous les liens de fichiers .tar.gz
    tar_gz_files = get_tar_gz_links(url)

    # Télécharger et extraire chaque fichier .tar.gz de manière parallèle
    with ThreadPoolExecutor(max_workers=4) as executor:  # 4 threads pour le téléchargement et parsing
        for file_url in tar_gz_files:
            try:
                print(f"Téléchargement de {file_url}")
                archive_path = download_archive(file_url, output_dir)
                print(f"Extraction et traitement de {archive_path}")
                executor.submit(extract_and_parse_archive, archive_path, collection)
            except Exception as e:
                print(f"Erreur lors du traitement du fichier {file_url}: {e}")

if __name__ == "__main__":
    main()
