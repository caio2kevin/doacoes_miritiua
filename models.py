from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)  # WhatsApp
    senha_hash = db.Column(db.String(256), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # doador | receptor | admin | instituicao
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


class Doador(db.Model):
    __tablename__ = 'doador'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), unique=True, nullable=False)
    cidade = db.Column(db.String(80), default='São Luís')
    bairro = db.Column(db.String(80))
    usuario = db.relationship('Usuario', backref=db.backref('doador', uselist=False))


class Receptor(db.Model):
    __tablename__ = 'receptor'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), unique=True, nullable=False)
    bairro = db.Column(db.String(80), default='Miritiua')
    # urgencia: 1=baixa, 2=média, 3=alta, 4=crítica (estudante sem equipamento)
    urgencia = db.Column(db.Integer, default=2)
    estudante = db.Column(db.Boolean, default=False)
    idade_escolar = db.Column(db.Boolean, default=False)
    observacao = db.Column(db.Text)
    usuario = db.relationship('Usuario', backref=db.backref('receptor', uselist=False))


class Instituicao(db.Model):
    __tablename__ = 'instituicao'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), unique=True, nullable=False)
    nome_instituicao = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(50))  # escola, ong, associação
    endereco = db.Column(db.String(200))
    usuario = db.relationship('Usuario', backref=db.backref('instituicao', uselist=False))


class Equipamento(db.Model):
    __tablename__ = 'equipamento'
    id = db.Column(db.Integer, primary_key=True)
    doador_id = db.Column(db.Integer, db.ForeignKey('doador.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # notebook, desktop, tablet, smartphone, monitor, etc.
    marca = db.Column(db.String(60))
    modelo = db.Column(db.String(80))
    estado = db.Column(db.String(30), default='bom')  # excelente, bom, regular, precisa_reparo
    descricao = db.Column(db.Text)
    disponivel = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    doador = db.relationship('Doador', backref=db.backref('equipamentos', lazy=True))


class Doacao(db.Model):
    __tablename__ = 'doacao'
    id = db.Column(db.Integer, primary_key=True)
    equipamento_id = db.Column(db.Integer, db.ForeignKey('equipamento.id'), unique=True, nullable=False)
    receptor_id = db.Column(db.Integer, db.ForeignKey('receptor.id'), nullable=False)
    status = db.Column(db.String(30), default='solicitada')  # solicitada, aprovada, em_transito, entregue, cancelada
    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_entrega = db.Column(db.DateTime)
    observacao = db.Column(db.Text)
    equipamento = db.relationship('Equipamento', backref=db.backref('doacao', uselist=False))
    receptor = db.relationship('Receptor', backref=db.backref('doacoes', lazy=True))


class Notificacao(db.Model):
    __tablename__ = 'notificacao'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    doacao_id = db.Column(db.Integer, db.ForeignKey('doacao.id'))
    mensagem = db.Column(db.Text, nullable=False)
    canal = db.Column(db.String(20), default='whatsapp')
    enviada = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    usuario = db.relationship('Usuario', backref=db.backref('notificacoes', lazy=True))
    doacao = db.relationship('Doacao', backref=db.backref('notificacoes', lazy=True))
