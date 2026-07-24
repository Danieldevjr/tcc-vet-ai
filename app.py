import streamlit as st
import os
from database import inicializar_banco, carregar_historico, salvar_diagnostico
from auth_ui import render_login_screen
from pdf_generator import gerar_laudo_pdf

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Vet.AI - Triagem Dermatológica",
    page_icon="🐾",
    layout="wide"
)

# Garante que o banco de dados e as tabelas existam no servidor
inicializar_banco()

# Inicializa o estado da sessão de login se não existir
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None

# 1. FLUXO DE AUTENTICAÇÃO
if st.session_state["usuario_logado"] is None:
    render_login_screen()
    st.stop()  # Interrompe a execução aqui até o usuário se logar

# Recupera os dados do usuário logado
user = st.session_state["usuario_logado"]

# 2. BARRA LATERAL (SIDEBAR)
st.sidebar.title("🐾 Vet.AI Dashboard")
st.sidebar.markdown(f"**Usuário:** {user['nome']}")
st.sidebar.markdown(f"**Perfil:** `{user['role'].upper()}`")

# Botão de Logout
if st.sidebar.button("Sair (Logout)", type="secondary"):
    st.session_state["usuario_logado"] = None
    st.rerun()

st.sidebar.markdown("---")

# Menu de navegação interno do sistema
menu = st.sidebar.radio("Navegação", ["Nova Triagem", "Histórico Clínico"])

# 3. MÓDULO: NOVA TRIAGEM
if menu == "Nova Triagem":
    st.title("🔬 Triagem Dermatológica Avançada")
    st.write("Insira os dados do prontuário e anexe a foto da lesão para análise do Comitê de IA.")

    # Formuário do Prontuário Clínico
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        nome_tutor = st.text_input("Nome do Tutor(a)")
        nome_animal = st.text_input("Nome do Paciente (Animal)")
    with col_t2:
        especie = st.selectbox("Espécie", ["Cão", "Gato"])
        idade = st.number_input("Idade (Anos)", min_value=0, max_value=30, value=1)

    st.markdown("---")
    
    # Upload da Imagem da Lesão
    uploaded_file = st.file_uploader("Selecione a imagem da lesão cutânea...", type=["jpg", "jpeg", "png"])
    
    # Switch opcional para ativação do Processamento Digital de Imagens (PDI)
    ativar_pdi = st.checkbox("🔬 Ativar Realce Avançado de Microtexturas (PDI)", value=False)
    
    if uploaded_file is not None:
        # Cria uma pasta temporária para salvar o upload se não existir
        if not os.path.exists("temp"):
            os.makedirs("temp")
            
        caminho_imagem = os.path.join("temp", uploaded_file.name)
        with open(caminho_imagem, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Exibição das imagens na interface
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            st.image(caminho_imagem, caption="Foto enviada pelo usuário", use_container_width=True)
            
        with col_img2:
            if ativar_pdi:
                st.info("A Inteligência Artificial analisará a versão Realçada da imagem.")
                # Simulando a imagem de saída do PDI (Fusão Multi-Escala)
                # Na integração real, você chamaria sua função: caminho_imagem = aplicar_pdi(caminho_imagem)
                with st.expander("👁️ Ver Imagem Processada pelo PDI (Fusão Multi-Escala)"):
                    st.image(caminho_imagem, caption="Microtexturas realçadas ativamente para a IA", use_container_width=True)
            else:
                st.warning("O Filtro PDI está desativado. A IA analisará a imagem original.")

        # Botão para disparar o diagnóstico do Comitê
        if st.button("🚀 Processar Diagnóstico", type="primary"):
            with st.spinner("O Comitê de IA (ResNet50 + EfficientNet + DenseNet) está avaliando..."):
                
                # --- SIMULAÇÃO DA INFERÊNCIA DO ENSEMBLE ---
                # Na sua integração real, chame a função que carrega os modelos e faz o Soft Voting
                diagnostico_predito = "Dermatite"
                confianca_calculada = 89.8
                # -------------------------------------------
                
                # Salva o resultado no banco SQLite pegando o fuso horário brasileiro (UTC-3)
                data_registro = salvar_diagnostico(
                    nome_arquivo=uploaded_file.name,
                    nome_animal=nome_animal if nome_animal else "Ignorado",
                    especie=especie,
                    idade=idade,
                    nome_tutor=nome_tutor if nome_tutor else "Não Informado",
                    diagnostico=diagnostico_predito,
                    confianca=confianca_calculada
                )
                
                st.success("🎯 Triagem dermatológica executada com sucesso!")
                
                # Exibe Resultados na Tela
                col_res1, col_res2 = st.columns(2)
                with col_res1:
                    st.metric(label="Diagnóstico Identificado", value=diagnostico_predito)
                with col_res2:
                    st.metric(label="Confiança do Comitê", value=f"{confianca_calculada:.1f}%")

                st.markdown("---")
                st.subheader("📄 Emissão do Laudo Clínico")
                
                try:
                    # Gera o PDF usando o gerador fpdf2 corrigido que retorna bytes
                    pdf_bytes = gerar_laudo_pdf(
                        caminho_imagem=caminho_imagem,
                        nome_animal=nome_animal,
                        especie=especie,
                        idade=idade,
                        nome_tutor=nome_tutor,
                        diagnostico=diagnostico_predito,
                        confianca=confianca_calculada,
                        data_registro=data_registro
                    )
                    
                    # Botão de download do Streamlit que aceita o formato bytes
                    st.download_button(
                        label="⬇️ Baixar Laudo Clínico Oficial (PDF)",
                        data=pdf_bytes,
                        file_name=f"laudo_{nome_animal if nome_animal else 'animal'}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"⚠️ Não foi possível estruturar o laudo em PDF. Detalhes: {e}")

# 4. MÓDULO: HISTÓRICO CLÍNICO
elif menu == "Histórico Clínico":
    st.title("📂 Histórico de Triagens Salvas")
    
    # Carrega os dados salvos em formato de DataFrame do Pandas
    df_historico = carregar_historico()
    
    if df_historico.empty:
        st.info("Nenhum registro de diagnóstico encontrado no banco de dados.")
    else:
        # Se for administrador, ele vê tudo. Se for aluno, pode restringir ou apenas visualizar.
        if user["role"] == "admin":
            st.write("📊 **Modo Administrador:** Exibindo todos os prontuários e auditoria global do sistema.")
            st.dataframe(df_historico, use_container_width=True)
            
            # Recurso exclusivo de exportação para administradores
            csv = df_historico.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exportar Histórico Completo (CSV)",
                data=csv,
                file_name="historico_geral_vetai.csv",
                mime="text/csv"
            )
        else:
            st.write("📋 **Modo Aluno:** Visualizando o histórico completo de triagens do laboratório.")
            # Exibe o histórico removendo colunas mais críticas se necessário
            st.dataframe(df_historico, use_container_width=True)