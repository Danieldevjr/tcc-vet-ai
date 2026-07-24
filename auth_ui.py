import streamlit as st
from database import autenticar_usuario, cadastrar_usuario

def render_login_screen():
    # Cria três colunas na tela. A do meio (largura 2) será o nosso card de login centralizado.
    col_espaco_esq, col_central, col_espaco_dir = st.columns([1, 2, 1])
    
    with col_central:
        # Espaçamento vertical inicial
        st.write("")
        st.write("")
        
        # Container com borda para simular um "Card" moderno de Login
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center; color: #005088; margin-bottom: 0;'>🐾 Vet.AI</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px;'>Triagem Dermatológica Inteligente</p>", unsafe_allow_html=True)
            st.markdown("---")
            
            # Abas para alternar entre entrar e criar conta
            tab_login, tab_cadastro = st.tabs(["🔒 Acessar Sistema", "📝 Criar Nova Conta"])
            
            # --- ABA DE LOGIN ---
            with tab_login:
                st.write("")
                email = st.text_input("E-mail Institucional", placeholder="exemplo@ufrn.br", key="login_email")
                senha = st.text_input("Senha de Acesso", type="password", placeholder="Digite sua senha", key="login_senha")
                st.write("")
                
                # Botão de login ocupando toda a largura para ficar mais moderno
                if st.button("Entrar no Vet.AI", type="primary", use_container_width=True):
                    if email and senha:
                        user = autenticar_usuario(email, senha)
                        if user:
                            st.session_state["usuario_logado"] = user
                            st.success(f"Autenticado com sucesso! Entrando...")
                            st.rerun()
                        else:
                            st.error("E-mail ou senha incorretos.")
                    else:
                        st.warning("Por favor, preencha todos os campos.")

            # --- ABA DE CADASTRO ---
            with tab_cadastro:
                st.write("")
                nome = st.text_input("Nome Completo", placeholder="Seu nome completo", key="reg_nome")
                email = st.text_input("E-mail para Registro", placeholder="Seu melhor e-mail", key="reg_email")
                senha = st.text_input("Definir Senha", type="password", placeholder="Crie uma senha forte", key="reg_senha")
                
                role = st.selectbox("Perfil de Acesso", ["aluno", "admin"], key="reg_role")
                
                # Exibe o campo extra de segurança apenas se escolher Admin
                chave_admin = ""
                if role == "admin":
                    st.markdown("<small style='color: #64748b;'>Apenas para professores e administradores autorizados:</small>", unsafe_allow_html=True)
                    chave_admin = st.text_input("Chave de Validação Admin", type="password", placeholder="Insira a chave do projeto")
                
                st.write("")
                
                if st.button("Finalizar Cadastro", use_container_width=True):
                    if nome and email and senha:
                        if role == "admin" and chave_admin != "vetai2026":
                            st.error("Chave de validação de Administrador inválida.")
                        else:
                            sucesso = cadastrar_usuario(nome, email, senha, role)
                            if sucesso:
                                st.success("Conta criada! Alterne para a aba 'Acessar Sistema' para fazer login.")
                            else:
                                st.error("Este e-mail já está registrado no sistema.")
                    else:
                        st.warning("Preencha todos os campos obrigatórios.")