from fpdf import FPDF
from datetime import datetime, timezone, timedelta

def gerar_laudo_pdf(caminho_imagem, nome_animal, especie, idade, nome_tutor, diagnostico, confianca, data_registro=None):
    # Configura o fuso horário oficial do Brasil (UTC-3)
    fuso_br = timezone(timedelta(hours=-3))
    
    # Se a data/hora não for informada pelo banco, gera a hora atual do Brasil
    if not data_registro:
        data_registro = datetime.now(fuso_br).strftime("%d/%m/%Y %H:%M:%S")

    # Inicializa o documento PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    
    # Cabeçalho da Clínica / Hospital
    pdf.set_font("Helvetica", style="B", size=18)
    pdf.cell(0, 10, txt="Hospital Veterinario - Vet.AI", ln=True, align="C")
    
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, txt="Laudo de Triagem Dermatologica Avancada", ln=True, align="C")
    pdf.ln(10)
    
    # Dados do Prontuário do Paciente
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, txt="Prontuario do Paciente", ln=True)
    
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 8, txt=f"Data e Hora da Triagem: {data_registro}", ln=True)
    pdf.cell(0, 8, txt=f"Tutor(a): {nome_tutor}", ln=True)
    pdf.cell(0, 8, txt=f"Paciente: {nome_animal}", ln=True)
    pdf.cell(0, 8, txt=f"Especie: {especie}", ln=True)
    pdf.cell(0, 8, txt=f"Idade: {idade} anos", ln=True)
    pdf.ln(10)
    
    # Resultados do Comitê de IA
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, txt="Resultado da Analise (Comite de IA)", ln=True)
    
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 8, txt=f"Diagnostico Preditivo: {diagnostico}", ln=True)
    pdf.cell(0, 8, txt=f"Nivel de Confianca: {confianca:.1f}%", ln=True)
    pdf.ln(10)
    
    # Inserção da Imagem Analisada
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, txt="Registro Fotografico Analisado:", ln=True)
    pdf.ln(5)
    
    try:
        pdf.image(caminho_imagem, x=20, w=170)
    except Exception as e:
        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 10, txt=f"[Erro ao carregar a imagem no documento: {e}]", ln=True)
        
    pdf.ln(20)
    
    # Rodapé Informativo
    pdf.set_font("Helvetica", style="I", size=10)
    aviso = "Aviso: Este laudo e um documento de triagem emitido por Inteligencia Artificial e nao substitui a avaliacao clinica presencial de um Medico Veterinario."
    pdf.multi_cell(0, 5, txt=aviso)
    
    # Retorna o arquivo formatado em bytes
    return bytes(pdf.output())