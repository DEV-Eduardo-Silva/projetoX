import streamlit as st

st.set_page_config(layout="wide")


# LOGIN SIMPLES AINDA SEM SENHA, VERIFICAR COM HENART NECESSIDADE

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:

    st.title("🔐 Sistema Oficina")
    st.markdown("### Escolha o usuário:")

    col1, col2, col3 = st.columns(3)

    if col1.button("👷 Anderson"):
        st.session_state.usuario = "anderson"
        st.rerun()

    if col2.button("🔧 Alexandre"):
        st.session_state.usuario = "alexandre"
        st.rerun()

    if col3.button("📊 Gestão"):
        st.session_state.usuario = "gestao"
        st.rerun()

    st.stop()


# PERFIL

usuario = st.session_state.usuario
st.sidebar.title(f"👤 {usuario.capitalize()}")

# MENU
if usuario == "anderson":
    menu = st.sidebar.selectbox("Menu", ["Abrir OS"])

elif usuario == "alexandre":
    menu = st.sidebar.selectbox("Menu", ["Executar OS", "Finalizar OS"])

elif usuario == "gestao":
    menu = st.sidebar.selectbox("Menu", ["Dashboard"])


 # NAVEGAÇÃO

if menu == "Dashboard":
    exec(open("dashboard.py").read())

elif menu == "Abrir OS":
    exec(open("abrir_os.py").read())

elif menu == "Executar OS":
    exec(open("iniciar_os.py").read())

elif menu == "Finalizar OS":
    exec(open("finalizar.py").read())
    
elif menu == "Cadastrar Placas":
    exec(open("cadastroplacas.py").read())


#  SAIR

st.sidebar.divider()

if st.sidebar.button(" Trocar usuário"):
    st.session_state.usuario = None
    st.rerun()