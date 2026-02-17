from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader
import pandas as pd
import io
import os
from datetime import datetime

# --- CONFIGURAÇÃO PARA IMAGENS NO PDF ---
def link_callback(uri, rel):
    """
    Converte caminhos relativos de HTML (assets/img/logo.png)
    para caminhos absolutos do sistema (/home/joao/projeto/assets/img/logo.png)
    """
    # Se for caminho absoluto, não mexe
    if uri.startswith("http") or os.path.isabs(uri):
        return uri
        
    # Caminho absoluto da pasta do projeto
    base_dir = os.getcwd()
    
    # Monta o caminho completo
    path = os.path.join(base_dir, uri)
    
    if not os.path.isfile(path):
        print(f"⚠️ Aviso: Imagem não encontrada no caminho: {path}")
        return uri
        
    return path

def render_html(template_name, context):
    template_dir = os.path.join(os.getcwd(), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    return template.render(context)

def formatar_moeda(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return valor

def gerar_proposta_pdf(dados):
    # Prepara dados
    dados_formatados = dados.copy()
    dados_formatados['data_hoje'] = datetime.now().strftime('%d/%m/%Y')
    
    campos_moeda = ['valor_imovel', 'entrada', 'saldo_devedor', 'parcela', 'custo_doc', 'total_necessario']
    for campo in campos_moeda:
        if campo in dados_formatados:
            dados_formatados[campo] = formatar_moeda(dados_formatados[campo])

    # Gera HTML
    try:
        source_html = render_html('proposta.html', dados_formatados)
    except Exception as e:
        print(f"Erro Template: {e}")
        return None

    # Gera PDF
    output_filename = f"proposta_{dados['cliente'].replace(' ', '_')}.pdf"
    
    with open(output_filename, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(
            source_html,
            dest=result_file,
            link_callback=link_callback  # <--- O SEGREDO ESTÁ AQUI
        )

    if pisa_status.err:
        return None
        
    return output_filename

def gerar_excel_comparativo(df_sac, df_price, dados_cliente):
    # (Mantém igual ao anterior)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        resumo = pd.DataFrame({
            'Cliente': [dados_cliente['cliente']],
            'Valor Imóvel': [dados_cliente['valor_imovel']],
            'Entrada': [dados_cliente['entrada']],
            'Prazo (meses)': [dados_cliente['meses']]
        })
        resumo.to_excel(writer, sheet_name='Resumo', index=False)
        df_sac.to_excel(writer, sheet_name='Tabela SAC', index=False)
        df_price.to_excel(writer, sheet_name='Tabela PRICE', index=False)
    output.seek(0)
    return output