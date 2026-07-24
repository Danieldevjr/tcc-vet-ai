import streamlit as st
from database import autenticar_usuario, cadastrar_usuario

def render_login_screen():
    st.title("Vet.AI - Acesso ao Sistema")
    
    tab_login, tab_cadastro = st.tabs(["🔒 Entrar", "📝 Criar Conta"])
    
    # ABA DE LOGIN
    with tab_login:
        st.subheader("Login de Acesso")
        email = st.text_input("E-mail Institucional", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")
        
        if st.button("Aceder ao Sistema", type="primary"):
            if email and senha:
                user = autenticar_usuario(email, senha)
                if user:
                    st.session_state["usuario_logado"] = user
                    st.success(f"Bem-vindo(a), {user['nome']}!")
                    st.rerun()
                else:
                    st.error("E-mail ou senha incorretos.")
            else:
                st.warning("Preencha todos os campos.")

    # ABA DE CADASTRO
    with tab_cadastro:
        st.subheader("Novo Registo")
        nome = st.text_input("Nome Completo", key="reg_nome")
        email = st.text_input("E-mail", key="reg_email")
        senha = st.text_input("Senha", type="password", key="reg_senha")
        role = st.selectbox("Perfil de Acesso", ["aluno", "admin"], key="reg_role")
        
        # Chave de segurança opcional para criar conta Admin
        chave_admin = ""
        if role == "admin":
            chave_admin = st.text_input("Chave de Validação Admin", type="password")
            
        if st.button("Cadastrar Conta"):
            if nome and email and senha:
                if role == "admin" and chave_admin != "vetai2026": # Defina a sua chave secreta
                    st.error("Chave de segurança de Administrador inválida.")
                else:
                    sucesso = cadastrar_usuario(nome, email, senha, role)
                    if sucesso:
                        st.success("Conta criada com sucesso! Faça login na aba ao lado.")
                    else:
                        st.error("Este e-mail já está registado no sistema.")
            else:
                st.warning("Preencha todos os campos obrigatórios.")