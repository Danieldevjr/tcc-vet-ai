import streamlit as st
import torch
from PIL import Image
import os
import tempfile

# Módulos da arquitetura Modular Clean Code do projeto
# (Certifique-se de que estes arquivos existem na sua pasta)
from database import inicializar_banco, salvar_diagnostico, carregar_historico
from pdf_generator import gerar_laudo_pdf
from vision_filters import medir_nitidez, verificar_dominio_biologico, aplicar_realce_pdi_avancado
from ai_model import carregar_modelo_ia, get_transformacao

# =====================================================================
# CONFIGURAÇÃO INICIAL E ESTILIZAÇÃO VISUAL
# =====================================================================
st.set_page_config(page_title="Vet.AI | PDI Opcional", page_icon="🐾", layout="wide")

# CSS personalizado para deixar a interface profissional e destacar o Checkbox
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; transition: 0.3s; }
        div[data-testid="metric-container"] { background-color: rgba(128, 128, 128, 0.1); border-radius: 10px; padding: 15px; border-left: 5px solid #14b8a6; }
        .aviso-alerta { color: #ff4b4b; font-weight: bold; padding: 15px; border: 2px solid #ff4b4b; border-radius: 8px; text-align: center; margin-bottom: 15px; background-color: rgba(255, 75, 75, 0.1); }
        /* Estilização para o contêiner do checkbox PDI */
        .div-pdi { margin-top: 10px; margin-bottom: 15px; padding: 15px; background-color: #f0f2f6; border-radius: 8px; border: 1px solid #d1d5db;}
    </style>
""", unsafe_allow_html=True)

# Inicialização Defensiva do Banco de Dados SQLite
try:
    inicializar_banco()
except Exception as e:
    st.error(f"⚠️ Erro crítico ao conectar ao banco de dados: {e}")

# Carregamento do modelo IA Ensemble em Cache para performance
@st.cache_resource
def iniciar_ia():
    return carregar_modelo_ia()

modelo, device, nomes_das_classes = iniciar_ia()
transformacao = get_transformacao()

# =====================================================================
# INTERFACE PRINCIPAL (STREAMLIT FRONT-END)
# =====================================================================
st.title("🐾 Vet.AI - Triagem Dermatológica Avançada")
st.markdown("Plataforma clínica modular com Prontuário Integrado, Tripla Defesa e **Realce PDI Opcional**.")
st.divider()

aba_diagnostico, aba_historico = st.tabs(["🩺 Realizar Diagnóstico", "📊 Analytics & Histórico"])

with aba_diagnostico:
    if modelo is None:
        st.error("❌ Erro: Arquivo de pesos 'modelo_vet_ensemble_V2_7Classes.pth' ausente no diretório raiz.")
    else:
        # SEÇÃO 1: PRONTUÁRIO CLÍNICO DO PACIENTE
        st.subheader("📋 Prontuário do Paciente")
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        
        with col_p1:
            nome_animal = st.text_input("Nome do Animal", placeholder="Ex: Thor").strip()
        with col_p2:
            especie = st.selectbox("Espécie", ["Cão", "Gato", "Outro"])
        with col_p3:
            idade = st.number_input("Idade (anos)", min_value=0, max_value=30, value=1, step=1)
        with col_p4:
            nome_tutor = st.text_input("Nome do Tutor(a)", placeholder="Ex: Maria Silva").strip()
            
        st.divider()

        # SEÇÃO 2: UPLOAD DA FOTO DA LESÃO
        imagem_upada = st.file_uploader("Faça upload da foto da lesão cutânea", type=["jpg", "jpeg", "png"])

        if imagem_upada is not None:
            col_img, col_res = st.columns([1, 1], gap="large")
            
            # Validação defensiva do arquivo de imagem
            try:
                imagem_original = Image.open(imagem_upada).convert('RGB')
                imagem_valida = True
            except Exception:
                st.error("❌ O arquivo enviado não é uma imagem válida ou está corrompido.")
                imagem_valida = False

            if imagem_valida:
                with col_img:
                    st.subheader("Imagem Original do Paciente")
                    with st.container(border=True):
                        st.image(imagem_original, use_container_width=True, caption="Foto enviada pelo usuário")

                with col_res:
                    st.subheader("Painel de Triagem")
                    
                    # --- CORREÇÃO AQUI: DEFINIÇÃO DO CHECKBOX ANTES DO BOTÃO ---
                    # Colocamos o controle PDI dentro de um contêiner visual estilizado
                    with st.container():
                        st.markdown('<div class="div-pdi">', unsafe_allow_html=True)
                        st.markdown("**⚙️ Pré-processamento Opcional**")
                        # A variável 'activar_realce' é definida AQUI
                        activar_realce = st.checkbox(
                            "🔬 Ativar Realce Avançado de Microtexturas (PDI)", 
                            value=False,
                            help="Recomendado para imagens levemente desfocadas. A IA analisará a versão realçada para maior precisão."
                        )
                        st.markdown('</div>', unsafe_allow_html=True)

                    # Botão principal de processamento
                    if st.button("🧠 Processar Diagnóstico", type="primary"):
                        # Validação obrigatória do prontuário
                        if not nome_animal or not nome_tutor:
                            st.warning("⚠️ Por favor, preencha o Nome do Animal e o Nome do Tutor antes de prosseguir.")
                        else:
                            with st.spinner("A validar integridade física e a processar IA..."):
                                
                                # --- CAMADA 1 DE DEFESA: FILTRO DE NITIDEZ ---
                                valor_nitidez = medir_nitidez(imagem_original)
                                if valor_nitidez < 100.0:
                                    st.markdown(f'''<div class="aviso-alerta">🚨 ANÁLISE BARRADA PELA CAMADA 1 (FOCO)<br>
                                        A foto está muito desfocada (Pontuação: {valor_nitidez:.1f}). Ajuste o foco e tente novamente.</div>''', unsafe_allow_html=True)
                                    st.stop()
                                    
                                # --- CAMADA 2 DE DEFESA: FILTRO COLORIMÉTRICO ---
                                percentagem_nao_biologica = verificar_dominio_biologico(imagem_original)
                                if percentagem_nao_biologica > 15.0:
                                    st.markdown(f'''<div class="aviso-alerta">🚨 ANÁLISE BARRADA PELA CAMADA 2 (DOMÍNIO)<br>
                                        Cenário externo detectado ({percentagem_nao_biologica:.1f}%). Aproxime a fotografia apenas na pele.</div>''', unsafe_allow_html=True)
                                    try:
                                        salvar_diagnostico(imagem_upada.name, nome_animal, especie, idade, nome_tutor, "Barrado (Cenário Externo)", 0.0)
                                    except Exception:
                                        pass
                                    st.stop()

                                # --- CAMADA 3 DE DEFESA: PDI OPCIONAL + IA ENSEMBLE ---
                                try:
                                    # LÓGICA DE DECISÃO: Agora 'activar_realce' está garantidamente definida
                                    if activar_realce:
                                        # Se marcado, aplica o pipeline PDI avançado (LAB+Multi-Scale Sharpening)
                                        imagem_para_ia = aplicar_realce_pdi_avancado(imagem_original)
                                        st.info("🔬 A Inteligência Artificial está analisando a versão **Realçada** da imagem.")
                                        
                                        # Define que a imagem nítida irá para o PDF
                                        imagem_laudo = imagem_para_ia
                                        
                                        # Exibe a imagem processada para transparência com o usuário
                                        with st.expander("🔬 Ver Imagem Processada pelo PDI (Fusão Multi-Escala)"):
                                            st.image(imagem_para_ia, use_container_width=True, caption="Microtexturas realçadas ativamente para a IA")
                                    else:
                                        # Se desmarcado, a IA analisa a original borrada
                                        imagem_para_ia = imagem_original
                                        st.warning("⚠️ A Inteligência Artificial está analisando a imagem **Original** (sem realce de PDI).")
                                        # Define que a imagem original irá para o PDF
                                        imagem_laudo = imagem_original

                                    # Prepara o tensor (tratado ou original) para o PyTorch
                                    img_tensor = transformacao(imagem_para_ia).unsqueeze(0).to(device)
                                    
                                    with torch.no_grad():
                                        saidas = modelo(img_tensor)
                                        probabilidades = torch.nn.functional.softmax(saidas[0], dim=0)
                                        confianca, predicao = torch.max(probabilidades, 0)
                                    
                                    diag = nomes_das_classes[predicao.item()]
                                    conf = confianca.item() * 100
                                    processamento_ia_ok = True
                                except Exception as e:
                                    st.error(f"❌ Erro interno durante a inferência da Inteligência Artificial: {e}")
                                    processamento_ia_ok = False

                                # Validação da barreira estatística de confiança
                                if processamento_ia_ok:
                                    LIMIAR_CONFIANCA_IA = 75.0
                                    
                                    if diag == 'INCONCLUSIVO' or conf < LIMIAR_CONFIANCA_IA:
                                        st.markdown(f'''<div class="aviso-alerta">🚨 ANÁLISE BARRADA PELA CAMADA 3 (IA)<br>
                                            Incerteza elevada ({conf:.1f}%) ou ruído identificado. Recomendamos encaminhar ao especialista.</div>''', unsafe_allow_html=True)
                                        try:
                                            salvar_diagnostico(imagem_upada.name, nome_animal, especie, idade, nome_tutor, "Barrado (Incerteza/Objeto)", conf)
                                        except Exception:
                                            pass
                                    else:
                                        # TUDO APROVADO: Salva no banco e gera PDF
                                        try:
                                            data_registro = salvar_diagnostico(imagem_upada.name, nome_animal, especie, idade, nome_tutor, diag, conf)
                                            st.success("✅ Triagem dermatológica executada com sucesso!")
                                            
                                            m1, m2 = st.columns(2)
                                            m1.metric("Diagnóstico Identificado", diag)
                                            m2.metric("Confiança do Comitê", f"{conf:.1f}%")
                                            st.progress(int(conf))
                                            
                                            # Geração Segura do PDF Hospitalar
                                            try:
                                                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img_laudo:
                                                    # Salva no laudo a imagem que a IA analisou (realçada ou original)
                                                    imagem_laudo.save(tmp_img_laudo.name)
                                                    caminho_laudo = tmp_img_laudo.name
                                                    
                                                pdf_bytes = gerar_laudo_pdf(caminho_laudo, nome_animal, especie, idade, nome_tutor, diag, conf, data_registro)
                                                
                                                st.download_button(
                                                    label="📄 Emitir Laudo Hospitalar (PDF)", 
                                                    data=pdf_bytes, 
                                                    file_name=f"Laudo_VetAI_{nome_animal}_{data_registro[:10].replace('/','')}.pdf", 
                                                    mime="application/pdf"
                                                )
                                                # Deleta arquivo temporário após geração do PDF
                                                os.unlink(caminho_laudo)
                                            except Exception as e_pdf:
                                                st.error(f"⚠️ Não foi possível estruturar o laudo em PDF. Detalhes: {e_pdf}")
                                                
                                        except Exception as e_db:
                                            st.error(f"⚠️ Triagem concluída, mas falhou ao gravar no histórico: {e_db}")

with aba_historico:
    st.subheader("📊 Painel de Analytics & Prontuários Médicos")
    try:
        df = carregar_historico()
        if not df.empty:
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1: 
                st.bar_chart(df['diagnostico'].value_counts(), color="#14b8a6")
            with col_chart2: 
                st.bar_chart(df.groupby('diagnostico')['confianca'].mean(), color="#8b5cf6")
            st.divider()
            
            # Mapeamento das 9 colunas do prontuário do SQLite
            df.columns = ["ID", "Data/Hora", "Nome Arquivo", "Paciente (Nome)", "Espécie", "Idade (Anos)", "Tutor(a)", "Diagnóstico", "Confiança (%)"]
            st.dataframe(df, use_container_width=True, hide_index=True, height=350)
        else:
            st.info("Nenhum registro clínico encontrado até o momento.")
    except Exception as e_hist:
        st.error(f"Erro ao carregar o histórico do SQLite: {e_hist}")