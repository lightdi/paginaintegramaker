# Integra Maker - IFPB Campus Sousa

Sistema web para o laboratório Integra Maker do IFPB Campus Sousa, desenvolvido em Flask.

## 📁 Estrutura do Projeto

```
Integramaker/
├── app.py                 # Aplicação principal Flask
├── models.py             # Modelos do banco de dados
├── email_config.py       # Configurações de email
├── create_admin.py       # Script para criar admin
├── requirements.txt      # Dependências Python
├── README.md            # Este arquivo
├── static/              # Arquivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
├── templates/           # Templates HTML
│   ├── admin/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── ...
└── Docker/              # Arquivos Docker
    ├── Dockerfile
    ├── docker-compose.yml
    └── docker-entrypoint.sh
```

## 🚀 Como Executar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Criar Usuário Administrador
```bash
python create_admin.py
```

### 3. Executar Aplicação
```bash
python app.py
```

### 4. Acessar Sistema
- **URL**: http://127.0.0.1:5000
- **Login Admin**: admin / admin123
- **Email Admin**: admin@ifpb.edu.br

## 🔧 Configuração de Email

### Modo Desenvolvimento (Padrão)
- Emails são confirmados automaticamente
- Links aparecem no console
- Sistema funciona sem configuração

### Modo Produção
1. Configure senha de app no Gmail
2. Edite `email_config.py`:
```python
MAIL_PASSWORD = 'sua_senha_de_app'
MAIL_SUPPRESS_SEND = False
```

## 📋 Funcionalidades

### ✅ Sistema de Usuários
- Cadastro apenas com emails @ifpb.edu.br
- Confirmação de email obrigatória
- Senhas criptografadas
- Controle de acesso por níveis

### ✅ Área Administrativa
- Dashboard administrativo
- Gestão de projetos
- Gestão de notícias
- Interface responsiva

### ✅ Área Pública
- Exibição de projetos ativos
- Exibição de projetos concluídos
- Notícias recentes
- Design da marca Integra Maker

## 🔒 Segurança

- ✅ Validação de domínio de email
- ✅ Senhas criptografadas com Werkzeug
- ✅ Tokens seguros para confirmação
- ✅ Sessões seguras do Flask
- ✅ Proteção CSRF nativa

## 🐳 Docker

### Executar com Docker
```bash
docker-compose up --build
```

### Arquivos Docker
- `Dockerfile` - Imagem da aplicação
- `docker-compose.yml` - Orquestração
- `docker-entrypoint.sh` - Script de inicialização

## 📧 Sistema de Email

### Validação
- Apenas emails @ifpb.edu.br são aceitos
- Validação automática no frontend e backend

### Confirmação
- Tokens únicos e seguros
- Expiração em 24 horas
- Modo desenvolvimento com confirmação automática

## 🎨 Design

### Cores da Marca
- **Laranja**: #FF9900 (navbar, footer)
- **Azul**: #007BFF (botões primários)
- **Verde**: #28A745 (sucesso)
- **Marrom**: #6B5A4D (títulos secundários)

### Responsividade
- Bootstrap 5
- Design mobile-first
- Interface adaptável

## 📚 Tecnologias

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Banco**: SQLite
- **Email**: Flask-Mail
- **Segurança**: Werkzeug
- **Containerização**: Docker

## 🔄 Desenvolvimento

### Estrutura Modular
- `app.py` - Lógica da aplicação
- `models.py` - Modelos do banco
- `email_config.py` - Configurações de email
- `templates/` - Interface do usuário
- `static/` - Recursos estáticos

### Banco de Dados
- SQLite para desenvolvimento
- Migrações automáticas
- Modelos bem estruturados

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs da aplicação
2. Confirme as configurações de email
3. Teste com modo desenvolvimento

---

**Integra Maker** - Laboratório de Inovação e Cultura Maker  
**IFPB Campus Sousa** - Instituto Federal da Paraíba