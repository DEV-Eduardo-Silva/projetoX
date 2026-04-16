import streamlit as st
import psycopg2
from datetime import datetime
import pytz

# FUSO BRASÍLIA
fuso_brasilia = pytz.timezone("America/Sao_Paulo")

st.title("🚛 Abertura de Ordem de Serviço")


# FUNÇÃO CONEXÃO

def conectar():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        sslmode="require"
    )


# INPUT PLACA

placa = st.text_input("Placa do veículo", key="placa")

st.subheader("Selecione os serviços")

# CHECKBOX SERVIÇOS

mecanica = st.checkbox("Mecânica", key="mecanica")
eletrica = st.checkbox("Elétrica", key="eletrica")
borracharia = st.checkbox("Borracharia", key="borracharia")
chapeacao = st.checkbox("Chapeação", key="chapeacao")
material = st.checkbox("Entrega de Material", key="material")
amarracao = st.checkbox("Amarração", key="amarracao")


# OBS PADRÃO (CASO NÃO MARQUE)

obs_mecanica = ""
obs_eletrica = ""
obs_borracharia = ""
obs_chapeacao = ""
obs_material = ""
obs_amarracao = ""

# CAMPOS DE OBS

if mecanica:
    obs_mecanica = st.text_area(
        "Obs Mecânica",
        value="Lubrificar e regular freios, revisar tirantes, verificar suspensão",
        key="obs_mecanica"
    )

if eletrica:
    obs_eletrica = st.text_area(
        "Obs Elétrica",
        value="Verificar parte elétrica",
        key="obs_eletrica"
    )

if borracharia:
    obs_borracharia = st.text_area(
        "Obs Borracharia",
        value="Verificar pneus e calibrar",
        key="obs_borracharia"
    )

if chapeacao:
    obs_chapeacao = st.text_area(
        "Obs Chapeação",
        value="Verificar lataria e estrutura",
        key="obs_chapeacao"
    )

if material:
    obs_material = st.text_area(
        "Obs Entrega de Material",
        value="",
        key="obs_material"
    )

if amarracao:
    obs_amarracao = st.text_area(
        "Obs Amarração",
        value="",
        key="obs_amarracao"
    )


# BOTÃO ABRIR OS

if st.button("Abrir OS"):

    if placa.strip() == "":
        st.warning("Informe a placa!")

    elif not (mecanica or eletrica or borracharia or chapeacao or material or amarracao):
        st.warning("Selecione pelo menos 1 serviço!")

    else:
        conn = conectar()
        cursor = conn.cursor()

        # VERIFICA SE PLACA EXISTE
        cursor.execute("SELECT placa FROM placas WHERE placa = %s", (placa.upper(),))
        resultado = cursor.fetchone()

        if resultado is None:
            st.error("Placa não cadastrada!")

        else:
            agora = datetime.now(fuso_brasilia)

            # CRIA OS PARA CADA SERVIÇO MARCADO
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

            if material:
                cursor.execute("""
                    INSERT INTO ordens_servico (
                        placa, tipo_servico, obs,
                        data_entrada, hora_entrada, status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    placa.upper(),
                    "Entrega de Material",
                    obs_material,
                    agora.date(),
                    agora.time(),
                    "AGUARDANDO"
                ))

            if amarracao:
                cursor.execute("""
                    INSERT INTO ordens_servico (
                        placa, tipo_servico, obs,
                        data_entrada, hora_entrada, status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    placa.upper(),
                    "Amarração",
                    obs_amarracao,
                    agora.date(),
                    agora.time(),
                    "AGUARDANDO"
                ))

            conn.commit()

            st.success("OS abertas com sucesso!")

            
            # LIMPAR CAMPOS APÓS ABRIR
           
            st.session_state["placa"] = ""
            st.session_state["mecanica"] = False
            st.session_state["eletrica"] = False
            st.session_state["borracharia"] = False
            st.session_state["chapeacao"] = False
            st.session_state["material"] = False
            st.session_state["amarracao"] = False

            st.session_state["obs_mecanica"] = ""
            st.session_state["obs_eletrica"] = ""
            st.session_state["obs_borracharia"] = ""
            st.session_state["obs_chapeacao"] = ""
            st.session_state["obs_material"] = ""
            st.session_state["obs_amarracao"] = ""

            cursor.close()
            conn.close()

            st.rerun()

        cursor.close()
        conn.close()