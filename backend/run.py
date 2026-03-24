import time
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from app.models import db
from app.seller_routes import seller_bp
from sqlalchemy.exc import OperationalError
from app.product_routes import product_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@db/minimercado_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key-mudar-depois' 
jwt = JWTManager(app)

db.init_app(app)
app.register_blueprint(seller_bp)
app.register_blueprint(product_bp)

def inicializar_banco():
    with app.app_context():
        for i in range(10): 
            try:
                print(f"Tentativa {i+1}: Conectando ao banco de dados...")
                db.create_all()
                print("Conectado com sucesso!")
                return
            except OperationalError:
                print("Banco de dados ainda indisponível. Aguardando 3 segundos...")
                time.sleep(3)
        print("Erro: Não foi possível conectar ao banco de dados após várias tentativas.")


inicializar_banco()

@app.route('/')
def index():
    return jsonify({"msg": "API do Mini Mercado está rodando!"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)