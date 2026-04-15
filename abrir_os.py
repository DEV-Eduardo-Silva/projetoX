import streamlit as st
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()


st.title("🚛 Abertura de Ordem de Serviço")

# DIGITAR PLACA 
placa = st.text_input("Placa do veículo")

st.subheader("Selecione os serviços")

# CHECKBOX DOS SERVIÇOS
mecanica = st.checkbox("Mecânica")
eletrica = st.checkbox("Elétrica")
borracharia = st.checkbox("Borracharia")
chapeacao = st.checkbox("Chapeação")
material = st.checkbox("Entrega de Material")
amarracao = st.checkbox("Amarração")

# OBS (INICIA VAZIO)
obs_mecanica = ""
obs_eletrica = ""
obs_borracharia = ""
obs_chapeacao = ""
obs_material = ""
obs_amarracao = ""

#  SE MARCAR, APARECE O CAMPO PARA DIGITAR OBS (ALGUNS JA VEM PREENCHIDO CONFORME OQ ANDERSON JA DIGITA)
if mecanica:
    obs_mecanica = st.text_area(
        "Obs Mecânica",
        value="Lubrificar e regular freios, revisar tirantes, verificar suspensão"
    )

if eletrica:
    obs_eletrica = st.text_area(
        "Obs Elétrica",
        value="Verificar parte elétrica"
    )

if borracharia:
    obs_borracharia = st.text_area(
        "Obs Borracharia",
        value="Verificar pneus e calibrar"
    )

if chapeacao:
    obs_chapeacao = st.text_area(
        "Obs Chapeação",
        value="Verificar lataria e estrutura"
    )

#  BOTÃO
if st.button("Abrir OS"):

    #  VALIDAÇÃO SIMPLES ONDE VAI FAZER BUSCA NO BANCO DE DADOS PARA VALIDAR PLACA
    if placa == "":
        st.warning("Informe a placa!")

    else:
        #  CONECTA NO BANCO = PRECISO PRIVAR PARA NAO DEIXAR A MOSTRA SENHA E BANCO
        conn = psycopg2.connect(
            host=st.secrets["DB_HOST"],
            port=st.secrets["DB_PORT"],
            database=st.secrets["DB_NAME"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            sslmode="require"
        )

        cursor = conn.cursor()

        #  VERIFICA SE A PLACA EXISTE
        cursor.execute(
            "SELECT placa FROM placas WHERE placa = %s",
            (placa.upper(),)
        )

        resultado = cursor.fetchone()

        #  SE NÃO EXISTIR
        if resultado is None:
            st.error("Placa não cadastrada!")

        else:
            agora = datetime.now()

            #  PARA CADA SERVIÇO MARCADO → CRIA UMA OS

            if mecanica:
                cursor.execute("""
                    INSERT INTO ordens_servico (
                        placa, tipo_servico, obs,
                        data_entrada, hora_entrada, status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    placa.upper(),
                    "Mecânica",
                    obs_mecanica,
                    agora.date(),
                    agora.time(),
                    "AGUARDANDO"
                ))

            if eletrica:
                cursor.execute("""
                    INSERT INTO ordens_servico (
                        placa, tipo_servico, obs,
                        data_entrada, hora_entrada, status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    placa.upper(),
                    "Elétrica",
                    obs_eletrica,
                    agora.date(),
                    agora.time(),
                    "AGUARDANDO"
                ))

            if borracharia:
                cursor.execute("""
                    INSERT INTO ordens_servico (
                        placa, tipo_servico, obs,
                        data_entrada, hora_entrada, status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    placa.upper(),
                    "Borracharia",
                    obs_borracharia,
                    agora.date(),
                    agora.time(),
                    "AGUARDANDO"
                ))

            if chapeacao:
                cursor.execute("""
                    INSERT INTO ordens_servico (
                        placa, tipo_servico, obs,
                        data_entrada, hora_entrada, status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    placa.upper(),
                    "Chapeação",
                    obs_chapeacao,
                    agora.date(),
                    agora.time(),
                    "AGUARDANDO"
                ))

            conn.commit()

            st.success("OS abertas com sucesso!")
            st.rerun()

        cursor.close()
        conn.close()