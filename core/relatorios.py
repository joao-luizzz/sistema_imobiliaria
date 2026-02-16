from fpdf import FPDF
from datetime import datetime
import os
import io               
import pandas as pd    

class PDF(FPDF):
    def header(self):
        # Tenta carregar a logo se existir na pasta assets
        if os.path.exists("assets/logo.png"):
            self.image("assets/logo.png", 10, 8, 33)
            self.set_font('Arial', 'B', 14)
            self.cell(40) 
            self.cell(0, 10, 'Proposta de Financiamento', 0, 1, 'C')
        else:
            self.set_font('Arial', 'B', 14)
            self.cell(0, 10, 'Proposta de Financiamento', 0, 1, 'C')
            
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Sistema Imobiliario Premium | Pagina {self.page_no()}', 0, 0, 'C')

def tratar_texto(texto):
    """Remove caracteres incompatíveis com Latin-1"""
    if isinstance(texto, str):
        return texto.encode('latin-1', 'replace').decode('latin-1')
    return str(texto)

def gerar_proposta_pdf(dados):
    """
    Gera o PDF e retorna o caminho do arquivo.
    """
    pdf = PDF()
    pdf.add_page()
    
    # Bloco 1: Cabeçalho do Cliente
    pdf.set_font("Arial", size=12)
    pdf.set_fill_color(240, 240, 240)
    
    nome_cliente = tratar_texto(dados['cliente'])
    
    pdf.cell(0, 10, txt=f"  Cliente: {nome_cliente}", ln=True, fill=True)
    pdf.cell(0, 10, txt=f"  Data da Simulacao: {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(5)
    
    # Bloco 2: Resumo Financeiro
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Resumo do Imovel", ln=True)
    pdf.set_font("Arial", size=12)
    
    pdf.cell(50, 10, "Valor do Imovel:", 0)
    pdf.cell(0, 10, f"R$ {dados['valor_imovel']:,.2f}", 1, 1)
    
    pdf.cell(50, 10, "Entrada:", 0)
    pdf.cell(0, 10, f"R$ {dados['entrada']:,.2f}", 1, 1)
    
    pdf.ln(5)
    
    # Bloco 3: Condições de Pagamento
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "  Plano de Pagamento Sugerido", 0, 1, 'L', fill=True)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(50, 10, "Saldo Financiado:", 0)
    pdf.cell(0, 10, f"R$ {dados['saldo_devedor']:,.2f}", 0, 1)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(50, 10, "1a Parcela:", 0)
    pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 10, f"R$ {dados['parcela']:,.2f}", 0, 1)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(50, 10, "Prazo:", 0)
    pdf.cell(0, 10, f"{dados['meses']} meses", 0, 1)

    pdf.ln(10)
    
    # Bloco 4: Parecer
    pdf.set_draw_color(200, 200, 200)
    pdf.rect(10, pdf.get_y(), 190, 20)
    pdf.set_xy(12, pdf.get_y() + 2)
    pdf.set_font("Arial", 'I', 10)
    
    texto_parecer = tratar_texto(dados['status_texto'])
    pdf.multi_cell(0, 5, txt=f"Parecer do Sistema:\n{texto_parecer}")
    
    safe_filename = f"proposta_{dados['cliente'].replace(' ', '_')}.pdf"
    safe_filename = safe_filename.encode('ascii', 'ignore').decode('ascii')
    
    pdf.output(safe_filename)
    return safe_filename

def gerar_excel_comparativo(df_sac, df_price, dados_cliente):
    """
    Gera um arquivo Excel com duas abas (SAC e PRICE) na memória RAM.
    Não salva no disco, retorna o objeto pronto para download.
    """
    output = io.BytesIO()
    
    # Cria o "Escritor" de Excel usando a engine openpyxl
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Aba 1: Resumo
        resumo = pd.DataFrame({
            'Cliente': [dados_cliente['cliente']],
            'Valor Imóvel': [dados_cliente['valor_imovel']],
            'Entrada': [dados_cliente['entrada']],
            'Prazo (meses)': [dados_cliente['meses']]
        })
        resumo.to_excel(writer, sheet_name='Resumo', index=False)
        
        # Aba 2 e 3: Tabelas completas
        df_sac.to_excel(writer, sheet_name='Tabela SAC', index=False)
        df_price.to_excel(writer, sheet_name='Tabela PRICE', index=False)
        
    output.seek(0)
    return output