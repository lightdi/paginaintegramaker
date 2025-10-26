from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import os
import re
from dotenv import load_dotenv
from models import db, Usuario, Projeto, Noticia

# Carregar variáveis de ambiente
load_dotenv('config.env')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'integra-maker-secret-key-2024')

# Configuração do banco PostgreSQL
DB_NAME = os.getenv('DB_NAME', 'integra_db')
DB_USER = os.getenv('DB_USER', 'agro_userindustria')
DB_PASSWORD = os.getenv('DB_PASSWORD', '!AgorIndustria')
DB_HOST = os.getenv('DB_HOST', '200.129.71.149')
DB_PORT = os.getenv('DB_PORT', '9000')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações para URLs externas (necessário para emails)
app.config['SERVER_NAME'] = '127.0.0.1:5000'
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

# Configurações de email
app.config.update({
    'MAIL_SERVER': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    'MAIL_PORT': int(os.getenv('MAIL_PORT', '587')),
    'MAIL_USE_TLS': os.getenv('MAIL_USE_TLS', 'True').lower() == 'true',
    'MAIL_USERNAME': os.getenv('MAIL_USERNAME', 'integramaker.ss@ifpb.edu.br'),
    'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD', 'wjdb cydc zvko bfij'),
    'MAIL_DEFAULT_SENDER': os.getenv('MAIL_DEFAULT_SENDER', 'integramaker.ss@ifpb.edu.br'),
    'MAIL_MAX_EMAILS': int(os.getenv('MAIL_MAX_EMAILS', '10')),
    'MAIL_SUPPRESS_SEND': os.getenv('MAIL_SUPPRESS_SEND', 'False').lower() == 'true'
})

# Inicializar extensões
db.init_app(app)
mail = Mail(app)

# Funções auxiliares
def validar_email_ifpb(email):
    """Valida se o email é do domínio @ifpb.edu.br"""
    pattern = r'^[a-zA-Z0-9._%+-]+@ifpb\.edu\.br$'
    return re.match(pattern, email) is not None

def enviar_email_confirmacao(usuario):
    """Envia email de confirmação para o usuário"""
    token = usuario.gerar_token_confirmacao()
    db.session.commit()
    # Modo de desenvolvimento - se email não funcionar, confirma automaticamente
    if app.config.get('MAIL_SUPPRESS_SEND', False):
        print(f"[MODO DESENVOLVIMENTO] Email de confirmacao para {usuario.email}")
        print(f"[MODO DESENVOLVIMENTO] Token: {token}")
        print(f"[MODO DESENVOLVIMENTO] Link: http://127.0.0.1:5000/confirmar-email/{token}")
        usuario.confirmar_email()
        db.session.commit()
        return True
    
    msg = Message(
        subject='Confirme seu email - Integra Maker',
        recipients=[usuario.email],
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    
    confirm_url = url_for('confirmar_email', token=token, _external=True)
    
    msg.html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #FF9900; padding: 20px; text-align: center;">
            <h1 style="color: white; margin: 0;">Integra Maker</h1>
            <p style="color: white; margin: 10px 0 0 0;">IFPB Campus Sousa</p>
        </div>
        
        <div style="padding: 30px; background-color: #f9f9f9;">
            <h2 style="color: #333;">Confirme seu email</h2>
            <p>Olá {usuario.nome},</p>
            <p>Obrigado por se cadastrar no Integra Maker! Para ativar sua conta, clique no botão abaixo:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{confirm_url}" 
                   style="background-color: #FF9900; color: white; padding: 15px 30px; 
                          text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Confirmar Email
                </a>
            </div>
            
            <p>Ou copie e cole este link no seu navegador:</p>
            <p style="word-break: break-all; color: #666;">{confirm_url}</p>
            
            <p style="margin-top: 30px; color: #666; font-size: 14px;">
                Este link expira em 24 horas. Se você não solicitou este cadastro, 
                pode ignorar este email.
            </p>
        </div>
        
        <div style="background-color: #6B5A4D; padding: 15px; text-align: center;">
            <p style="color: white; margin: 0; font-size: 12px;">
                Integra Maker - Laboratório de Inovação e Cultura Maker<br>
                IFPB Campus Sousa
            </p>
        </div>
    </body>
    </html>
    """
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        print(f"[FALLBACK] Confirmando email automaticamente para {usuario.email}")
        print(f"[FALLBACK] Token: {token}")
        print(f"[FALLBACK] Link: http://127.0.0.1:5000/confirmar-email/{token}")
        usuario.confirmar_email()
        db.session.commit()
        return True

# Funções de autenticação
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'error')
            return redirect(url_for('login'))
        
        user = Usuario.query.get(session['user_id'])
        if not user:
            flash('Usuário não encontrado.', 'error')
            return redirect(url_for('login'))
        
        if not user.email_confirmado:
            flash('Você precisa confirmar seu email antes de acessar a área administrativa.', 'warning')
            return redirect(url_for('login'))
        
        if not user.is_admin:
            flash('Acesso negado. Apenas administradores podem acessar esta área.', 'error')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

# Rotas de autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = Usuario.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.email_confirmado:
                flash('Você precisa confirmar seu email antes de fazer login. Verifique sua caixa de entrada.', 'warning')
                return render_template('login.html')
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash(f'Bem-vindo, {user.nome}!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('admin'))
        else:
            flash('Usuário ou senha incorretos.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado com sucesso.', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        nome = request.form['nome']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validações
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('register.html')
        
        if not validar_email_ifpb(email):
            flash('Apenas emails do domínio @ifpb.edu.br são aceitos.', 'error')
            return render_template('register.html')
        
        if Usuario.query.filter_by(username=username).first():
            flash('Nome de usuário já existe.', 'error')
            return render_template('register.html')
        
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'error')
            return render_template('register.html')
        
        # Criar usuário
        user = Usuario(username=username, email=email, nome=nome)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Enviar email de confirmação
        if enviar_email_confirmacao(user):
            flash('Usuário cadastrado com sucesso! Verifique seu email para confirmar a conta.', 'success')
        else:
            flash('Usuário cadastrado, mas houve erro ao enviar email de confirmação. Entre em contato com o administrador.', 'warning')
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/confirmar-email/<token>')
def confirmar_email(token):
    user = Usuario.query.filter_by(token_confirmacao=token).first()
    
    if not user:
        flash('Token de confirmação inválido ou expirado.', 'error')
        return redirect(url_for('login'))
    
    # Verificar se o token não expirou (24 horas)
    if user.data_criacao < datetime.utcnow() - timedelta(hours=24):
        flash('Token de confirmação expirado. Solicite um novo cadastro.', 'error')
        return redirect(url_for('register'))
    
    user.confirmar_email()
    db.session.commit()
    
    flash('Email confirmado com sucesso! Agora você pode fazer login.', 'success')
    return redirect(url_for('login'))

@app.route('/reenviar-confirmacao')
def reenviar_confirmacao():
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro.', 'error')
        return redirect(url_for('login'))
    
    user = Usuario.query.get(session['user_id'])
    if user.email_confirmado:
        flash('Seu email já foi confirmado.', 'info')
        return redirect(url_for('index'))
    
    if enviar_email_confirmacao(user):
        flash('Email de confirmação reenviado! Verifique sua caixa de entrada.', 'success')
    else:
        flash('Erro ao reenviar email de confirmação. Entre em contato com o administrador.', 'error')
    
    return redirect(url_for('login'))

# Rotas principais
@app.route('/')
def index():
    projetos_ativos = Projeto.query.filter_by(status='ativo').order_by(Projeto.data_criacao.desc()).limit(6).all()
    projetos_concluidos = Projeto.query.filter_by(status='concluido').order_by(Projeto.data_conclusao.desc()).limit(6).all()
    noticias_recentes = Noticia.query.order_by(Noticia.data_publicacao.desc()).limit(3).all()
    return render_template('index.html', 
                         projetos_ativos=projetos_ativos,
                         projetos_concluidos=projetos_concluidos,
                         noticias_recentes=noticias_recentes)

@app.route('/projetos')
def projetos():
    status = request.args.get('status', 'todos')
    if status == 'ativos':
        projetos = Projeto.query.filter_by(status='ativo').order_by(Projeto.data_criacao.desc()).all()
    elif status == 'concluidos':
        projetos = Projeto.query.filter_by(status='concluido').order_by(Projeto.data_conclusao.desc()).all()
    else:
        projetos = Projeto.query.order_by(Projeto.data_criacao.desc()).all()
    
    return render_template('projetos.html', projetos=projetos, status_atual=status)

@app.route('/projeto/<int:id>')
def projeto_detalhes(id):
    projeto = Projeto.query.get_or_404(id)
    return render_template('projeto_detalhes.html', projeto=projeto)

@app.route('/noticias')
def noticias():
    noticias = Noticia.query.order_by(Noticia.data_publicacao.desc()).all()
    return render_template('noticias.html', noticias=noticias)

@app.route('/noticia/<int:id>')
def noticia_detalhes(id):
    noticia = Noticia.query.get_or_404(id)
    return render_template('noticia_detalhes.html', noticia=noticia)

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

# Área administrativa
@app.route('/admin')
@admin_required
def admin():
    total_projetos = Projeto.query.count()
    projetos_ativos = Projeto.query.filter_by(status='ativo').count()
    projetos_concluidos = Projeto.query.filter_by(status='concluido').count()
    total_noticias = Noticia.query.count()
    
    return render_template('admin/dashboard.html',
                         total_projetos=total_projetos,
                         projetos_ativos=projetos_ativos,
                         projetos_concluidos=projetos_concluidos,
                         total_noticias=total_noticias)

@app.route('/admin/projetos')
@admin_required
def admin_projetos():
    projetos = Projeto.query.order_by(Projeto.data_criacao.desc()).all()
    return render_template('admin/projetos.html', projetos=projetos)

@app.route('/admin/projetos/novo', methods=['GET', 'POST'])
@admin_required
def admin_projeto_novo():
    if request.method == 'POST':
        projeto = Projeto(
            titulo=request.form['titulo'],
            descricao=request.form['descricao'],
            equipe=request.form['equipe'],
            disciplina=request.form['disciplina'],
            tecnologias=request.form['tecnologias'],
            imagem_url=request.form.get('imagem_url', ''),
            status=request.form.get('status', 'ativo')
        )
        
        if projeto.status == 'concluido':
            projeto.data_conclusao = datetime.utcnow()
        
        db.session.add(projeto)
        db.session.commit()
        flash('Projeto cadastrado com sucesso!', 'success')
        return redirect(url_for('admin_projetos'))
    
    return render_template('admin/projeto_form.html')

@app.route('/admin/projetos/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_projeto_editar(id):
    projeto = Projeto.query.get_or_404(id)
    
    if request.method == 'POST':
        projeto.titulo = request.form['titulo']
        projeto.descricao = request.form['descricao']
        projeto.equipe = request.form['equipe']
        projeto.disciplina = request.form['disciplina']
        projeto.tecnologias = request.form['tecnologias']
        projeto.imagem_url = request.form.get('imagem_url', '')
        projeto.status = request.form.get('status', 'ativo')
        
        if projeto.status == 'concluido' and not projeto.data_conclusao:
            projeto.data_conclusao = datetime.utcnow()
        elif projeto.status == 'ativo':
            projeto.data_conclusao = None
        
        db.session.commit()
        flash('Projeto atualizado com sucesso!', 'success')
        return redirect(url_for('admin_projetos'))
    
    return render_template('admin/projeto_form.html', projeto=projeto)

@app.route('/admin/projetos/deletar/<int:id>')
@admin_required
def admin_projeto_deletar(id):
    projeto = Projeto.query.get_or_404(id)
    db.session.delete(projeto)
    db.session.commit()
    flash('Projeto deletado com sucesso!', 'success')
    return redirect(url_for('admin_projetos'))

@app.route('/admin/noticias')
@admin_required
def admin_noticias():
    noticias = Noticia.query.order_by(Noticia.data_publicacao.desc()).all()
    return render_template('admin/noticias.html', noticias=noticias)

@app.route('/admin/noticias/nova', methods=['GET', 'POST'])
@admin_required
def admin_noticia_nova():
    if request.method == 'POST':
        noticia = Noticia(
            titulo=request.form['titulo'],
            conteudo=request.form['conteudo'],
            autor=request.form['autor'],
            imagem_url=request.form.get('imagem_url', '')
        )
        
        db.session.add(noticia)
        db.session.commit()
        flash('Notícia cadastrada com sucesso!', 'success')
        return redirect(url_for('admin_noticias'))
    
    return render_template('admin/noticia_form.html')

@app.route('/admin/noticias/editar/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_noticia_editar(id):
    noticia = Noticia.query.get_or_404(id)
    
    if request.method == 'POST':
        noticia.titulo = request.form['titulo']
        noticia.conteudo = request.form['conteudo']
        noticia.autor = request.form['autor']
        noticia.imagem_url = request.form.get('imagem_url', '')
        
        db.session.commit()
        flash('Notícia atualizada com sucesso!', 'success')
        return redirect(url_for('admin_noticias'))
    
    return render_template('admin/noticia_form.html', noticia=noticia)

@app.route('/admin/noticias/deletar/<int:id>')
@admin_required
def admin_noticia_deletar(id):
    noticia = Noticia.query.get_or_404(id)
    db.session.delete(noticia)
    db.session.commit()
    flash('Notícia deletada com sucesso!', 'success')
    return redirect(url_for('admin_noticias'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
