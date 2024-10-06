import os
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer les configurations depuis .env
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
jwt_secret_key = os.getenv("JWT_SECRET_KEY")
api_username = os.getenv("API_USERNAME")
api_password = os.getenv("API_PASSWORD")

# Configurer l'application Flask
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = jwt_secret_key  # Clé secrète pour le JWT
jwt = JWTManager(app)

# Connexion à MongoDB
client = MongoClient(mongo_uri)
db = client["cour_cassation"]
collection = db["decisions"]

# Base de données pour stocker les utilisateurs  
users = {
    api_username: generate_password_hash(api_password)
}

# After inserting all the documents, create the text index on 'contenu'
print("Creating text index on 'contenu' field...")
collection.create_index([("contenu", "text")])
print("Index created.")

# Route pour obtenir un token JWT après login
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if username not in users or not check_password_hash(users[username], password):
        return jsonify({"msg": "Identifiant ou mot de passe incorrect"}), 401

    # Créer un token d'accès
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# Route pour lister toutes les décisions (afficher uniquement id et titre)
@app.route("/decisions", methods=["GET"])
@jwt_required()
def get_decisions():
    decisions = collection.find({}, {"_id": 0, "id": 1, "titre": 1})
    result = [{"id": decision["id"], "titre": decision["titre"]} for decision in decisions]
    return jsonify(result)

# Route pour filtrer par formation
@app.route("/decisions/formation", methods=["GET"])
@jwt_required()
def filter_by_formation():
    formation = request.args.get("formation")
    if not formation:
        return jsonify({"msg": "Veuillez fournir une formation"}), 400
    
    decisions = collection.find({"formation": formation}, {"_id": 0, "id": 1, "titre": 1})
    result = [{"id": decision["id"], "titre": decision["titre"]} for decision in decisions]
    return jsonify(result)

# Route pour récupérer une décision par son identifiant
@app.route("/decisions/<decision_id>", methods=["GET"])
@jwt_required()
def get_decision_by_id(decision_id):
    decision = collection.find_one({"id": decision_id}, {"_id": 0, "id": 1, "titre": 1, "contenu": 1})
    
    if not decision:
        return jsonify({"msg": "Décision non trouvée"}), 404

    return jsonify(decision)

# Route to get the top 10 decisions where input string matches most with 'contenu'
@app.route("/decisions/search", methods=["GET"])
@jwt_required()
def search_decisions():
    query = request.args.get("q")
    if not query:
        return jsonify({"msg": "Veuillez fournir une chaîne de recherche"}), 400

    # Perform text search on 'contenu' field
    decisions = collection.find(
        {"$text": {"$search": query}},
        {"score": {"$meta": "textScore"}, "id": 1, "titre": 1, "contenu": 1}
    ).sort([("score", {"$meta": "textScore"})]).limit(10)

    result = [{"id": decision["id"], "titre": decision["titre"], "contenu": decision["contenu"]} for decision in decisions]
    return jsonify(result)

# Lancer l'application Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
