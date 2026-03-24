from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models import db, Seller
import random

seller_bp = Blueprint('seller', __name__)

@seller_bp.route('/api/sellers', methods=['GET'])
def get_sellers():
    try:
        sellers = Seller.query.all()
        output = [s.to_dict() for s in sellers]
        return jsonify({"total": len(output), "sellers": output}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

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
        return jsonify({"mensagem": "Sucesso", "codigo": codigo}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500
    
@seller_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    seller = Seller.query.filter_by(email=email).first()

    
    if not seller or seller.senha != senha: 
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
    celular = data.get('celular')
    codigo_recebido = data.get('codigo')

    seller = Seller.query.filter_by(celular=celular).first()

    if not seller:
        return jsonify({"erro": "Seller nao encontrado"}), 404

    if seller.codigo_ativacao == str(codigo_recebido):
        seller.status = 'Ativo'
        seller.codigo_ativacao = None
        db.session.commit()
        return jsonify({"mensagem": "Conta ativada com sucesso!"}), 200
    else:
        return jsonify({"erro": "Codigo invalido"}), 400