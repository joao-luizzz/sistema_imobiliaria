import plotly.graph_objects as go
import pandas as pd

# Configuração padrão para TODOS os gráficos (Tema Dark/Clean)
LAYOUT_PADRAO = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Inter, sans-serif", color="#94a3b8"),
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis=dict(showgrid=False, zeroline=False, color='#64748b'),
    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False, color='#64748b'),
    hovermode="x unified"
)

def grafico_evolucao_parcelas(df):
    fig = go.Figure()
    
    # Efeito degradê na linha
    fig.add_trace(go.Scatter(
        x=df['Mês'], 
        y=df['Parcela'], 
        mode='lines', 
        name='Parcela',
        line=dict(color='#3b82f6', width=4, shape='spline'), # Spline deixa a curva suave
        fill='tozeroy', 
        fillcolor='rgba(59, 130, 246, 0.1)'
    ))

    fig.update_layout(**LAYOUT_PADRAO, height=350)
    fig.update_yaxes(tickprefix="R$ ")
    return fig

def grafico_pizza_status(df):
    df_status = df['status'].value_counts().reset_index()
    
    cores = {'APROVADO': '#10b981', 'ATENÇÃO': '#f59e0b', 'REPROVADO': '#ef4444'}
    
    fig = go.Figure(data=[go.Pie(
        labels=df_status['status'], 
        values=df_status['count'], 
        hole=.7, # Buraco maior = mais moderno
        marker=dict(colors=[cores.get(s, '#334155') for s in df_status['status']]),
        textinfo='percent',
        hoverinfo='label+value'
    )])
    
    fig.update_layout(
        height=300, 
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", y=-0.1, font=dict(color='#94a3b8'))
    )
    return fig

def grafico_timeline_simulacoes(df):
    """Gera o gráfico de Barras da linha de tempo de atendimentos"""
    
    # 1. Agrupa por dia
    if 'data_criacao' in df.columns:
        df['data'] = pd.to_datetime(df['data_criacao']).dt.date
    else:
        # Fallback caso a coluna não exista (segurança)
        return go.Figure()

    df_timeline = df.groupby('data').size().reset_index(name='quantidade')
    
    # 2. Cria o Gráfico de Barras (Mais bonito para volumes diários)
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_timeline['data'], 
        y=df_timeline['quantidade'],
        name='Simulações',
        marker_color='#3b82f6', # Azul da marca
        opacity=0.9,
        hovertemplate='<b>Dia %{x|%d/%m}</b><br>%{y} Simulações<extra></extra>',
        showlegend=False
    ))
    
    # 3. Configuração Visual (Remove grades e força formatação de data)
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.05)', # Grade bem sutil
            color='#64748b',
            zeroline=False,
            dtick=1 # Garante que o eixo Y mostre apenas números inteiros (1, 2, 3...) e não 1.5
        ),
        xaxis=dict(
            showgrid=False, 
            color='#64748b',
            tickformat="%d/%m", # <--- O SEGREDO: Força mostrar dia/mês
            type='category' # Trata as datas como categorias para não criar buracos vazios
        )
    )
    return fig