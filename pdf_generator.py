from fpdf import FPDF
import datetime

def gerar_laudo_pdf(caminho_imagem, nome_animal, especie, idade, nome_tutor, diagnostico, confianca, data_registro):
    # Inicializa o PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Configura a margem e a fonte padrão (usando fontes nativas que não exigem ficheiros externos)
    pdf.set_margins(20, 20, 20)
    
    # Cabeçalho do Hospital / Clínica
    pdf.set_font("Helvetica", style="B", size=18)
    pdf.cell(0, 10, txt="Hospital Veterinário - Vet.AI", ln=True, align="C")
    
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, txt="Laudo de Triagem Dermatológica Avançada", ln=True, align="C")
    pdf.ln(10)
    
    # Dados do Prontuário
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, txt="Prontuário do Paciente", ln=True)
    
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 8, txt=f"Data da Triagem: {data_registro}", ln=True)
    pdf.cell(0, 8, txt=f"Tutor(a): {nome_tutor}", ln=True)
    pdf.cell(0, 8, txt=f"Paciente: {nome_animal}", ln=True)
    pdf.cell(0, 8, txt=f"Espécie: {especie}", ln=True)
    pdf.cell(0, 8, txt=f"Idade: {idade} anos", ln=True)
    pdf.ln(10)
    
    # Resultados da Inteligência Artificial
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, txt="Resultado da Análise (Comitê de IA)", ln=True)
    
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 8, txt=f"Diagnóstico Preditivo: {diagnostico}", ln=True)
    pdf.cell(0, 8, txt=f"Nível de Confiança: {confianca:.1f}%", ln=True)
    pdf.ln(10)
    
    # Inserir Imagem (Realçada ou Original)
    pdf.set_font("Helvetica", style="B", size=14)
    pdf.cell(0, 10, txt="Registo Fotográfico Analisado:", ln=True)
    pdf.ln(5)
    
    try:
        # A biblioteca fpdf2 lida melhor com as imagens
        pdf.image(caminho_imagem, x=20, w=170)
    except Exception as e:
        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 10, txt=f"[Erro ao carregar a imagem no documento: {e}]", ln=True)
        
    pdf.ln(20)
    
    # Rodapé Legal
    pdf.set_font("Helvetica", style="I", size=10)
    aviso = "Aviso: Este laudo é um documento de triagem emitido por Inteligência Artificial (Projeto TADS) e não substitui a avaliação clínica presencial de um Médico Veterinário."
    pdf.multi_cell(0, 5, txt=aviso)
    
    # Retorna o ficheiro em formato de bytes para o Streamlit processar o download
    return bytes(pdf.output())