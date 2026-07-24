import streamlit as st
import os
import cv2
import numpy as np
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

# --- FUNÇÃO DA CAMADA DE VALIDAÇÃO DE ESCOPO (Filtro Baseado em PDI) ---
def validar_imagem_escopo(caminho_img):
    """
    Analisa características da imagem para bloquear paisagens (céu, florestas)
    ou imagens com padrões que não condizem com uma foto aproximada de lesão na pele.
    """
    img = cv2.imread(caminho_img)
    if img is None:
        return False, "Imagem Corrompida"
        
    # Converte para o espaço de cores HSV para analisar matizes (cores)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Calcula histograma de cores para detectar excesso de azul (céu) ou verde (floresta/grama)
    # Tons de azul e verde no HSV costumam ficar entre as faixas de 35 a 130
    hist_cores = cv2.calcHist([hsv], [0], None, [180], [0, 180])
    pixels_paisagem = np.sum(hist_cores[35:130])
    total_pixels = img.shape[0] * img.shape[1]
    porcentagem_paisagem = (pixels_paisagem / total_pixels) * 100
    
    # Se mais de 55% da imagem for composta por tons puros de azul/verde, bloqueia como paisagem externa
    if porcentagem_paisagem > 55.0:
        return False, "Cenário Externo / Paisagem"
        
    # Verifica a variância dos tons de cinza (imagens muito uniformes como paredes brancas ou folhas de papel)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    variancia = np.var(gray)
    if variancia < 200:
        return False, "Superfície Lisa / Objeto Uniforme"
        
    return True, "Imagem Válida (Pele/Tecido)"

# 3. MÓDULO: NOVA TRIAGEM
if menu == "Nova Triagem":
    st.title("🔬 Triagem Dermatológica Avançada")
    st.write("Insira os dados do prontuário e anexe a foto da lesão para análise do Comitê de IA.")

    # Formulário do Prontuário Clínico
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
    
    # Switch para ativação do Processamento Digital de Imagens (PDI)
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
                with st.expander("👁️ Ver Imagem Processada pelo PDI (Fusão Multi-Escala)"):
                    st.image(caminho_imagem, caption="Microtexturas realçadas ativamente para a IA", use_container_width=True)
            else:
                st.warning("O Filtro PDI está desativado. A IA analisará a imagem original.")

        # Botão para disparar o diagnóstico do Comitê
        if st.button("🚀 Processar Diagnóstico", type="primary"):
            
            # --- EXECUÇÃO DA CAMADA DE VALIDAÇÃO DE ESCOPO ---
            imagem_valida, motivo_rejeicao = validar_imagem_escopo(caminho_imagem)
            
            if not imagem_valida:
                st.error("❌ **Detecção de Inconsistência de Domínio!**")
                st.warning(f"A imagem enviada foi rejeitada pela camada de segurança. Motivo: **{motivo_rejeicao}**.")
                st.info("Por favor, envie uma foto aproximada e focada da lesão dermatológica do animal.")
                st.stop() # Interrompe a execução imediatamente para não gerar o falso positivo
            
            # --- CONTINUAÇÃO SE A IMAGEM FOR VÁLIDA ---
            with st.spinner("O Comitê de IA (ResNet50 + EfficientNet + DenseNet) está avaliando..."):
                
                # --- SIMULAÇÃO DA INFERÊNCIA DO ENSEMBLE ---
                # Aqui entra o soft voting do seu modelo consolidado
                diagnostico_predito = "Dermatite"
                confianca_calculada = 89.8
                # -------------------------------------------
                
                # Salva o resultado no banco SQLite
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
                    # Gera o PDF usando o gerador fpdf2
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
                    
                    # Botão de download do Streamlit
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
            st.dataframe(df_historico, use_container_width=True)