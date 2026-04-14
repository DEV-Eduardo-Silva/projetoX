import psycopg2
import streamlit as st
from dotenv import load_dotenv
import os

print("INICIANDO...")
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
CREATE TABLE IF NOT EXISTS placas (
    id SERIAL PRIMARY KEY,
    placa VARCHAR(10) UNIQUE
);
""")

conn.commit()

print("Tabela placas criada!")

cursor.close()
conn.close()

print("FINALIZOU!")