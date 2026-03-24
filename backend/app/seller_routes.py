import os
import random
from dotenv import load_dotenv
from twilio.rest import Client
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models import db, Seller


load_dotenv(dotenv_path="/app/.env")

print(f"DEBUG SID: {os.getenv('TWILIO_SID')}")
print(f"DEBUG PHONE: {os.getenv('TWILIO_PHONE')}")

seller_bp = Blueprint('seller', __name__)

# ENVIO DE WHATSAPP
def enviar_whatsapp(celular, codigo):
    try:
        sid = os.getenv('TWILIO_SID')
        token = os.getenv('TWILIO_TOKEN')
        from_phone = os.getenv('TWILIO_PHONE')
        
        client = Client(sid, token)
        
       
        celular_limpo = str(celular).replace("+", "").replace(" ", "").strip()
        para = f"whatsapp:+{celular_limpo}"
        
        texto = f"Seu codigo de ativacao do Mini Mercado e: {codigo}"
        
        print(f"--- Tentando enviar para: {para} ---") 
        
        message = client.messages.create(
            from_=from_phone,
            body=texto,
            to=para
        )
        print(f"--- Sucesso Twilio! SID: {message.sid} ---")
    except Exception as e:
        print(f"--- ERRO DETALHADO DO TWILIO: {e} ---")

#  LISTAR SELLERS (GET)
@seller_bp.route('/api/sellers', methods=['GET'])
def get_sellers():
    try:
        sellers = Seller.query.all()
        output = [s.to_dict() for s in sellers]
        return jsonify({"total": len(output), "sellers": output}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# CADASTRO (POST)
@seller_bp.route('/api/sellers', methods=['POST'])
def create_seller():
    data = request.get_json()
    if not data or not data.get('email'):
        return jsonify({"erro": "Dados incompletos"}), 400

    
    codigo = str(random.randint(1000, 9999))
    
    new_seller = Seller(
        nome=data.get('nome'),
        cnpj=data.get('cnpj'),
        email=data.get('email'),
        celular=data.get('celular'),
        senha=data.get('senha'),
        codigo_ativacao=codigo,
        status='Inativo'
    )

    try:
        db.session.add(new_seller)
        db.session.commit() 
        
        print("Chamando a função de WhatsApp...")
        enviar_whatsapp(new_seller.celular, codigo)
        
        return jsonify({"mensagem": "Sucesso", "codigo": codigo}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500
    
# LOGIN (POST)
@seller_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()

    email_enviado = data.get('email')
    senha_enviada = data.get('senha')

    seller = Seller.query.filter_by(email=email_enviado).first()

 
    if not seller or str(seller.senha) != senha_enviada: 
        return jsonify({"erro": "E-mail ou senha inválidos"}), 401
    
    
    if seller.status != 'Ativo':
        return jsonify({"erro": "Conta inativa. Verifique seu WhatsApp para ativar."}), 403

    
    access_token = create_access_token(identity=str(seller.id))
    
    return jsonify({
        "mensagem": "Login realizado com sucesso!",
        "token": access_token,
        "seller": seller.to_dict()
    }), 200

@seller_bp.route('/api/sellers/activate', methods=['POST'])
def activate_seller():
    data = request.get_json()
    
   
    celular_enviado = str(data.get('celular', '')).strip()
    codigo_enviado = str(data.get('codigo', '')).strip()

    
    seller = Seller.query.filter(
        (Seller.celular == celular_enviado) | 
        (Seller.celular == celular_enviado.replace("+", ""))
    ).first()

    if not seller:
        return jsonify({"erro": "Seller nao encontrado"}), 404

 
    codigo_no_banco = str(seller.codigo_ativacao).strip()
    
    if codigo_no_banco == codigo_enviado:
        seller.status = 'Ativo'
        seller.codigo_ativacao = None
        db.session.commit()
        return jsonify({"mensagem": "Conta ativada com sucesso!"}), 200
    
    
    print(f"ERRO DE COMPARAÇÃO: Banco({codigo_no_banco}) vs Enviado({codigo_enviado})")
    return jsonify({"erro": "Codigo invalido"}), 400