from fpdf import FPDF
from datetime import datetime
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Proposta de Financiamento - Praia Grande/SP', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def gerar_proposta_pdf(dados):
    """
    Recebe um dicionário com os dados e gera o arquivo PDF.
    Retorna o nome do arquivo gerado.
    """
    pdf = PDF()
    pdf.add_page()
    
    # Bloco 1: Cabeçalho
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Cliente: {dados['cliente']}", ln=True)
    pdf.cell(0, 10, txt=f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(10)
    
    # Bloco 2: Valores
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Resumo Financeiro", ln=True)
    pdf.set_font("Arial", size=12)
    
    pdf.cell(0, 10, txt=f"Valor do Imóvel: R$ {dados['valor_imovel']:,.2f}", ln=True)
    pdf.cell(0, 10, txt=f"Entrada: R$ {dados['entrada']:,.2f}", ln=True)
    pdf.cell(0, 10, txt=f"Chaves: R$ {dados['chaves']:,.2f}", ln=True)
    pdf.cell(0, 10, txt=f"Intercaladas: R$ {dados['total_intercaladas']:,.2f}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt=f"Saldo Financiado: R$ {dados['saldo_devedor']:,.2f}", ln=True)
    pdf.cell(0, 10, txt=f"Mensais: {dados['meses']}x de R$ {dados['parcela']:,.2f}", ln=True)
    
    pdf.ln(10)
    # Bloco 3: Status
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, txt=f"Análise de Crédito: {dados['status_texto']}", ln=True)
    
    filename = f"proposta_{dados['cliente'].replace(' ', '_')}.pdf"
    pdf.output(filename)
    return filename