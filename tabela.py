import psycopg2
from dotenv import load_dotenv
import streamlit as st
import os

print("INICIANDO SCRIPT...")
load_dotenv()
conn = psycopg2.connect(
    host=st.secrets["DB_HOST"],
    port=st.secrets["DB_PORT"],
    database=st.secrets["DB_NAME"],
    user=st.secrets["DB_USER"],
    password=st.secrets["DB_PASSWORD"],
    sslmode="require"
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS ordens_servico (
    id SERIAL PRIMARY KEY,
    placa VARCHAR(10),
    tipo_servico VARCHAR(20),
    obs TEXT,
    data_entrada DATE,
    hora_entrada TIME,
    status VARCHAR(20) DEFAULT 'AGUARDANDO',
    rampa VARCHAR(10),
    executor1 VARCHAR(50),
    executor2 VARCHAR(50),
    data_inicio DATE,
    hora_inicio TIME,
    data_saida DATE,
    hora_saida TIME,
    tempo_executor1 INTEGER,
    tempo_executor2 INTEGER,
    obs_execucao TEXT,
    obs_final TEXT,
    gatilho_uipath VARCHAR(20)
);
""")

conn.commit()

print("Tabela criada com sucesso!")

cursor.close()
conn.close()

print("FINALIZOU!")