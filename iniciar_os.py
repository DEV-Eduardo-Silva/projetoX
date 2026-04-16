import streamlit as st
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os
import pytz

# FUSO BRASILIA
fuso_brasilia = pytz.timezone("America/Sao_Paulo")

load_dotenv()
st.title("🧑‍🔧 Início de Serviços")

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()

# PLACAS ÚNICAS
cursor.execute("""
    SELECT DISTINCT placa
    FROM ordens_servico
    WHERE status = 'AGUARDANDO'
    AND (inicio_servico IS NULL OR inicio_servico != 'SIM')
    ORDER BY placa
""")

placas = cursor.fetchall()

if len(placas) == 0:
    st.info("Nenhum serviço disponível")

else:
    for p in placas:

        placa = p[0]

        st.markdown(f"## 🚛 {placa}")

        # SERVIÇOS DESSA PLACA
        cursor.execute("""
            SELECT id, tipo_servico, obs
            FROM ordens_servico
            WHERE placa = %s
            AND status = 'AGUARDANDO'
            AND (inicio_servico IS NULL OR inicio_servico != 'SIM')
        """, (placa,))

        servicos = cursor.fetchall()

        selecionados = []

        for s in servicos:
            os_id = s[0]
            tipo = s[1]
            obs_original = s[2]

            col1, col2 = st.columns([3,1])

            with col1:
                marcado = st.checkbox(tipo, key=f"check_{os_id}")

            with col2:
        
                # BOTÃO CANCELAR
                if st.button("❌ Cancelar", key=f"cancel_{os_id}"):
                    cursor.execute("""
                        UPDATE ordens_servico
                        SET status = 'CANCELADO'
                        WHERE id = %s
                    """, (os_id,))
                    conn.commit()
                    st.success(f"OS {os_id} cancelada!")
                    st.rerun()

            if marcado:

                executor1 = st.selectbox(
                    "Executor 1",
                    ["Adilso", "Fabio", "Valdir", "Leandro", "Jesus", "Evandro", "Aleson", "Marcos", "Dionathan"],
                    key=f"exec1_{os_id}"
                )

                executor2 = st.selectbox(
                    "Executor 2",
                    ["", "Adilso", "Fabio", "Valdir", "Leandro", "Jesus", "Evandro", "Aleson", "Marcos", "Dionathan"],
                    key=f"exec2_{os_id}"
                )

                rampa = st.selectbox(
                    "Box",
                    ["BOX 1", "BOX 2", "BOX 3", "BOX CHAPEAÇÃO", "BOX BORRACHARIA", "POSTO"],
                    key=f"rampa_{os_id}"
                )

                obs_editada = st.text_area(
                    "Observação",
                    value=obs_original,
                    key=f"obs_{os_id}"
                )

                selecionados.append((os_id, executor1, executor2, rampa, obs_editada))

        # BOTÃO INICIAR
        if st.button(f"Iniciar serviços {placa}"):

            if len(selecionados) == 0:
                st.warning("Selecione pelo menos um serviço")

            else:
                agora = datetime.now(fuso_brasilia)

                for item in selecionados:
                    os_id = item[0]
                    executor1 = item[1]
                    executor2 = item[2]
                    rampa = item[3]
                    obs_final = item[4]

                    cursor.execute("""
                        UPDATE ordens_servico
                        SET
                            status = 'EM MANUTENÇÃO',
                            inicio_servico = 'SIM',
                            obs = %s,
                            rampa = %s,
                            executor1 = %s,
                            executor2 = %s,
                            data_inicio = %s,
                            hora_inicio = %s
                        WHERE id = %s
                    """, (
                        obs_final,
                        rampa,
                        executor1,
                        executor2,
                        agora.date(),
                        agora.time(),
                        os_id
                    ))

                conn.commit()

                st.success(f"Serviços da placa {placa} iniciados!")
                st.rerun()


cursor.close()
conn.close()