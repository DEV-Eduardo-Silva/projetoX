import streamlit as st
import psycopg2
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os


load_dotenv()

st.set_page_config(layout="wide")
st.title("📊 Dashboard Oficina")


# CONEXÃO (AINDA PRECISO PRIVAR)
 
conn = psycopg2.connect(
       host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()


#  FILTRO

col_data1, col_data2 = st.columns(2)
data_inicio = col_data1.date_input("Data início", datetime.now().date())
data_fim = col_data2.date_input("Data fim", datetime.now().date())


#  KPIs

cursor.execute("""
    SELECT COUNT(*) FROM ordens_servico
    WHERE data_inicio BETWEEN %s AND %s
""", (data_inicio, data_fim))
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM ordens_servico WHERE status = 'EM MANUTENÇÃO'")
em_manutencao = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM ordens_servico WHERE status = 'FINALIZADO'")
finalizados = cursor.fetchone()[0]

k1, k2, k3 = st.columns(3)
k1.metric("TOTAL OS", total)
k2.metric("EM MANUTENÇÃO", em_manutencao)
k3.metric("FINALIZADAS", finalizados)

st.divider()


# LAYOUT

col_main, col_side = st.columns([3, 1])


# FUNÇÃO TEMPO

def formatar_tempo(delta):
    horas = int(delta.total_seconds() // 3600)
    minutos = int((delta.total_seconds() % 3600) // 60)
    return f"{horas}h {minutos}min"


#  RAMPAS

with col_main:

    st.subheader("🔧 Rampas")

    lista_rampas = ["BOX 1", "BOX 2", "BOX 3", "BOX CHAPEAÇÃO", "BOX BORRACHARIA", "POSTO"]

    cursor.execute("""
        SELECT placa, tipo_servico, executor1, executor2, numero_os, rampa, data_inicio, hora_inicio
        FROM ordens_servico
        WHERE status = 'EM MANUTENÇÃO'
    """)

    dados = cursor.fetchall()

    rampas_ocupadas = {}

    for row in dados:
        placa, tipo, exec1, exec2, os_num, rampa, data_i, hora_i = row

        inicio = datetime.combine(data_i, hora_i)
        tempo = datetime.now() - inicio

        rampas_ocupadas[rampa] = {
            "placa": placa,
            "tipo": tipo,
            "exec": f"{exec1} {exec2 if exec2 else ''}",
            "os": os_num,
            "tempo": formatar_tempo(tempo)
        }

    cols = st.columns(3)

    for i, rampa in enumerate(lista_rampas):

        with cols[i % 3]:

            if rampa in rampas_ocupadas:
                s = rampas_ocupadas[rampa]

                st.error(f"""
🔴 {rampa} - OCUPADO

🚛 {s['placa']}
🔧 {s['tipo']}
👷 {s['exec']}
📄 OS {s['os']}
⏱ {s['tempo']}
""")
            else:
                st.success(f"🟢 {rampa} - LIVRE")


#  AGUARDANDO

with col_side:

    st.subheader("🚗 Aguardando")

    cursor.execute("""
        SELECT 
            placa,
            STRING_AGG(tipo_servico, ' / ') AS servicos,
            MIN(data_entrada + hora_entrada) AS inicio_espera
        FROM ordens_servico
        WHERE status = 'AGUARDANDO'
        GROUP BY placa
        ORDER BY inicio_espera
    """)

    aguardando = cursor.fetchall()

    if not aguardando:
        st.success("Nenhum aguardando")

    else:
        for placa, servicos, inicio in aguardando:

            tempo = datetime.now() - inicio
            tempo_formatado = formatar_tempo(tempo)

            if tempo.total_seconds() > 7200:
                st.error(f"{placa} | {tempo_formatado} | {servicos}")
            else:
                st.info(f"{placa} | {tempo_formatado} | {servicos}")


# ⏱ TEMPO MÉDIO

with st.container():

    st.subheader("⏱ Tempo médio para entrar na oficina")

    cursor.execute("""
        SELECT 
            AVG((data_inicio + hora_inicio) - (data_entrada + hora_entrada))
        FROM ordens_servico
        WHERE data_entrada IS NOT NULL 
        AND data_inicio IS NOT NULL
    """)

    tempo_medio = cursor.fetchone()[0]

    if tempo_medio:

        total_segundos = tempo_medio.total_seconds()
        horas = int(total_segundos // 3600)
        minutos = int((total_segundos % 3600) // 60)

        tempo_formatado = f"{horas}h {minutos}min"

        st.success(f"Tempo médio: {tempo_formatado}")

    else:
        st.info("Sem dados de tempo médio")


#  RANKING (PERFORMAR, COMPARAR HRS QTD OS, TOTAL OS)

with st.expander("📊 Ranking e Produtividade", expanded=False):

    col_g1, col_g2 = st.columns(2)

    # TEMPO EM HORAS
    cursor.execute("""
        SELECT executor1 AS mecanico, 
        EXTRACT(EPOCH FROM SUM(tempo_executor1)) / 3600
        FROM ordens_servico
        WHERE executor1 IS NOT NULL AND executor1 <> ''
        GROUP BY executor1

        UNION ALL

        SELECT executor2,
        EXTRACT(EPOCH FROM SUM(tempo_executor2)) / 3600
        FROM ordens_servico
        WHERE executor2 IS NOT NULL AND executor2 <> ''
        GROUP BY executor2;
    """)

    dados = cursor.fetchall()

    df = pd.DataFrame(dados, columns=["mecanico", "horas"])
    df = df.groupby("mecanico").sum().sort_values(by="horas", ascending=False)

    with col_g1:
        st.markdown("### ⏱ Tempo por mecânico")

        if not df.empty:
            fig, ax = plt.subplots()
            ax.bar(df.index, df["horas"])
            ax.set_ylabel("Horas trabalhadas")
            st.pyplot(fig)

            top = df.iloc[0]
            st.success(f"🏆 Melhor mecânico: {top.name} ({round(top['horas'],2)}h)")
        else:
            st.info("Sem dados")

    # PRODUTIVIDADE
    cursor.execute("""
        SELECT executor1 AS mecanico, COUNT(*)
        FROM ordens_servico
        WHERE status = 'FINALIZADO' AND executor1 IS NOT NULL AND executor1 <> ''
        GROUP BY executor1

        UNION ALL

        SELECT executor2, COUNT(*)
        FROM ordens_servico
        WHERE executor2 IS NOT NULL AND executor2 <> '' AND status = 'FINALIZADO'
        GROUP BY executor2;
    """)

    dados = cursor.fetchall()

    df2 = pd.DataFrame(dados, columns=["mecanico", "qtd"])
    df2 = df2.groupby("mecanico").sum().sort_values(by="qtd", ascending=False)

    with col_g2:
        st.markdown("### 📈 Produtividade")

        if not df2.empty:
            fig2, ax2 = plt.subplots()
            ax2.bar(df2.index, df2["qtd"])
            ax2.set_ylabel("OS finalizadas")
            st.pyplot(fig2)

            top2 = df2.iloc[0]
            st.success(f"🚀 Mais produtivo: {top2.name} ({int(top2['qtd'])} OS)")
        else:
            st.info("Sem dados")


#  FINAL

cursor.close()
conn.close()