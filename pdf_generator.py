from fpdf import FPDF

def gerar_laudo_pdf(imagem_path, nome_animal, especie, idade, nome_tutor, diagnostico, confianca, data_hora):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho do Sistema
    pdf.set_font("helvetica", 'B', 16)
    pdf.set_text_color(20, 184, 166)
    pdf.cell(0, 10, "VET.AI - LAUDO DE TRIAGEM DERMATOLOGICA", ln=True, align='C')
    pdf.set_font("helvetica", 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, "Relatorio Preditivo Multimodelo (Ensemble Learning)", ln=True, align='C')
    pdf.ln(10)
    
    # Seção 1: Dados do Prontuário Clínico
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "1. IDENTIFICACAO DO PACIENTE E TUTOR", ln=True)
    pdf.set_font("helvetica", '', 11)
    pdf.cell(0, 6, f"Nome do Animal: {nome_animal}", ln=True)
    pdf.cell(0, 6, f"Especie: {especie}", ln=True)
    pdf.cell(0, 6, f"Idade: {idade} ano(s)", ln=True)
    pdf.cell(0, 6, f"Tutor(a): {nome_tutor}", ln=True)
    pdf.cell(0, 6, f"Data e Hora da Triagem: {data_hora}", ln=True)
    pdf.ln(5)
    
    # Seção 2: Registro Fotográfico
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "2. REGISTRO FOTOGRAFICO DA LESAO", ln=True)
    pdf.image(imagem_path, x=10, y=pdf.get_y(), w=90) 
    pdf.ln(100) # Espaço para a imagem não sobrepor o texto
    
    # Seção 3: Resultado da IA
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "3. ANALISE E DIAGNOSTICO PREDITIVO", ln=True)
    pdf.set_font("helvetica", '', 11)
    pdf.cell(0, 6, f"Arquitetura: Comite Ensemble (ResNet50 + EffNet-B0 + DenseNet121)", ln=True)
    pdf.cell(0, 6, f"Patologia Preditada: {diagnostico}", ln=True)
    pdf.cell(0, 6, f"Grau de Confianca do Comite: {confianca:.2f}%", ln=True)
    
    # Rodapé Legal
    pdf.ln(15)
    pdf.set_font("helvetica", 'I', 9)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(0, 5, "AVISO LEGAL: Este laudo foi gerado de forma automatizada por Inteligencia Artificial como suporte clinico. Nao substitui de forma alguma a avaliacao presencial conduzida por um Medico Veterinario.")
    
    return bytes(pdf.output())