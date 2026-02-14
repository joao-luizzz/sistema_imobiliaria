import plotly.graph_objects as go
import pandas as pd

def grafico_evolucao_parcelas(df):
    """Gera o gráfico de linha/área para a evolução das parcelas"""
    fig = go.Figure()
    
    # Linha da Parcela
    fig.add_trace(go.Scatter(
        x=df['Mês'], 
        y=df['Parcela'], 
        mode='lines', 
        name='Parcela',
        line=dict(color='#3b82f6', width=3),
        fill='tozeroy', 
        fillcolor='rgba(59, 130, 246, 0.1)',
        hovertemplate='<b>Mês %{x}</b><br>Total: R$ %{y:,.2f}<extra></extra>'
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0),
        height=350,
        hovermode="x unified",
        xaxis=dict(showgrid=False, color='#64748b'),
        yaxis=dict(showgrid=True, gridcolor='#1e293b', color='#64748b', tickprefix="R$ ")
    )
    return fig

def grafico_pizza_status(df):
    """Gera o gráfico de rosca para o Dashboard de status"""
    df_status = df['status'].value_counts().reset_index()
    
    # Mapeamento de cores fixas
    cores = {
        'APROVADO': '#10b981',
        'ATENÇÃO': '#f59e0b',
        'REPROVADO': '#ef4444'
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=df_status['status'], 
        values=df_status['count'], 
        hole=.6,
        marker=dict(colors=[cores.get(s, '#334155') for s in df_status['status']])
    )])
    
    fig.update_layout(
        height=300, 
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color='#94a3b8'))
    )
    return fig

def grafico_timeline_simulacoes(df):
    """Gera o gráfico de linha de tempo de atendimentos"""
    # Garante que a data está em formato datetime
    df['data'] = pd.to_datetime(df['data_criacao']).dt.date
    df_timeline = df.groupby('data').size().reset_index(name='quantidade')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_timeline['data'], 
        y=df_timeline['quantidade'],
        mode='lines+markers',
        line=dict(color='#3b82f6', width=3),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.05)'
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, color='#64748b'),
        yaxis=dict(showgrid=True, gridcolor='#1e293b', color='#64748b')
    )
    return fig