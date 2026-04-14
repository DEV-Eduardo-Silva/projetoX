import streamlit as st
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

st.subheader("📋 Cadastro de Placas")

placas_texto = st.text_area("Cole as placas (uma por linha)")

if st.button("Salvar placas"):
    if placas_texto == "":
        st.warning("Cole alguma placa!")
    else:
        conn = psycopg2.connect(
            host=st.secrets["DB_HOST"],
            port=st.secrets["DB_PORT"],
            database=st.secrets["DB_NAME"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            sslmode="require"
        )
        
        cursor = conn.cursor()

        lista = placas_texto.split("\n")

        for p in lista:
            placa = p.strip().upper()
            if placa != "":
                cursor.execute("""
                    INSERT INTO placas (placa)
                    VALUES (%s)
                    ON CONFLICT (placa) DO NOTHING
                """, (placa,))

        conn.commit()

        st.success("Placas cadastradas!")

        cursor.close()
        conn.close()