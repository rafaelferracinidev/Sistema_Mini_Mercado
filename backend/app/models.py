from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Seller(db.Model):
    __tablename__ = 'sellers'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    celular = db.Column(db.String(20), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    codigo_ativacao = db.Column(db.String(4), nullable=True) 
    status = db.Column(db.String(20), default='Inativo') 

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "cnpj": self.cnpj,
            "email": self.email,
            "status": self.status
        }

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    
   
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "preco": self.preco,
            "quantidade": self.quantidade,
            "seller_id": self.seller_id
        }