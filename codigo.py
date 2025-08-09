# 🌌 LAVANEL
# Flask + Plotly + Pandas


from flask import Flask, render_template_string, request
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
import inspect
import random

# App Flask
app = Flask(__name__)

# Banco de dados 
produtos = ["Pizza Gamer", "Mouse RGB", "Cadeira Gamer", "Monitor UltraWide", "Headset Pro", "Teclado Mecânico", "Controle PS5"]
meses = ["Janeiro", "Fevereiro", "Março", "Abril"]

data = []
for mes in meses:
    for produto in produtos:
        data.append({"Produto": produto, "Vendas": random.randint(50, 500), "Mês": mes})

df = pd.DataFrame(data)
engine = create_engine("sqlite:///:memory:")
df.to_sql("vendas", con=engine, index=False, if_exists="replace")

HTML_BASE = """
<!DOCTYPE html>
<html>
<head>
    <title>🌌 Laravel — Showcode V3 🌌</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        @keyframes neonGlow {
            0%, 100% { text-shadow: 0 0 10px #0ff, 0 0 20px #0ff, 0 0 30px #00f; }
            50% { text-shadow: 0 0 20px #ff00ff, 0 0 30px #0ff, 0 0 40px #00f; }
        }
        @keyframes gradientBG {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        @keyframes fadeIn {
            from {opacity: 0;}
            to {opacity: 1;}
        }
        body {
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
            background-size: 400% 400%;
            animation: gradientBG 10s ease infinite;
            color: white;
        }
        h1 {
            animation: neonGlow 2s infinite;
            text-align: center;
            margin-top: 20px;
        }
        .container { margin-top: 30px; animation: fadeIn 1.5s ease-in; }
        pre {
            background-color: rgba(255,255,255,0.05);
            color: #00ffcc;
            padding: 10px;
            border-radius: 10px;
            overflow-x: auto;
        }
        textarea {
            background-color: rgba(255,255,255,0.1);
            color: white;
        }
        .btn-glow {
            background: linear-gradient(90deg, #00f, #0ff, #00f);
            background-size: 200% 200%;
            color: white;
            border: none;
            animation: gradientBG 3s ease infinite;
        }
        .btn-glow:hover {
            filter: brightness(1.3);
        }
    </style>
</head>
<body>
<div class="container">
    <h1>🌌 Laravel — Showcode V3 🚀</h1>
    <p class="text-center">💻 Dashboard futurista com gráficos animados e console SQL</p>
    <ul class="nav nav-tabs">
      <li class="nav-item"><a class="nav-link {% if page=='dashboard' %}active{% endif %}" href="/">Dashboard</a></li>
      <li class="nav-item"><a class="nav-link {% if page=='sql' %}active{% endif %}" href="/sql">SQL</a></li>
      <li class="nav-item"><a class="nav-link {% if page=='codigo' %}active{% endif %}" href="/codigo">Código</a></li>
    </ul>
    <div class="mt-4">
        {{ content|safe }}
    </div>
</div>
</body>
</html>
"""

#Dashboard 
@app.route("/")
def dashboard():
    fig1 = px.bar(df, x="Produto", y="Vendas", color="Mês", barmode="group",
                  title="🔥 Vendas por Produto", template="plotly_dark",
                  color_discrete_sequence=px.colors.qualitative.Bold)
    fig2 = px.pie(df.groupby("Produto").sum().reset_index(), names="Produto", values="Vendas",
                  title="🍕 Participação no Total de Vendas", hole=0.4,
                  color_discrete_sequence=px.colors.sequential.Plasma)
    fig3 = px.line(df.groupby(["Mês"]).sum().reset_index(), x="Mês", y="Vendas",
                   title="📈 Evolução das Vendas", markers=True,
                   color_discrete_sequence=["#0ff"], template="plotly_dark")
    
    content = fig1.to_html(full_html=False) + fig2.to_html(full_html=False) + fig3.to_html(full_html=False)
    return render_template_string(HTML_BASE, content=content, page="dashboard")

# Console SQL
@app.route("/sql", methods=["GET", "POST"])
def sql_console():
    query = ""
    result_html = ""
    if request.method == "POST":
        query = request.form.get("query")
        try:
            result_df = pd.read_sql(text(query), con=engine)
            result_html = result_df.to_html(classes="table table-dark table-striped", index=False)
        except Exception as e:
            result_html = f"<p style='color:red;'>⚠️ Erro: {e}</p>"
    form_html = f"""
        <form method="POST">
            <textarea name="query" rows="4" class="form-control" placeholder="Digite sua query SQL aqui">{query}</textarea>
            <button class="btn btn-glow mt-2">Executar 🚀</button>
        </form>
        <div class="mt-3">{result_html}</div>
    """
    return render_template_string(HTML_BASE, content=form_html, page="sql")

#codigo fonte
@app.route("/codigo")
def codigo():
    codigo_str = inspect.getsource(inspect.getmodule(inspect.currentframe()))
    return render_template_string(HTML_BASE, content=f"<pre>{codigo_str}</pre>", page="codigo")

#começar
if __name__ == "__main__":
    app.run(debug=True)
