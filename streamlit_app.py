import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Predicciones Montoya - LaLiga 2026", layout="wide", page_icon="⚽")

# --- CONEXIÓN A LA BASE DE DATOS ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345", # CAMBIA ESTO
        database="Proyecto"
    )

# --- CARGA DE DATOS ---
def load_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- INTERFAZ DE USUARIO ---
st.title("⚽ Dashboard de Análisis Deportivo 2026")
st.markdown(f"**Desarrollado por:** Santiago Montoya | *Talento Tech*")

# Sidebar - Logos de las Ligas
st.sidebar.header("Competiciones Top")
ligas = {
    "LaLiga": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/LaLiga_EA_Sports_logo.svg/512px-LaLiga_EA_Sports_logo.svg.png",
    "Premier League": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f2/Premier_League_Logo.svg/512px-Premier_League_Logo.svg.png",
    "Champions League": "https://upload.wikimedia.org/wikipedia/en/thumb/b/bf/UEFA_Champions_League_logo_2.svg/512px-UEFA_Champions_League_logo_2.svg.png",
    "Serie A": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Serie_A_logo_2022.svg/512px-Serie_A_logo_2022.svg.png"
}

for liga, url in ligas.items():
    st.sidebar.image(url, caption=liga, width=80)

# Pestañas principales
tab1, tab2, tab3 = st.tabs(["📊 Estadísticas Generales", "🏟️ Equipos", "🎲 Probabilidades"])

with tab1:
    st.header("Resumen de la Temporada")
    try:
        df_partidos = load_data("SELECT * FROM Partidos")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Partidos", len(df_partidos))
        col2.metric("Promedio Goles Local", round(df_partidos['goles_local'].mean(), 2))
        col3.metric("Promedio Goles Visitante", round(df_partidos['goles_visitante'].mean(), 2))

        # Gráfico de Goles
        fig = px.histogram(df_partidos, x="goles_local", title="Distribución de Goles Locales", color_discrete_sequence=['#f39c12'])
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")

with tab2:
    st.header("Análisis por Equipo")
    try:
        equipos = load_data("SELECT * FROM Equipos")
        seleccion = st.selectbox("Selecciona un equipo para ver su detalle:", equipos['nombre'])
        
        # Consulta filtrada
        id_equipo = equipos[equipos['nombre'] == seleccion]['equipo_id'].values[0]
        stats_query = f"""
            SELECT p.fecha, p.goles_local, p.goles_visitante, ep.posesion_local 
            FROM Partidos p 
            JOIN Estadisticas_Partido ep ON p.partido_id = ep.partido_id
            WHERE p.id_local = {id_equipo}
        """
        df_stats = load_data(stats_query)
        st.write(f"Últimos partidos en casa de {seleccion}")
        st.dataframe(df_stats, use_container_width=True)
    except Exception as e:
        st.warning("Asegúrate de que las tablas tengan datos.")

with tab3:
    st.header("Mercado de Apuestas")
    st.info("Visualización de las cuotas actuales y valor esperado.")
    try:
        df_cuotas = load_data("""
            SELECT e1.nombre as Local, e2.nombre as Visitante, c.cuota_local, c.cuota_empate, c.cuota_visitante 
            FROM Cuotas c
            JOIN Partidos p ON c.partido_id = p.partido_id
            JOIN Equipos e1 ON p.id_local = e1.equipo_id
            JOIN Equipos e2 ON p.id_visitante = e2.equipo_id
        """)
        st.table(df_cuotas.head(10))
    except Exception as e:
        st.error("No se pudieron cargar las cuotas.")