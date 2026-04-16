import streamlit as st
import psycopg2
from datetime import datetime, timedelta
import pytz

fuso_brasilia = pytz.timezone("America/Sao_Paulo")

st.set_page_config(layout="wide")
st.title("Finalização de Serviços")

# CONEXAO (Streamlit Cloud)
def conectar():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        port=5432,
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        sslmode="require"
    )

conn = conectar()
cursor = conn.cursor()

# FUNCAO INTERVALO
def hora_para_intervalo(hhmm):
    try:
        h, m = hhmm.split(":")
        return timedelta(hours=int(h), minutes=int(m))
    except:
        return timedelta(0)

# BUSCA DADOS
cursor.execute("""
    SELECT id, numero_os, placa, tipo_servico, data_inicio, hora_inicio, executor1, executor2, rampa
    FROM ordens_servico
    WHERE status = 'EM MANUTENÇÃO'
""")

dados = cursor.fetchall()

if len(dados) == 0:
    st.info("Nenhum serviço em andamento")

else:
    for os in dados:

        os_id, numero_os, placa, tipo, data_inicio, hora_inicio, executor1, executor2, rampa = os

        agora = datetime.now(fuso_brasilia)

        # VALIDACAO PARA NAO QUEBRAR SE ESTIVER NULO
        if data_inicio is None or hora_inicio is None:
            st.error(f"OS {numero_os} está sem data_inicio ou hora_inicio no banco.")
            continue

        inicio = fuso_brasilia.localize(datetime.combine(data_inicio, hora_inicio))
        tempo_total = agora - inicio

        # SE TEMPO DER NEGATIVO, ZERA
        if tempo_total.total_seconds() < 0:
            tempo_total = timedelta(0)

        # TEMPO FORMATADO
        horas = int(tempo_total.total_seconds() // 3600)
        minutos = int((tempo_total.total_seconds() % 3600) // 60)
        tempo_sugerido = f"{horas}:{minutos:02d}"

        # UI
        with st.expander(
            f"{placa} | {tipo} | {executor1} {executor2 if executor2 else ''} | {tempo_sugerido}",
            expanded=False
        ):

            st.write(f"{rampa} | OS: {numero_os}")

            obs_final = st.text_area("Observação final", key=f"obs_{os_id}")

            col_btn1, col_btn2 = st.columns(2)

            # EDITAR
            if col_btn1.button(f"Editar OS {numero_os}", key=f"edit_{os_id}"):
                st.session_state[f"editando_{os_id}"] = True

            if st.session_state.get(f"editando_{os_id}", False):

                st.warning("Modo edição ativo")

                lista_exec1 = ["Adilso", "Fabio", "Valdir", "Leandro", "Jesus", "Evandro", "Aleson", "Marcos", "Dionathan"]
                lista_exec2 = [""] + lista_exec1

                # DEFINE INDEX EXECUTOR 1
                if executor1 in lista_exec1:
                    index_exec1 = lista_exec1.index(executor1)
                else:
                    index_exec1 = 0

                # DEFINE INDEX EXECUTOR 2
                if executor2 in lista_exec2:
                    index_exec2 = lista_exec2.index(executor2)
                else:
                    index_exec2 = 0

                novo_exec1 = st.selectbox(
                    "Executor 1",
                    lista_exec1,
                    index=index_exec1,
                    key=f"exec1_{os_id}"
                )

                novo_exec2 = st.selectbox(
                    "Executor 2",
                    lista_exec2,
                    index=index_exec2,
                    key=f"exec2_{os_id}"
                )

                tempo_exec1 = st.text_input(
                    "Tempo Executor 1 (h:mm)",
                    value=tempo_sugerido,
                    key=f"t1_{os_id}"
                )

                tempo_exec2 = "0:00"
                if novo_exec2 and novo_exec2.strip() != "":
                    tempo_exec2 = st.text_input(
                        "Tempo Executor 2 (h:mm)",
                        value=tempo_sugerido,
                        key=f"t2_{os_id}"
                    )

                data_saida = st.date_input("Data de saída", value=agora.date(), key=f"data_{os_id}")
                hora_saida = st.time_input("Hora de saída", value=agora.time(), key=f"hora_{os_id}")

                if st.button(f"Salvar edição {numero_os}", key=f"save_{os_id}"):

                    cursor.execute("""
                        UPDATE ordens_servico
                        SET
                            executor1 = %s,
                            executor2 = %s,
                            tempo_executor1 = (%s || ':00')::interval,
                            tempo_executor2 = CASE
                                WHEN %s IS NULL OR %s = '' THEN NULL
                                ELSE (%s || ':00')::interval
                            END,
                            hora_maodeobra = (hora_inicio + (%s || ':00')::interval),
                            data_saida = %s,
                            hora_saida = %s
                        WHERE id = %s
                    """, (
                        novo_exec1,
                        novo_exec2 if novo_exec2 else None,
                        tempo_exec1,
                        novo_exec2,
                        novo_exec2,
                        tempo_exec2,
                        tempo_exec1,
                        data_saida,
                        hora_saida,
                        os_id
                    ))

                    conn.commit()

                    st.success("Alterações salvas!")
                    st.session_state[f"editando_{os_id}"] = False
                    st.rerun()

            # FINALIZAR
            if col_btn2.button(f"Finalizar OS {numero_os}", key=f"final_{os_id}"):

                cursor.execute("""
                    UPDATE ordens_servico
                    SET
                        status = 'FINALIZADO',
                        data_saida = %s,
                        hora_saida = %s,
                        tempo_executor1 = (%s || ':00')::interval,
                        tempo_executor2 = CASE
                            WHEN executor2 IS NULL OR executor2 = '' THEN NULL
                            ELSE (%s || ':00')::interval
                        END,
                        hora_maodeobra = (hora_inicio + (%s || ':00')::interval),
                        obs = COALESCE(obs, '') || %s
                    WHERE id = %s
                """, (
                    agora.date(),
                    agora.time(),
                    tempo_sugerido,
                    tempo_sugerido,
                    tempo_sugerido,
                    f" | FINAL: {obs_final}" if obs_final else "",
                    os_id
                ))

                conn.commit()

                st.success(f"OS {numero_os} finalizada!")
                st.rerun()

cursor.close()
conn.close()