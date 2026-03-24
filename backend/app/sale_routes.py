from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Product, Sale

sale_bp = Blueprint('sale', __name__)

@sale_bp.route('/api/sales', methods=['POST'])
@jwt_required()
def register_sale():
    current_seller_id = get_jwt_identity()
    data = request.get_json()
    
    product_id = data.get('product_id')
    quantidade = data.get('quantidade')

    # 1. Busca o produto e verifica se pertence ao Seller logado
    product = Product.query.filter_by(id=product_id, seller_id=current_seller_id).first()
    
    if not product:
        return jsonify({"erro": "Produto não encontrado"}), 404

    # 2. Verifica se tem estoque suficiente
    if product.quantidade < quantidade:
        return jsonify({"erro": f"Estoque insuficiente. Disponível: {product.quantidade}"}), 400

    # 3. Cálculo do valor total
    valor_total = product.preco * quantidade

    # 4. REGRA DE OURO: Baixa no estoque
    product.quantidade -= quantidade

    # 5. Registra a venda
    new_sale = Sale(
        product_id=product.id,
        seller_id=current_seller_id,
        quantidade_vendida=quantidade,
        valor_total=valor_total
    )

    try:
        db.session.add(new_sale)
        db.session.commit() # Salva a venda E a alteração no produto (estoque)
        return jsonify({
            "mensagem": "Venda realizada!",
            "estoque_atual": product.quantidade,
            "total_pago": valor_total
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": str(e)}), 500