import psycopg2
from dotenv import load_dotenv
import streamlit as st
import os
load_dotenv()
# conexão com o postgres padrão
conn = psycopg2.connect(
    conn = psycopg2.connect(
    host=st.secrets["DB_HOST"],
    port=st.secrets["DB_PORT"],
    database=st.secrets["DB_NAME"],
    user=st.secrets["DB_USER"],
    password=st.secrets["DB_PASSWORD"],
    sslmode="require"
)
)

conn.autocommit = True
cursor = conn.cursor()

# cria o banco
cursor.execute("CREATE DATABASE oficina_db;")

print("Banco criado com sucesso!")

cursor.close()
conn.close()