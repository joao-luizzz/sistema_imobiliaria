import streamlit as st
import os

def inject_custom_css():
    """Injeta o CSS global para deixar o app com cara de software premium"""
    st.markdown("""
    <style>
        /* Tipografia e Títulos */
        h1 { font-weight: 700; letter-spacing: -1px; font-size: 2rem; color: #f8fafc; }
        h2, h3 { font-weight: 600; color: #e2e8f0; }
        
        /* Tabela HTML Clean */
        .table-container { max-height: 400px; overflow-y: auto; border: 1px solid #334155; border-radius: 8px; margin-top: 10px; }
        .minimal-table { width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 0.85rem; color: #cbd5e1; background: transparent; }
        .minimal-table th { text-align: left; padding: 12px 16px; border-bottom: 2px solid #334155; color: #94a3b8; font-weight: 600; text-transform: uppercase; font-size: 0.7rem; position: sticky; top: 0; background-color: #0f172a; z-index: 10; }
        .minimal-table td { padding: 10px 16px; border-bottom: 1px solid #1e293b; }

        /* Cards KPI */
        .kpi-card {
            background: linear-gradient(145deg, #1e293b, #0f172a);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            height: 100%;
        }
        .kpi-card:hover { border-color: #3b82f6; transform: translateY(-5px); }
        .kpi-label { color: #94a3b8; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; display: block; margin-bottom: 5px; }
        .kpi-value { color: #f8fafc; font-size: 1.6rem; font-weight: 700; margin: 0; line-height: 1.2; }
        .kpi-sub { color: #64748b; font-size: 0.75rem; margin-top: 5px; display: block; }
    </style>
    """, unsafe_allow_html=True)

def card_html(label, valor, subtexto="", cor_destaque="#3b82f6"):
    """Gera o código HTML para um card de KPI"""
    return f"""
    <div class="kpi-card">
        <span class="kpi-label">{label}</span>
        <div class="kpi-value" style="color: {cor_destaque}">{valor}</div>
        <span class="kpi-sub">{subtexto}</span>
    </div>
    """

def renderizar_tabela_html(df):
    """Transforma o DataFrame em uma tabela HTML elegante"""
    df_fmt = df.copy()
    # Formata as colunas financeiras
    cols = ['Parcela', 'Amortização', 'Juros', 'Seguros/Taxas', 'Saldo Devedor']
    for col in cols:
        if col in df_fmt.columns:
            df_fmt[col] = df_fmt[col].apply(lambda x: f"R$ {x:,.2f}")
            
    return f'<div class="table-container">{df_fmt.to_html(classes="minimal-table", index=False, border=0)}</div>'