from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Product

product_bp = Blueprint('product', __name__)


@product_bp.route('/api/products', methods=['POST'])
@jwt_required() 
def create_product():
    
    current_seller_id = get_jwt_identity()
    
    data = request.get_json()
    
    if not data or not data.get('nome') or not data.get('preco'):
        return jsonify({"erro": "Dados do produto incompletos"}), 400

    new_product = Product(
        nome=data['nome'],
        preco=data['preco'],
        quantidade=data.get('quantidade', 0),
        seller_id=current_seller_id
    )

    try:
        db.session.add(new_product)
        db.session.commit()
        return jsonify({
            "mensagem": "Produto cadastrado!",
            "produto": new_product.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500


@product_bp.route('/api/products', methods=['GET'])
@jwt_required()
def get_products():
    current_seller_id = get_jwt_identity()
   
    products = Product.query.filter_by(seller_id=current_seller_id).all()
    return jsonify([p.to_dict() for p in products]), 200


@product_bp.route('/api/products/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    current_seller_id = get_jwt_identity()
    product = Product.query.filter_by(id=id, seller_id=current_seller_id).first()

    if not product:
        return jsonify({"erro": "Produto não encontrado ou acesso negado"}), 404

    data = request.get_json()
    product.nome = data.get('nome', product.nome)
    product.preco = data.get('preco', product.preco)
    product.quantidade = data.get('quantidade', product.quantidade)

    db.session.commit()
    return jsonify({"mensagem": "Produto atualizado!", "produto": product.to_dict()}), 200


@product_bp.route('/api/products/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    current_seller_id = get_jwt_identity()
    product = Product.query.filter_by(id=id, seller_id=current_seller_id).first()

    if not product:
        return jsonify({"erro": "Produto não encontrado"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"mensagem": "Produto removido com sucesso!"}), 200