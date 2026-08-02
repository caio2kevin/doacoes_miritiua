<<<<<<< HEAD
# Sistema de Doações de Equipamentos Tecnológicos – Miritiua/MA

**MVP – Atividade Extensionista II (UNINTER)**  
Curso: CST em Análise e Desenvolvimento de Sistemas  
Aluno: Caio Henrique Da Silva Cunha (RU 4604094)

Sistema web gratuito para conectar doadores de equipamentos tecnológicos a moradores, estudantes e instituições do bairro Miritiua (São José de Ribamar/MA).

ODS alinhados: **4** (Educação de qualidade), **10** (Redução das desigualdades), **17** (Parcerias).

---

## Tecnologias (100% gratuitas)

| Camada       | Tecnologia              | Custo     |
|--------------|-------------------------|-----------|
| Backend      | Python 3 + Flask        | Gratuito  |
| ORM          | Flask-SQLAlchemy        | Gratuito  |
| Banco local  | SQLite                  | Gratuito  |
| Banco prod.  | PostgreSQL (Render / Railway / Neon / ElephantSQL free) | Gratuito (tier free) |
| Frontend     | HTML + Bootstrap 5 CDN  | Gratuito  |
| Notificações | Links `wa.me` (WhatsApp)| Gratuito  |
| Hospedagem   | Render.com / Railway / PythonAnywhere free | Gratuito |

---

## Como rodar localmente (2 minutos)

### 1. Pré-requisitos
- Python 3.10+ instalado

### 2. Instalar dependências
```bash
cd mvp-doacoes
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Iniciar o sistema
```bash
python app.py
```

Acesse: **http://127.0.0.1:5000**

### Contas de teste já criadas

| Perfil    | E-mail                | Senha    |
|-----------|-----------------------|----------|
| Admin     | admin@miritiua.org    | admin123 |
| Doador    | maria@email.com       | 123456   |
| Receptor  | joao@email.com        | 123456   |

---

## Funcionalidades do MVP

- [x] Cadastro de **Doador**, **Receptor** e **Instituição**
- [x] Cadastro de equipamentos (notebook, smartphone, tablet, etc.)
- [x] Listagem e busca de equipamentos disponíveis
- [x] Solicitação de doação pelo receptor
- [x] Priorização de receptores por **urgência** (1–4)
- [x] Painel administrativo (status da doação + urgência)
- [x] Notificação via **link do WhatsApp** (sem API paga)
- [x] Autenticação simples com senha hasheada

---

## Estrutura do projeto

```
mvp-doacoes/
├── app.py                 # Aplicação principal + rotas
├── models.py              # Modelos (Usuario, Doador, Receptor, Equipamento, Doacao, Notificacao)
├── requirements.txt
├── README.md
├── schema_postgresql.sql  # Script para migrar para PostgreSQL
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── cadastro.html
    ├── equipamentos.html
    ├── novo_equipamento.html
    ├── solicitar.html
    ├── solicitacao_ok.html
    ├── minhas_doacoes_doador.html
    ├── minhas_doacoes_receptor.html
    └── admin_painel.html
```

---

## Migrar para PostgreSQL (quando quiser)

1. Crie um banco gratuito em:
   - [Neon.tech](https://neon.tech) (recomendado)
   - [Render.com](https://render.com) → PostgreSQL
   - [Railway.app](https://railway.app)
   - [ElephantSQL](https://www.elephantsql.com) (plano free)

2. Pegue a URL de conexão (ex: `postgresql://user:senha@host/db`)

3. No terminal:
```bash
export DATABASE_URL="postgresql://..."
# ou crie um arquivo .env
```

4. Instale o driver:
```bash
pip install psycopg2-binary
```

5. Execute o script SQL (`schema_postgresql.sql`) ou deixe o SQLAlchemy criar as tabelas:
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

---

## Hospedar de graça (Render.com – exemplo)

1. Suba o código no GitHub
2. Em [render.com](https://render.com) → New → Web Service
3. Conecte o repositório
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `gunicorn app:app`
6. Adicione `gunicorn` no `requirements.txt`
7. Crie um PostgreSQL gratuito no mesmo painel e vincule a variável `DATABASE_URL`

---

## Próximos passos (Atividade Extensionista III / IV)

- [ ] Upload de fotos dos equipamentos
- [ ] Filtro geográfico (proximidade)
- [ ] Relatórios de impacto social (PDF)
- [ ] Integração com WhatsApp Business API (quando houver orçamento)
- [ ] App mobile simples (PWA)
- [ ] Validação de identidade básica

---

## Licença

Projeto acadêmico – uso livre para fins educacionais e sociais.
Elaborado por Caio Henrique Da Silva Cunha – UNINTER – 2026.
=======
# doacoes_miritiua
Sistema web gratuito para conectar doadores de equipamentos tecnológicos a moradores, estudantes e instituições do bairro Miritiua (São José de Ribamar/MA)
>>>>>>> ff1353313d75eb0b773b14e65225253555218b2a
