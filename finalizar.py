import streamlit as st
import psycopg2
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("✅ Finalização de Serviços")

# 🔐 CONEXÃO (Streamlit Cloud)
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

# 🔥 FUNÇÃO CORRETA → INTERVALO
def hora_para_intervalo(hhmm):
    try:
        h, m = hhmm.split(":")
        return timedelta(hours=int(h), minutes=int(m))
    except:
        return timedelta(0)

# 📊 BUSCA DADOS
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

        agora = datetime.now()
        inicio = datetime.combine(data_inicio, hora_inicio)
        tempo_total = agora - inicio

        # ⏱ tempo formatado
        horas = int(tempo_total.total_seconds() // 3600)
        minutos = int((tempo_total.total_seconds() % 3600) // 60)
        tempo_sugerido = f"{horas}:{minutos:02d}"

        # UI
        with st.expander(
            f"🚛 {placa} | 🔧 {tipo} | 👷 {executor1} {executor2 if executor2 else ''} | ⏱ {tempo_sugerido}",
            expanded=False
        ):

            st.write(f"📍 {rampa} | OS: {numero_os}")

            obs_final = st.text_area("Observação final", key=f"obs_{os_id}")

            col_btn1, col_btn2 = st.columns(2)

            # ✏️ EDITAR
            if col_btn1.button(f"✏️ Editar OS {numero_os}", key=f"edit_{os_id}"):
                st.session_state[f"editando_{os_id}"] = True

            if st.session_state.get(f"editando_{os_id}", False):

                st.warning("Modo edição ativo")

                novo_exec1 = st.text_input("Executor 1", value=executor1 or "", key=f"exec1_{os_id}")
                novo_exec2 = st.text_input("Executor 2", value=executor2 or "", key=f"exec2_{os_id}")

                tempo_exec1 = st.text_input("Tempo Executor 1 (h:mm)", value=tempo_sugerido, key=f"t1_{os_id}")
                tempo_exec2 = st.text_input(
                    "Tempo Executor 2 (h:mm)",
                    value=tempo_sugerido if executor2 else "0:00",
                    key=f"t2_{os_id}"
                )

                data_saida = st.date_input("Data de saída", value=agora.date(), key=f"data_{os_id}")
                hora_saida = st.time_input("Hora de saída", value=agora.time(), key=f"hora_{os_id}")

                if st.button(f"💾 Salvar edição {numero_os}", key=f"save_{os_id}"):

                    t1_intervalo = hora_para_intervalo(tempo_exec1)
                    t2_intervalo = hora_para_intervalo(tempo_exec2)

                    cursor.execute("""
                        UPDATE ordens_servico
                        SET
                            executor1 = %s,
                            executor2 = %s,
                            tempo_executor1 = %s,
                            tempo_executor2 = %s,
                            data_saida = %s,
                            hora_saida = %s
                        WHERE id = %s
                    """, (
                        novo_exec1,
                        novo_exec2 if novo_exec2 else None,
                        t1_intervalo,
                        t2_intervalo,
                        data_saida,
                        hora_saida,
                        os_id
                    ))

                    conn.commit()

                    st.success("Alterações salvas!")
                    st.session_state[f"editando_{os_id}"] = False
                    st.rerun()

            # ✅ FINALIZAR
            if col_btn2.button(f"✅ Finalizar OS {numero_os}", key=f"final_{os_id}"):

                t1_intervalo = hora_para_intervalo(tempo_sugerido)
                t2_intervalo = t1_intervalo if executor2 else timedelta(0)

                cursor.execute("""
                    UPDATE ordens_servico
                    SET
                        status = 'FINALIZADO',
                        data_saida = %s,
                        hora_saida = %s,
                        tempo_executor1 = %s,
                        tempo_executor2 = %s,
                        obs = COALESCE(obs, '') || %s
                    WHERE id = %s
                """, (
                    agora.date(),
                    agora.time(),
                    t1_intervalo,
                    t2_intervalo,
                    f" | FINAL: {obs_final}" if obs_final else "",
                    os_id
                ))

                conn.commit()

                st.success(f"OS {numero_os} finalizada!")
                st.rerun()

cursor.close()
conn.close()