from flask import Flask
from app.routes.status import status_bp
from app.database.mongodb import get_database

app = Flask(__name__)

# Permitir caracteres especiales en respuestas JSON
app.json.ensure_ascii = False

# Registrar rutas existentes
app.register_blueprint(status_bp)

# ==============================
# PRUEBA DE CONEXIÓN MONGODB
# ==============================

try:
    db = get_database()
    collections = db.list_collection_names()

    print("\n✅ CONEXIÓN EXITOSA CON MONGODB")
    print("Base de datos:", db.name)
    print("Colecciones disponibles:")

    for collection in collections:
        print(" -", collection)

except Exception as error:
    print("\n❌ ERROR DE CONEXIÓN CON MONGODB")
    print(error)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )