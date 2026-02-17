🧠 Fase 1: Inteligência Financeira (O "Wow" Factor)

Dê ao cliente respostas para perguntas difíceis.

    [ ] Simulador de Amortização Extra ("E se eu der um lance?")

        O que é: Permitir que o usuário diga: "E se eu der R$ 5.000 a mais todo ano?".

        Impacto: Mostra como o prazo cai de 30 anos para 15 anos. Venda garantida.

        Técnica: Alterar o loop em core/calculos.py para abater do saldo devedor periodicamente.

    [ ] Comparador Lado a Lado (Batalha de Cenários)

        O que é: Um botão "Comparar" que coloca SAC e PRICE lado a lado na tela.

        Impacto: O cliente entende visualmente a diferença da parcela inicial vs. total de juros.

        Técnica: Criar uma view nova que chama a função de cálculo duas vezes e exibe em st.columns(2).

    [ ] Cálculo do C.E.T. (Custo Efetivo Total)

        O que é: Além dos juros, somar taxas e seguros para mostrar a taxa real anual.

        Impacto: Transparência e compliance bancário.

📱 Fase 2: Viralização e Comunicação

Facilite a vida do corretor para compartilhar os dados.

    [ ] Botão "Enviar no WhatsApp"

        O que é: Um botão que abre o WhatsApp Web já com um texto pronto: "Olá [Cliente], segue o resumo: Imóvel de R$ X, Parcela de R$ Y. Vamos agendar visita?"

        Técnica: Usar st.link_button com URL formatada (https://wa.me/?text=...).

    [ ] Exportar para Excel (Planilha Detalhada)

        O que é: Além do PDF (que é estático), permitir baixar o .xlsx da evolução da dívida.

        Impacto: Para clientes analíticos (engenheiros, contadores) que gostam de conferir conta.

🎨 Fase 3: UX Refinada (Experiência de Uso)

Deixar o uso mais fluido e evitar erros.

    [ ] Máscaras de Input (R$ Dinâmico)

        O que é: O usuário digita 350000 e o campo formata sozinho para R$ 350.000,00.

        Impacto: Evita erros de "um zero a mais ou a menos".

        Obs: O Streamlit nativo não faz isso bem, mas podemos usar formatação visual ou bibliotecas extras.

    [ ] Dashboard Interativo com Filtros de Data

        O que é: No Analytics, permitir escolher: "Últimos 7 dias", "Este Mês", "Este Ano".

        Técnica: Adicionar um st.date_input no views/dashboard.py que filtra o DataFrame.

🤖 Fase 4: O Futuro (IA Integration)

    [ ] Assistente de Análise de Crédito (IA Simples)

        O que é: Um texto gerado automaticamente: "Com base na renda de R$ 15k, este cliente tem perfil 'Ouro'. Sugira imóveis de até R$ 800k."

        Técnica: Regras condicionais avançadas (If/Else) ou conectar na API do Gemini para gerar o texto.


        # 🗺️ Mapa de Evolução do Sistema

## ✅ Feito
- [x] Estrutura de Pastas (MVC)
- [x] Calculadora de ITBI
- [x] Geração de PDF Premium (HTML/CSS)
- [x] Refatoração para Services (EM ANDAMENTO)

## 🔜 Próximos Passos (Prioridade)

### 1. 🏠 Calculadora "Aluguel vs. Compra" (Matador de Objeções)
- Criar nova View (`views/comparativo.py`).
- Inputs: Valor Aluguel, Rendimento CDI, Valorização Imóvel.
- Gráfico de Linhas cruzadas (Patrimônio Aluguel vs. Compra).
- Objetivo: Provar matematicamente que comprar é melhor a longo prazo.

### 2. 🚦 CRM Leve (Funil de Vendas)
- Alterar Banco de Dados: Adicionar coluna `status_lead`.
- Dashboard: Criar gráfico de Funil.
- Histórico: Permitir mudar status (Novo -> Visita -> Proposta -> Vendido).