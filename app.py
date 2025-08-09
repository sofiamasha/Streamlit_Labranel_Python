# Projeto: "Labranel - Showcode"
# App Streamlit impressionante: mostra código, roda consultas SQL, visualiza dados animados.
# Arquivo único. Execute: pip install streamlit pandas sqlalchemy plotly

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import sqlite3
import inspect
import textwrap
import io

st.set_page_config(page_title="Labranel — Showcode", layout="wide")

st.markdown("""
<style>
body {background: radial-gradient(circle at 10% 10%, #0f172a, #020617); color: #e6eef8}
.header {font-size:28px; font-weight:700; color:#ffd6e0}
.card {background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)); padding:18px; border-radius:12px;}
.small {color:#bcd4ff}
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="header">Labranel — Showcode: visualização, SQL interativo e preview do código</div>', unsafe_allow_html=True)
st.write('Um projeto single-file em Python (Streamlit) para impressionar seguidores e professores.\nEscolha uma aba para explorar:')


def build_sample_db(conn):
    df_products = pd.DataFrame([
        (1, 'Creme Hidratante', 'Skincare'),
        (2, 'Shampoo Nutritivo', 'Hair'),
        (3, 'Sérum Vit C', 'Skincare'),
        (4, 'Máscara Capilar', 'Hair'),
        (5, 'Sabonete Líquido', 'Body')
    ], columns=['product_id','product','category'])

    rows=[]
    import random
    months = pd.date_range('2024-01-01', periods=12, freq='M')
    regions = ['Norte','Nordeste','Sudeste','Sul','Centro-Oeste']
    for m in months:
        for p in df_products['product_id']:
            for r in regions:
                qty = max(0, int(random.gauss(200,80)))
                price = round(random.uniform(10,80),2)
                rows.append((m.strftime('%Y-%m'), p, r, qty, price))
    df_sales = pd.DataFrame(rows, columns=['month','product_id','region','qty','price'])

    df_products.to_sql('products', conn, if_exists='replace', index=False)
    df_sales.to_sql('sales', conn, if_exists='replace', index=False)

conn = sqlite3.connect(':memory:')
build_sample_db(conn)
engine = create_engine('sqlite://', creator=lambda: conn)

pages = st.tabs(["Dashboard", "SQL Interativo", "Preview do Código", "Export & Share"])
with pages[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader('Vendas por Categoria — Sunburst interativo')
        q = """
        SELECT p.category, s.region, SUM(s.qty * s.price) as revenue
        FROM sales s JOIN products p ON s.product_id = p.product_id
        GROUP BY p.category, s.region
        """
        df_rev = pd.read_sql_query(q, conn)
        fig = px.sunburst(df_rev, path=['category','region'], values='revenue', title='Receita por categoria e região')
        fig.update_layout(margin=dict(t=40,l=0,r=0,b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader('Controles')
        sel_region = st.selectbox('Filtrar região (opcional)', options=['Todas'] + ['Norte','Nordeste','Sudeste','Sul','Centro-Oeste'])
        if sel_region != 'Todas':
            df_rev = df_rev[df_rev['region'] == sel_region]
            fig2 = px.treemap(df_rev, path=['category','region'], values='revenue')
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('---')
        st.write('Dica: clique nas fatias para explorar.')
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card" style="margin-top:14px">', unsafe_allow_html=True)
    st.subheader('Animação: Top produtos por receita ao longo do ano')
    q2 = """
    SELECT s.month, p.product, SUM(s.qty * s.price) as revenue
    FROM sales s JOIN products p ON s.product_id = p.product_id
    GROUP BY s.month, p.product
    ORDER BY s.month
    """
    df_time = pd.read_sql_query(q2, conn)
    fig_anim = px.bar(df_time, x='product', y='revenue', color='product', animation_frame='month', range_y=[0, df_time['revenue'].max()*1.1], title='Top produtos por mês')
    fig_anim.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_anim, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


with pages[1]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader('Console SQL — rode consultas na DB em memória')
    default = 'SELECT * FROM products LIMIT 10;'
    query = st.text_area('Escreva sua query SQL:', value=default, height=120)
    run = st.button('Executar SQL')
    if run:
        try:
            df = pd.read_sql_query(query, conn)
            st.success(f'Resultado: {len(df)} linhas')
            st.dataframe(df)
            if st.checkbox('Mostrar gráfico automático (se aplicável)'):
                if {'revenue','month','product'}.issubset(set(df.columns)):
                    fig = px.line(df, x='month', y='revenue', color='product')
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error('Erro na consulta: ' + str(e))
    st.markdown('</div>', unsafe_allow_html=True)

with pages[2]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader('Preview dinâmico do próprio código (mostre aos seguidores)')
    if st.button('Mostrar código deste arquivo'):
        import sys
        try:
            with open(__file__, 'r', encoding='utf-8') as f:
                code_raw = f.read()
        except Exception:
            code_raw = inspect.getsource(inspect.getmodule(inspect.currentframe()))
        st.code(code_raw, language='python')
    st.markdown('</div>', unsafe_allow_html=True)

with pages[3]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader('Exportar resultados e compartilhar')
    sample_export = pd.read_sql_query('SELECT * FROM sales LIMIT 100', conn)
    csv = sample_export.to_csv(index=False).encode('utf-8')
    st.download_button('Baixar CSV (amostra 100 linhas)', data=csv, file_name='labranel_sales_sample.csv', mime='text/csv')
    st.write('Você pode rodar este app localmente e gravar a tela para mostrar ao público.')
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('\n---\n<small class="small">Feito com Python + Streamlit — single-file. Personalize os dados, temas e textos para seu projeto.</small>', unsafe_allow_html=True)
