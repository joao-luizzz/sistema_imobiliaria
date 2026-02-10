from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Simulacao Imobiliaria', 0, 1, 'C')
        self.ln(5)

def gerar_proposta_pdf(dados):
    pdf = PDF()
    pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Cliente: {dados['cliente']}", ln=True)
    pdf.cell(0, 10, txt=f"Imovel: R$ {dados['valor_imovel']:,.2f}", ln=True)
    pdf.cell(0, 10, txt=f"Parcela: R$ {dados['parcela']:,.2f}", ln=True)
    pdf.cell(0, 10, txt=f"Status: {dados['status_texto']}", ln=True)
    filename = "proposta.pdf"
    pdf.output(filename)
    return filename
