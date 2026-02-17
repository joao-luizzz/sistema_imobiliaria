import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ==========================================
# 🏠 GRÁFICOS DA SIMULAÇÃO (View Simulacao)
# ==========================================

def plot_amortizacao(df):
    """
    Gera um gráfico de área empilhada mostrando a composição da parcela
    (Amortização vs Juros) ao longo dos meses.
    """
    fig = go.Figure()

    # Camada de Amortização (Verde)
    fig.add_trace(go.Scatter(
        x=df['Mes'],
        y=df['Amortizacao'],
        mode='lines',
        name='Amortização (Abate Dívida)',
        stackgroup='one',
        line=dict(width=0, color='#10b981'), # Verde
        fillcolor='rgba(16, 185, 129, 0.6)'
    ))

    # Camada de Juros (Vermelho)
    fig.add_trace(go.Scatter(
        x=df['Mes'],
        y=df['Juros'],
        mode='lines',
        name='Juros (Custo)',
        stackgroup='one',
        line=dict(width=0, color='#ef4444'), # Vermelho
        fillcolor='rgba(239, 68, 68, 0.6)'
    ))

    fig.update_layout(
        title="Composição da Parcela ao Longo do Tempo",
        xaxis_title="Meses",
        yaxis_title="Valor (R$)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=60, b=20),
        height=400
    )
    return fig

def plot_composicao(saldo_devedor, total_juros):
    """
    Gera um gráfico de Rosca (Donut) comparando o valor original vs juros.
    """
    labels = ['Valor Financiado', 'Total em Juros']
    values = [saldo_devedor, total_juros]
    colors = ['#3b82f6', '#f59e0b'] # Azul e Laranja

    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        hole=.5,
        marker=dict(colors=colors)
    )])

    fig.update_layout(
        title="Custo Total do Financiamento",
        annotations=[dict(text='Total', x=0.5, y=0.5, font_size=20, showarrow=False)],
        margin=dict(l=20, r=20, t=60, b=20),
        height=300
    )
    return fig

# ==========================================
# 📊 GRÁFICOS DO DASHBOARD (View Dashboard)
# ==========================================

def grafico_timeline_simulacoes(df):
    """
    Mostra a evolução das simulações ao longo do tempo.
    """
    if df.empty:
        return go.Figure()

    if 'data_criacao' in df.columns:
        # Garante datetime
        df['data_criacao'] = pd.to_datetime(df['data_criacao'])
        
        # Agrupa por dia
        contagem = df.groupby(df['data_criacao'].dt.date).size().reset_index(name='Quantidade')
        contagem.columns = ['Data', 'Quantidade']
        
        fig = px.bar(
            contagem, 
            x='Data', 
            y='Quantidade', 
            title="Evolução de Simulações por Dia",
            color_discrete_sequence=['#3b82f6']
        )
        
        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="Volume",
            height=350,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        return fig
    else:
        return go.Figure()

def grafico_pizza_status(df): # <--- NOME CORRIGIDO AQUI
    """
    Mostra a distribuição dos status (Pizza).
    """
    if df.empty or 'status' not in df.columns:
        return go.Figure()
        
    contagem = df['status'].value_counts().reset_index()
    contagem.columns = ['Status', 'Quantidade']
    
    fig = px.pie(
        contagem, 
        names='Status', 
        values='Quantidade', 
        title="Distribuição de Status",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig