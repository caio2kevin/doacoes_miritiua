-- Schema PostgreSQL – Sistema de Doações Miritiua
-- Execute este script em um banco PostgreSQL gratuito (Neon, Render, Railway, etc.)

CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    senha_hash VARCHAR(256) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('doador', 'receptor', 'admin', 'instituicao')),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS doador (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER UNIQUE NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    cidade VARCHAR(80) DEFAULT 'São Luís',
    bairro VARCHAR(80)
);

CREATE TABLE IF NOT EXISTS receptor (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER UNIQUE NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    bairro VARCHAR(80) DEFAULT 'Miritiua',
    urgencia INTEGER DEFAULT 2 CHECK (urgencia BETWEEN 1 AND 4),
    estudante BOOLEAN DEFAULT FALSE,
    idade_escolar BOOLEAN DEFAULT FALSE,
    observacao TEXT
);

CREATE TABLE IF NOT EXISTS instituicao (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER UNIQUE NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    nome_instituicao VARCHAR(150) NOT NULL,
    tipo VARCHAR(50),
    endereco VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS equipamento (
    id SERIAL PRIMARY KEY,
    doador_id INTEGER NOT NULL REFERENCES doador(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL,
    marca VARCHAR(60),
    modelo VARCHAR(80),
    estado VARCHAR(30) DEFAULT 'bom',
    descricao TEXT,
    disponivel BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS doacao (
    id SERIAL PRIMARY KEY,
    equipamento_id INTEGER UNIQUE NOT NULL REFERENCES equipamento(id),
    receptor_id INTEGER NOT NULL REFERENCES receptor(id),
    status VARCHAR(30) DEFAULT 'solicitada'
        CHECK (status IN ('solicitada', 'aprovada', 'em_transito', 'entregue', 'cancelada')),
    data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_entrega TIMESTAMP,
    observacao TEXT
);

CREATE TABLE IF NOT EXISTS notificacao (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id),
    doacao_id INTEGER REFERENCES doacao(id),
    mensagem TEXT NOT NULL,
    canal VARCHAR(20) DEFAULT 'whatsapp',
    enviada BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices úteis
CREATE INDEX IF NOT EXISTS idx_equipamento_disponivel ON equipamento(disponivel);
CREATE INDEX IF NOT EXISTS idx_receptor_urgencia ON receptor(urgencia DESC);
CREATE INDEX IF NOT EXISTS idx_doacao_status ON doacao(status);
