from database import db

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(50))
    mensagem = db.Column(db.Text)

    status = db.Column(db.String(30), default="novo", nullable=False)

    empresa_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    criado_em = db.Column(db.DateTime, server_default=db.func.now())