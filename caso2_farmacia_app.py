
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ① Configuración
st.set_page_config(page_title='Farma Dashboard', page_icon='💊',
                   layout='wide', initial_sidebar_state='expanded')

# ② Carga de datos con caché
@st.cache_data
def cargar_datos():
    ruta = os.path.join(os.path.dirname(__file__), 'caso2_farmacia_dataset.csv')
    df = pd.read_csv(ruta)
    df['fecha_venta'] = pd.to_datetime(df['fecha_venta'])
    return df

df = cargar_datos()

# ── Sidebar  filtros ───────────────────────────────────────
with st.sidebar:
    st.header("🔧 Filtros")

    filtro_vencimiento = st.checkbox(
        "⚠️ Solo vencimiento crítico (< 90 días)"
    )

    filtro_stock = st.checkbox(
        "📦 Solo stock crítico (< 50 unidades)"
    )
# ── Aplicar filtros globales ──────────────────────
df_f = df.copy()

if filtro_vencimiento:
    df_f = df_f[df_f['dias_vencimiento'] < 90]

if filtro_stock:
    df_f = df_f[df_f['stock_disponible'] < 50]
                                    

# ⑤ Título
st.title("💊 Farma — Dashboard de Operaciones Farmacéuticas")
st.markdown("**Panel de control de ventas · 2024**")
st.markdown("---")

# ⑥ KPIs (patrón F)
k1, k2, k3 = st.columns(3)

# ── KPI 1: Ventas totales y promedio ───────────────────────────
total_ventas = df['total_venta_cop'].sum()

# KPI 2:  Calcula el promedio de 'total_venta_cop'
promedio_ventas = df['total_venta_cop'].mean()

# KPI 3:  Calcula la cantidad total de unidades vendidas
total_unidades = df['cantidad_unidades'].sum()

k1.metric(" Total Ventas",    f"${total_ventas:,}")
k2.metric(" Promedio de ventas",    f"{promedio_ventas}")
k3.metric("Total Unidades",  f"{total_unidades:,}")
st.markdown("---")



# FUnciones de gráficos
# grafico 1 col 1:
top5_medicamentos = (
    df.groupby('medicamento')
      .agg(ventas_totales=('total_venta_cop', 'sum'),     # ??? suma
           unidades=('cantidad_unidades', 'sum')         # ??? suma también
      )
      .sort_values('ventas_totales', ascending=False)               # ??? ordena por ventas_totales
      .head(5)
      .reset_index()
)

# grafico 2 col 2
ventas_categoria = df.groupby('categoria')['total_venta_cop'].sum().reset_index()

# grafico 3 col 3
ventas_mes = df.groupby(df['fecha_venta'].dt.to_period('M'))['total_venta_cop'].sum().reset_index()
ventas_mes['fecha_venta'] = ventas_mes['fecha_venta'].astype(str)

# grafico 5 col 5
ventas_ciudad = (
    df.groupby('ciudad')
      .agg(
          total_ventas=('total_venta_cop', 'sum'),
          num_ventas=('id_venta', 'count')
      )
      .reset_index()
)
pivot_ciudad_trim = df.pivot_table(
    values='total_venta_cop',                     # ??? total_venta_cop
    index='ciudad',                      # ??? ciudad
    columns='trimestre',                    # ??? trimestre
    aggfunc='sum'
).round(0)



# ⑦ Fila 1: línea + pie (patrón Z)
col1, col2 = st.columns([1.5, 1])
with col1:
    fig = px.bar(
        top5_medicamentos,
        x='ventas_totales',
        y='medicamento',
        orientation='h',
        title='🏆 Top 5 Medicamentos por Ventas',
        labels={
            'ventas_totales': 'Ventas (COP)',
            'medicamento': 'Medicamento'
        },
        color='ventas_totales',
        color_continuous_scale='Teal',
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)


with col2:
    ventas_categoria = (
        df_f.groupby('categoria')['total_venta_cop']
        .sum()
        .reset_index()
    )

    fig2 = px.pie(
        ventas_categoria,
        names='categoria',
        values='total_venta_cop',
        title='💊 Distribución de Ventas por Categoría de Medicamento',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig2, use_container_width=True)


# ⑧ Fila 2: barras + scatter (patrón Z invertido)
col3, col4 = st.columns([1, 1.5])
with col3:
    fig3 = px.line(
    ventas_mes,
    x='fecha_venta',
    y='total_venta_cop',
    markers=True,                     # ??? True para mostrar puntos
    title='📅 Evolución Mensual de Ventas (COP)',
    labels={'fecha_venta': 'Mes', 'total_venta_cop': 'Ventas (COP)'}
)

    st.plotly_chart(fig3, use_container_width=True)

with col4:
    fig4 = px.scatter(
    df,
    x='precio_unitario_cop',                          # ??? precio unitario
    y='cantidad_unidades',                          # ??? cantidad de unidades
    color='categoria',                      # ??? color por categoría
    hover_data=['medicamento', 'farmacia'],
    title='💰 Precio Unitario vs Cantidad Vendida',
    labels={
        'precio_unitario_cop': 'Precio Unitario (COP)',
        'cantidad_unidades': 'Unidades Vendidas'
    }
)
    st.plotly_chart(fig4, use_container_width=True)


fig5 = px.imshow(
pivot_ciudad_trim,
title='🌡️ Ventas por Ciudad y Trimestre (COP)',
color_continuous_scale='RdYlGn',     # ??? elige una escala: 'Blues', 'Viridis', 'RdYlGn'
text_auto=True
)
st.plotly_chart(fig5, use_container_width=True)


# ⑩ Tabla colapsable
with st.expander("📋 Ver datos filtrados"):
    st.dataframe(df_f.sort_values('fecha_venta', ascending=False), use_container_width=True)
    st.download_button("⬇️ Descargar CSV", df_f.to_csv(index=False), "farmacia.csv")

st.caption("🔧 Streamlit + Plotly | Clase de Visualización de Datos")
