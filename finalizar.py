import streamlit as st
import psycopg2
from datetime import datetime, timedelta
import pytz

fuso_brasilia = pytz.timezone("America/Sao_Paulo")

st.set_page_config(layout="wide")
st.title("Finalização de Serviços")

def conectar():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        port=5432,
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        sslmode="require"
    )

def formatar_timedelta(td):
    total_segundos = int(td.total_seconds())
    if total_segundos < 0:
        total_segundos = 0

    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    return f"{horas}:{minutos:02d}"

conn = conectar()
cursor = conn.cursor()

cursor.execute("""
    SELECT id, numero_os, placa, tipo_servico, data_inicio, hora_inicio, executor1, executor2, rampa
    FROM ordens_servico
    WHERE status = 'EM MANUTENÇÃO'
    ORDER BY data_inicio DESC, hora_inicio DESC
""")

dados = cursor.fetchall()

if len(dados) == 0:
    st.info("Nenhum serviço em andamento")

else:
    for os in dados:

        os_id, numero_os, placa, tipo, data_inicio, hora_inicio, executor1, executor2, rampa = os

        agora = datetime.now(fuso_brasilia)

        if data_inicio is None or hora_inicio is None:
            st.error(f"OS {numero_os} está sem data_inicio ou hora_inicio no banco.")
            continue

        inicio = fuso_brasilia.localize(datetime.combine(data_inicio, hora_inicio))
        tempo_total = agora - inicio

        if tempo_total.total_seconds() < 0:
            tempo_total = timedelta(0)

        tempo_sugerido = formatar_timedelta(tempo_total)

        lista_exec1 = ["Adilso", "Fabio", "Valdir", "Leandro", "Jesus", "Evandro", "Aleson", "Marcos", "Dionathan"]
        lista_exec2 = [""] + lista_exec1

        executor1 = (executor1 or "").strip()
        executor2 = (executor2 or "").strip()

        with st.expander(
            f"{placa} | {tipo} | {executor1} {executor2 if executor2 else ''} | {tempo_sugerido}",
            expanded=False
        ):

            st.write(f"{rampa} | OS: {numero_os}")

            obs_final = st.text_area("Observação final", key=f"obs_{os_id}")

            col_btn1, col_btn2 = st.columns(2)

            # BOTÃO FINALIZAR (ABRE MODO FINALIZAÇÃO)
            if col_btn2.button(f"Finalizar OS {numero_os}", key=f"btn_final_{os_id}"):
                st.session_state[f"finalizando_{os_id}"] = True

            if st.session_state.get(f"finalizando_{os_id}", False):

                st.warning("Modo finalização ativo")

                # EXECUTOR 1
                if executor1 in lista_exec1:
                    index_exec1 = lista_exec1.index(executor1)
                else:
                    index_exec1 = 0

                # EXECUTOR 2
                if executor2 in lista_exec2:
                    index_exec2 = lista_exec2.index(executor2)
                else:
                    index_exec2 = 0

                novo_exec1 = st.selectbox(
                    "Executor 1",
                    lista_exec1,
                    index=index_exec1,
                    key=f"exec1_final_{os_id}"
                )

                novo_exec2 = st.selectbox(
                    "Executor 2",
                    lista_exec2,
                    index=index_exec2,
                    key=f"exec2_final_{os_id}"
                )

                tempo_exec1 = st.text_input(
                    "Tempo Executor 1 (h:mm)",
                    value=tempo_sugerido,
                    key=f"tempo1_final_{os_id}"
                )

                tempo_exec2 = ""
                if novo_exec2 and novo_exec2.strip() != "":
                    tempo_exec2 = st.text_input(
                        "Tempo Executor 2 (h:mm)",
                        value=tempo_sugerido,
                        key=f"tempo2_final_{os_id}"
                    )

                data_saida = st.date_input(
                    "Data de saída",
                    value=agora.date(),
                    key=f"data_saida_final_{os_id}"
                )

                hora_saida = st.time_input(
                    "Hora de saída",
                    value=agora.time(),
                    key=f"hora_saida_final_{os_id}"
                )

                if st.button(f"Confirmar Finalização OS {numero_os}", key=f"confirm_final_{os_id}"):

                    cursor.execute("""
                        UPDATE ordens_servico
                        SET
                            status = 'FINALIZADO',
                            executor1 = %s,
                            executor2 = %s,
                            data_saida = %s,
                            hora_saida = %s,
                            tempo_executor1 = (%s || ':00')::interval,
                            tempo_executor2 = CASE
                                WHEN %s IS NULL OR %s = '' THEN NULL
                                ELSE (%s || ':00')::interval
                            END,
                            hora_maodeobra = (
                                hora_inicio::interval +
                                CASE
                                    WHEN %s IS NULL OR %s = '' THEN (%s || ':00')::interval
                                    ELSE (%s || ':00')::interval
                                END
                            )::time,
                            obs = COALESCE(obs, '') || %s
                        WHERE id = %s
                    """, (
                        novo_exec1,
                        novo_exec2 if novo_exec2.strip() != "" else None,
                        data_saida,
                        hora_saida,
                        tempo_exec1,
                        tempo_exec2, tempo_exec2, tempo_exec2,
                        tempo_exec2, tempo_exec2,
                        tempo_exec1,
                        tempo_exec2,
                        f" | FINAL: {obs_final}" if obs_final else "",
                        os_id
                    ))

                    conn.commit()

                    st.success(f"OS {numero_os} finalizada com sucesso!")
                    st.session_state[f"finalizando_{os_id}"] = False
                    st.rerun()

cursor.close()
conn.close()