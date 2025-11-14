from flask import Flask, render_template, request, jsonify
from db import get_connection
from queries import ranking_query, headtohead_query, ultimos_partidos_query
import psycopg2.extras
import pandas as pd

app = Flask(__name__)


@app.route("/")
def home():
    conn = get_connection()
    # pandas usa el connection DBAPI; funciona aunque da advertencia
    df = pd.read_sql(ranking_query, conn)
    conn.close()

    df.columns = ["Equipo", "Ganados local", "Ganados visita", "Ganados", "Empates", "Derrotas loc", "Derrotas vis", "Derrotas", "GF", "GC", "+/-", "Puntos", '%', "Jugados"]
    df["+/-"] = df["+/-"].apply(
        lambda x: f'<span class="diff {"positive" if x > 0 else "negative" if x < 0 else "neutral"}">{x}</span>'
    )
    table_html = df.to_html(
        classes="table table-striped table-hover table-sm ranking-table sortable",
        index=False,
        border=0,
        escape=False
    )
    equipos = df["Equipo"].tolist()
    puntos = df["Puntos"].tolist()
    return render_template("index.html", table=table_html,
                           equipos_json=equipos, puntos_json=puntos)


# Página que muestra el formulario/selects (GET). La comparación se hace vía AJAX.
@app.route("/head-to-head", methods=["GET"])
def headtohead_page():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT ID_TEAM, Nombre FROM Equipos ORDER BY Nombre;")
    equipos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("headtohead.html", equipos=equipos)


# API que devuelve JSON con las estadísticas y últimos partidos (usada por fetch)
@app.route("/api/headtohead", methods=["POST"])
def api_headtohead():
    data = request.get_json() or {}
    eq1 = data.get("equipo1")
    eq2 = data.get("equipo2")

    if not eq1 or not eq2:
        return jsonify({"error": "falta equipo1 o equipo2"}), 400
    if str(eq1) == str(eq2):
        return jsonify({"error": "Los equipos deben ser distintos"}), 400

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Estadísticas head-to-head
    cur.execute(headtohead_query, {"eq1": int(eq1), "eq2": int(eq2)})
    stats = cur.fetchone() or {}

    # Últimos partidos (lista)
    cur.execute(ultimos_partidos_query, {"eq1": int(eq1), "eq2": int(eq2)})
    matches = cur.fetchall() or []

    # Obtener nombres de equipos para mostrar en frontend
    cur.execute("SELECT ID_TEAM, Nombre FROM Equipos WHERE ID_TEAM IN (%s, %s);",
                (int(eq1), int(eq2)))
    names = cur.fetchall()
    name_map = {r["id_team"]: r["nombre"] for r in names} if names else {}

    cur.close()
    conn.close()

    # Preparar respuesta limpia
    resp = {
        "stats": stats,
        "matches": matches,
        "names": name_map
    }
    return jsonify(resp)


if __name__ == "__main__":
    app.run(debug=True)
