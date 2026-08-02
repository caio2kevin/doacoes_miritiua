"""
MVP - Sistema de Cadastro e Gestão de Doações de Equipamentos Tecnológicos
Bairro Miritiua – São José de Ribamar/MA
Atividade Extensionista II - UNINTER
"""

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, abort
)
from models import (
    db, Usuario, Doador, Receptor, Instituicao,
    Equipamento, Doacao, Notificacao
)
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-miritiua-2026-chave-secreta')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///doacoes_miritiua.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# ───────────────────────── Helpers ─────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Faça login para continuar.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('tipo') != 'admin':
            flash('Acesso restrito ao administrador.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated


def get_usuario_atual():
    if 'usuario_id' in session:
        return Usuario.query.get(session['usuario_id'])
    return None


def gerar_link_whatsapp(telefone: str, mensagem: str) -> str:
    """Gera link wa.me gratuito (sem API paga)."""
    # Remove caracteres não numéricos
    num = ''.join(filter(str.isdigit, telefone))
    if not num.startswith('55'):
        num = '55' + num
    from urllib.parse import quote
    return f"https://wa.me/{num}?text={quote(mensagem)}"


# ───────────────────────── Rotas públicas ─────────────────────────

@app.route('/')
def index():
    total_equip = Equipamento.query.filter_by(disponivel=True).count()
    total_doacoes = Doacao.query.filter_by(status='entregue').count()
    total_receptores = Receptor.query.count()
    return render_template(
        'index.html',
        total_equip=total_equip,
        total_doacoes=total_doacoes,
        total_receptores=total_receptores,
        usuario=get_usuario_atual()
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        user = Usuario.query.filter_by(email=email, ativo=True).first()
        if user and user.check_senha(senha):
            session['usuario_id'] = user.id
            session['tipo'] = user.tipo
            session['nome'] = user.nome
            flash(f'Bem-vindo(a), {user.nome}!', 'success')
            if user.tipo == 'admin':
                return redirect(url_for('admin_painel'))
            return redirect(url_for('index'))
        flash('E-mail ou senha inválidos.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('index'))


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        telefone = request.form.get('telefone', '').strip()
        senha = request.form.get('senha', '')
        tipo = request.form.get('tipo', 'receptor')

        if Usuario.query.filter_by(email=email).first():
            flash('Este e-mail já está cadastrado.', 'danger')
            return redirect(url_for('cadastro'))

        user = Usuario(nome=nome, email=email, telefone=telefone, tipo=tipo)
        user.set_senha(senha)
        db.session.add(user)
        db.session.flush()  # pega o id

        if tipo == 'doador':
            doador = Doador(
                usuario_id=user.id,
                cidade=request.form.get('cidade', 'São Luís'),
                bairro=request.form.get('bairro_doador', '') or request.form.get('bairro', '')
            )
            db.session.add(doador)
        elif tipo == 'receptor':
            receptor = Receptor(
                usuario_id=user.id,
                bairro=request.form.get('bairro', 'Miritiua'),
                urgencia=int(request.form.get('urgencia', 2)),
                estudante=request.form.get('estudante') == 'on',
                idade_escolar=request.form.get('idade_escolar') == 'on',
                observacao=request.form.get('observacao', '')
            )
            db.session.add(receptor)
        elif tipo == 'instituicao':
            inst = Instituicao(
                usuario_id=user.id,
                nome_instituicao=request.form.get('nome_instituicao', ''),
                tipo=request.form.get('tipo_inst', 'escola'),
                endereco=request.form.get('endereco', '')
            )
            db.session.add(inst)

        db.session.commit()
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html')


# ───────────────────────── Equipamentos ─────────────────────────

@app.route('/equipamentos')
def listar_equipamentos():
    q = request.args.get('q', '').strip()
    tipo_filtro = request.args.get('tipo', '')
    query = Equipamento.query.filter_by(disponivel=True)
    if q:
        query = query.filter(
            db.or_(
                Equipamento.marca.ilike(f'%{q}%'),
                Equipamento.modelo.ilike(f'%{q}%'),
                Equipamento.descricao.ilike(f'%{q}%')
            )
        )
    if tipo_filtro:
        query = query.filter_by(tipo=tipo_filtro)
    equipamentos = query.order_by(Equipamento.criado_em.desc()).all()
    tipos = db.session.query(Equipamento.tipo).distinct().all()
    return render_template(
        'equipamentos.html',
        equipamentos=equipamentos,
        tipos=[t[0] for t in tipos],
        usuario=get_usuario_atual(),
        q=q,
        tipo_filtro=tipo_filtro
    )


@app.route('/equipamento/novo', methods=['GET', 'POST'])
@login_required
def novo_equipamento():
    if session.get('tipo') != 'doador':
        flash('Apenas doadores podem cadastrar equipamentos.', 'warning')
        return redirect(url_for('index'))

    doador = Doador.query.filter_by(usuario_id=session['usuario_id']).first()
    if not doador:
        flash('Perfil de doador não encontrado.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        eq = Equipamento(
            doador_id=doador.id,
            tipo=request.form.get('tipo'),
            marca=request.form.get('marca', ''),
            modelo=request.form.get('modelo', ''),
            estado=request.form.get('estado', 'bom'),
            descricao=request.form.get('descricao', '')
        )
        db.session.add(eq)
        db.session.commit()
        flash('Equipamento cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_equipamentos'))

    return render_template('novo_equipamento.html', usuario=get_usuario_atual())


# ───────────────────────── Solicitar doação ─────────────────────────

@app.route('/solicitar/<int:equip_id>', methods=['GET', 'POST'])
@login_required
def solicitar_doacao(equip_id):
    if session.get('tipo') != 'receptor':
        flash('Apenas receptores podem solicitar equipamentos.', 'warning')
        return redirect(url_for('listar_equipamentos'))

    equip = Equipamento.query.get_or_404(equip_id)
    if not equip.disponivel:
        flash('Este equipamento não está mais disponível.', 'warning')
        return redirect(url_for('listar_equipamentos'))

    receptor = Receptor.query.filter_by(usuario_id=session['usuario_id']).first()
    if not receptor:
        flash('Perfil de receptor não encontrado.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Marca equipamento como indisponível
        equip.disponivel = False
        doacao = Doacao(
            equipamento_id=equip.id,
            receptor_id=receptor.id,
            status='solicitada',
            observacao=request.form.get('observacao', '')
        )
        db.session.add(doacao)
        db.session.flush()

        # Notificação para o doador
        doador_user = equip.doador.usuario
        msg = (
            f"Olá {doador_user.nome}! Sua doação do equipamento "
            f"{equip.tipo} {equip.marca or ''} {equip.modelo or ''} "
            f"foi solicitada por {receptor.usuario.nome} (bairro {receptor.bairro}). "
            f"Acesse o sistema para acompanhar."
        )
        notif = Notificacao(
            usuario_id=doador_user.id,
            doacao_id=doacao.id,
            mensagem=msg,
            canal='whatsapp'
        )
        db.session.add(notif)
        db.session.commit()

        link_wa = gerar_link_whatsapp(doador_user.telefone, msg)
        flash(
            f'Solicitação registrada! Clique no botão abaixo para avisar o doador pelo WhatsApp.',
            'success'
        )
        return render_template(
            'solicitacao_ok.html',
            doacao=doacao,
            link_whatsapp=link_wa,
            usuario=get_usuario_atual()
        )

    return render_template(
        'solicitar.html',
        equipamento=equip,
        usuario=get_usuario_atual()
    )


# ───────────────────────── Painel do usuário ─────────────────────────

@app.route('/minhas-doacoes')
@login_required
def minhas_doacoes():
    user = get_usuario_atual()
    if user.tipo == 'doador':
        doador = Doador.query.filter_by(usuario_id=user.id).first()
        equipamentos = Equipamento.query.filter_by(doador_id=doador.id).all() if doador else []
        return render_template(
            'minhas_doacoes_doador.html',
            equipamentos=equipamentos,
            usuario=user
        )
    elif user.tipo == 'receptor':
        receptor = Receptor.query.filter_by(usuario_id=user.id).first()
        doacoes = Doacao.query.filter_by(receptor_id=receptor.id).all() if receptor else []
        return render_template(
            'minhas_doacoes_receptor.html',
            doacoes=doacoes,
            usuario=user
        )
    return redirect(url_for('index'))


# ───────────────────────── Admin ─────────────────────────

@app.route('/admin')
@login_required
@admin_required
def admin_painel():
    # Priorização: receptores com maior urgência primeiro
    receptores = (
        Receptor.query
        .join(Usuario)
        .order_by(Receptor.urgencia.desc(), Usuario.criado_em.asc())
        .all()
    )
    doacoes_pendentes = Doacao.query.filter(
        Doacao.status.in_(['solicitada', 'aprovada', 'em_transito'])
    ).order_by(Doacao.data_solicitacao.desc()).all()
    total_equip = Equipamento.query.count()
    disponiveis = Equipamento.query.filter_by(disponivel=True).count()
    entregues = Doacao.query.filter_by(status='entregue').count()

    return render_template(
        'admin_painel.html',
        receptores=receptores,
        doacoes_pendentes=doacoes_pendentes,
        total_equip=total_equip,
        disponiveis=disponiveis,
        entregues=entregues,
        usuario=get_usuario_atual()
    )


@app.route('/admin/doacao/<int:doacao_id>/status', methods=['POST'])
@login_required
@admin_required
def atualizar_status_doacao(doacao_id):
    doacao = Doacao.query.get_or_404(doacao_id)
    novo_status = request.form.get('status')
    if novo_status not in ('solicitada', 'aprovada', 'em_transito', 'entregue', 'cancelada'):
        flash('Status inválido.', 'danger')
        return redirect(url_for('admin_painel'))

    doacao.status = novo_status
    if novo_status == 'entregue':
        doacao.data_entrega = datetime.utcnow()
        doacao.equipamento.disponivel = False

    # Notificação ao receptor
    receptor_user = doacao.receptor.usuario
    msg = (
        f"Atualização da sua solicitação (#{doacao.id}): "
        f"status alterado para *{novo_status.upper()}*. "
        f"Equipamento: {doacao.equipamento.tipo} "
        f"{doacao.equipamento.marca or ''} {doacao.equipamento.modelo or ''}."
    )
    notif = Notificacao(
        usuario_id=receptor_user.id,
        doacao_id=doacao.id,
        mensagem=msg
    )
    db.session.add(notif)
    db.session.commit()

    link_wa = gerar_link_whatsapp(receptor_user.telefone, msg)
    flash(f'Status atualizado. Avisar receptor pelo WhatsApp: {link_wa}', 'success')
    return redirect(url_for('admin_painel'))


@app.route('/admin/receptor/<int:rec_id>/urgencia', methods=['POST'])
@login_required
@admin_required
def atualizar_urgencia(rec_id):
    receptor = Receptor.query.get_or_404(rec_id)
    urgencia = int(request.form.get('urgencia', 2))
    if 1 <= urgencia <= 4:
        receptor.urgencia = urgencia
        db.session.commit()
        flash('Urgência atualizada.', 'success')
    return redirect(url_for('admin_painel'))


# ───────────────────────── Inicialização ─────────────────────────

def criar_dados_iniciais():
    """Cria admin padrão e alguns dados de exemplo se o banco estiver vazio."""
    if Usuario.query.filter_by(tipo='admin').first():
        return

    admin = Usuario(
        nome='Administrador ONG',
        email='admin@miritiua.org',
        telefone='98999990000',
        tipo='admin'
    )
    admin.set_senha('admin123')
    db.session.add(admin)

    # Doador de exemplo
    doador_u = Usuario(
        nome='Maria Doadora',
        email='maria@email.com',
        telefone='98988887777',
        tipo='doador'
    )
    doador_u.set_senha('123456')
    db.session.add(doador_u)
    db.session.flush()
    doador = Doador(usuario_id=doador_u.id, cidade='São Luís', bairro='Centro')
    db.session.add(doador)
    db.session.flush()

    eq1 = Equipamento(
        doador_id=doador.id,
        tipo='notebook',
        marca='Dell',
        modelo='Inspiron 15',
        estado='bom',
        descricao='Notebook usado, funciona bem, ideal para estudos.'
    )
    eq2 = Equipamento(
        doador_id=doador.id,
        tipo='smartphone',
        marca='Samsung',
        modelo='Galaxy A12',
        estado='regular',
        descricao='Celular com tela boa, bateria mediana.'
    )
    db.session.add_all([eq1, eq2])

    # Receptor de exemplo
    rec_u = Usuario(
        nome='João Estudante',
        email='joao@email.com',
        telefone='98977776666',
        tipo='receptor'
    )
    rec_u.set_senha('123456')
    db.session.add(rec_u)
    db.session.flush()
    receptor = Receptor(
        usuario_id=rec_u.id,
        bairro='Miritiua',
        urgencia=4,
        estudante=True,
        idade_escolar=True,
        observacao='Aluno do 9º ano, precisa de notebook para aulas online.'
    )
    db.session.add(receptor)
    db.session.commit()
    print('✅ Dados iniciais criados:')
    print('   Admin: admin@miritiua.org / admin123')
    print('   Doador: maria@email.com / 123456')
    print('   Receptor: joao@email.com / 123456')


@app.cli.command('init-db')
def init_db():
    """Cria as tabelas e dados iniciais."""
    db.create_all()
    criar_dados_iniciais()
    print('Banco de dados inicializado.')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if os.environ.get('FLASK_ENV') != 'production':
            criar_dados_iniciais()
    app.run(debug=True, host='0.0.0.0', port=5000)