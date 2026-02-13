# 🚀 Roadmap do Sistema Imobiliário

## ✅ Fase 1: Realismo Financeiro (Feito)
- [x] Adicionar input de 'Taxa Adm/Seguro' no app.py
- [x] Atualizar função projetar_amortizacao em calculos.py para incluir tarifa

## ✅ Fase 2: O Oráculo (Feito)
- [x] Criar função calcular_poder_compra em calculos.py
- [x] Implementar seletor de 'Modo de Operação' no app.py
- [x] Criar layout e cards específicos para o modo Oráculo

## ✅ Fase 3: Visual Premium (Feito)
- [x] Atualizar CSS com classes .kpi-card e .oracle-card
- [x] Substituir st.metric por cards HTML personalizados

## 🚧 Fase 4: Persistência de Dados (Próximo Passo)
- [ ] Escolher banco de dados: Supabase (PostgreSQL)
- [ ] Criar conta no Supabase e pegar credenciais (URL)
- [ ] Configurar .streamlit/secrets.toml com as senhas
- [ ] Criar tabela 'simulacoes' no banco
- [ ] Atualizar database.py para salvar na nuvem em vez de SQLite

## 🚀 Geral / Deploy
- [ ] Atualizar requirements.txt (adicionar plotly, psycopg2-binary, etc.)
- [ ] Testar aplicação completa localmente
- [ ] Fazer commit e push final
- [ ] Verificar deploy no Streamlit Cloud