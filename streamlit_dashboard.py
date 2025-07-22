import streamlit as st
import polars as pl
import plotly.express as px
import numpy as np
from scipy import stats
from enhanced_data_processing import process_data_with_weighting, get_gas_impact_info

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Análisis de Emisiones",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función para cargar y procesar los datos (ahora usa la función mejorada)
@st.cache_data
def load_processed_data(file_path):
    return process_data_with_weighting(file_path)

# Función para generar visualizaciones
def generate_emissions_by_year(df, emission_col, title_suffix=""): # Añadido emission_col y title_suffix
    emisiones_por_anio = df.group_by("Anio").agg(pl.sum(emission_col).alias("Total_Emisiones_Anual")).sort("Anio")
    fig = px.line(emisiones_por_anio.to_pandas(), x="Anio", y="Total_Emisiones_Anual",
                  title=f"Tendencia de Emisiones Totales {title_suffix} por Año",
                  labels={"Anio": "Año", "Total_Emisiones_Anual": "Emisiones Totales (CO2eq)"})
    fig.update_layout(height=400)
    return fig

def generate_emissions_by_gas_type(df, gas_cols, title_suffix=""): # Añadido gas_cols y title_suffix
    emisiones_gases_por_anio = df.group_by("Anio").agg(
        [pl.sum(col).alias(col) for col in gas_cols]
    ).sort("Anio")
    
    emisiones_gases_por_anio_pd = emisiones_gases_por_anio.to_pandas().melt(id_vars=["Anio"],
                                                                           value_vars=gas_cols,
                                                                           var_name="Tipo_Gas",
                                                                           value_name="Emisiones")
    
    fig = px.area(emisiones_gases_por_anio_pd, x="Anio", y="Emisiones", color="Tipo_Gas",
                  title=f"Emisiones {title_suffix} por Tipo de Gas a lo largo del Tiempo",
                  labels={"Anio": "Año", "Emisiones": "Emisiones (CO2eq)", "Tipo_Gas": "Tipo de Gas"})
    fig.update_layout(height=400)
    return fig

def generate_top_classifications(df, emission_col, top_n=10, title_suffix=""): # Añadido emission_col y title_suffix
    emisiones_por_clasificacion = df.group_by("Clasificacion").agg(
        pl.sum(emission_col).alias("Suma_Total_Emisiones")
    ).sort("Suma_Total_Emisiones", descending=True).head(top_n)
    
    fig = px.bar(emisiones_por_clasificacion.to_pandas(), x="Suma_Total_Emisiones", y="Clasificacion",
                 orientation="h", title=f"Top {top_n} Clasificaciones con Mayores Emisiones {title_suffix}",
                 labels={"Suma_Total_Emisiones": "Emisiones Totales (CO2eq)", "Clasificacion": "Clasificación"})
    fig.update_layout(yaxis={"categoryorder":"total ascending"}, height=500)
    return fig

def generate_pie_chart_by_classification(df, emission_col, title_suffix=""): # Nueva función para gráfico de pastel
    emisiones_por_clasificacion = df.group_by("Clasificacion").agg(
        pl.sum(emission_col).alias("Suma_Total_Emisiones")
    ).sort("Suma_Total_Emisiones", descending=True)
    
    fig = px.pie(emisiones_por_clasificacion.to_pandas(), values="Suma_Total_Emisiones", names="Clasificacion",
                 title=f"Distribución de Emisiones {title_suffix} por Clasificación",
                 hole=0.3) # Añade un agujero para un donut chart
    fig.update_traces(textposition=\'inside\', textinfo=\'percent+label\')
    fig.update_layout(height=500)
    return fig

def generate_correlation_heatmap(df):
    # Seleccionar solo las columnas de emisiones para la correlación
    emissions_data = df.select(["CH4_eq", "CO2_eq", "N2O_eq"])
    
    # Convertir a pandas DataFrame para calcular la matriz de correlación
    corr_matrix = emissions_data.to_pandas().corr()
    
    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                    title="Matriz de Correlación entre Gases de Efecto Invernadero")
    fig.update_layout(height=400)
    return fig

# Función principal de la aplicación
def main():
    st.title("🌍 Dashboard de Análisis de Emisiones")
    st.markdown("### Análisis de la cantidad y gravedad de las emisiones y su impacto ambiental")
    
    # Cargar datos
    file_path = "/home/ubuntu/upload/proyecto2.csv"
    df = load_processed_data(file_path)
    
    # Sidebar para filtros
    st.sidebar.header("Filtros")
    
    # Filtro por año
    years = sorted(df["Anio"].unique().to_list())
    selected_years = st.sidebar.multiselect("Seleccionar Años", years, default=years)
    
    # Filtrar datos según selección
    if selected_years:
        df_filtered = df.filter(pl.col("Anio").is_in(selected_years))
    else:
        df_filtered = df
    
    # Selección de tipo de emisión para visualizaciones
    emission_type = st.sidebar.radio(
        "Seleccionar Tipo de Emisión",
        ("Emisiones Totales (Original)", "Emisiones Ponderadas por GWP", "Impacto Combinado")
    )
    
    if emission_type == "Emisiones Totales (Original)":
        current_emission_col = "Total_Emisiones"
        gas_cols_for_viz = ["CH4_eq", "CO2_eq", "N2O_eq"]
        title_suffix = "(Original)"
    elif emission_type == "Emisiones Ponderadas por GWP":
        current_emission_col = "Total_GWP_weighted"
        gas_cols_for_viz = ["CH4_GWP_weighted", "CO2_GWP_weighted", "N2O_GWP_weighted"]
        title_suffix = "(Ponderadas por GWP)"
    else: # Impacto Combinado
        current_emission_col = "Impacto_Combinado"
        gas_cols_for_viz = ["CH4_damage_weighted", "CO2_damage_weighted", "N2O_damage_weighted"]
        title_suffix = "(Impacto Combinado)"

    # Métricas principales
    st.header("📈 Métricas Clave")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_emissions = df_filtered[current_emission_col].sum()
        st.metric(f"Total {emission_type}", f"{total_emissions:,.0f} CO2eq")
    
    with col2:
        co2_emissions = df_filtered[gas_cols_for_viz[1]].sum() # CO2_eq o CO2_GWP_weighted
        st.metric(f"Emisiones CO2 {title_suffix}", f"{co2_emissions:,.0f} CO2eq")
    
    with col3:
        ch4_emissions = df_filtered[gas_cols_for_viz[0]].sum() # CH4_eq o CH4_GWP_weighted
        st.metric(f"Emisiones CH4 {title_suffix}", f"{ch4_emissions:,.0f} CO2eq")
    
    with col4:
        n2o_emissions = df_filtered[gas_cols_for_viz[2]].sum() # N2O_eq o N2O_GWP_weighted
        st.metric(f"Emisiones N2O {title_suffix}", f"{n2o_emissions:,.0f} CO2eq")
    
    # Visualizaciones principales
    st.header("📊 Visualizaciones")
    
    # Gráfico de tendencias por año
    st.subheader(f"Tendencia de Emisiones Totales {title_suffix}")
    fig1 = generate_emissions_by_year(df_filtered, current_emission_col, title_suffix)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Gráfico de emisiones por tipo de gas
    st.subheader(f"Emisiones {title_suffix} por Tipo de Gas")
    fig2 = generate_emissions_by_gas_type(df_filtered, gas_cols_for_viz, title_suffix)
    st.plotly_chart(fig2, use_container_width=True)
    
    # Top clasificaciones
    st.subheader(f"Principales Fuentes de Emisiones {title_suffix}")
    top_n = st.slider("Número de clasificaciones a mostrar", 5, 20, 10, key="top_n_slider")
    fig3 = generate_top_classifications(df_filtered, current_emission_col, top_n, title_suffix)
    st.plotly_chart(fig3, use_container_width=True)

    # Nueva gráfica: Distribución de Emisiones por Clasificación (Pie Chart)
    st.subheader(f"Distribución Porcentual de Emisiones {title_suffix} por Clasificación")
    fig_pie = generate_pie_chart_by_classification(df_filtered, current_emission_col, title_suffix)
    st.plotly_chart(fig_pie, use_container_width=True)

    # Nueva gráfica: Matriz de Correlación
    st.subheader("Matriz de Correlación entre Gases de Efecto Invernadero")
    fig_corr = generate_correlation_heatmap(df_filtered)
    st.plotly_chart(fig_corr, use_container_width=True)

    # Apartado de Análisis Industrial
    st.header("🏭 Análisis Específico de la Industria")
    st.markdown("Aquí se presenta un análisis detallado de las emisiones provenientes de sectores industriales. Se consideran clasificaciones que contienen 'Industr' o 'Fabricación'.")

    # Filtrar datos para clasificaciones industriales
    industrial_df = df_filtered.filter(
        pl.col("Clasificacion").str.contains("Industr") | pl.col("Clasificacion").str.contains("Fabricación")
    )

    if not industrial_df.is_empty():
        # Top clasificaciones industriales
        st.subheader(f"Top Clasificaciones Industriales {title_suffix}")
        top_n_industry = st.slider("Número de clasificaciones industriales a mostrar", 3, 15, 5, key="top_n_industry_slider")
        fig_industry_bar = generate_top_classifications(industrial_df, current_emission_col, top_n_industry, f"{title_suffix} (Industrial)")
        st.plotly_chart(fig_industry_bar, use_container_width=True)

        # Tendencia de emisiones industriales por año
        st.subheader(f"Tendencia de Emisiones Industriales {title_suffix} por Año")
        fig_industry_line = generate_emissions_by_year(industrial_df, current_emission_col, f"{title_suffix} (Industrial)")
        st.plotly_chart(fig_industry_line, use_container_width=True)

        # Distribución de emisiones industriales por tipo de gas
        st.subheader(f"Emisiones Industriales {title_suffix} por Tipo de Gas")
        fig_industry_area = generate_emissions_by_gas_type(industrial_df, gas_cols_for_viz, f"{title_suffix} (Industrial)")
        st.plotly_chart(fig_industry_area, use_container_width=True)

    else:
        st.info("No se encontraron datos para clasificaciones industriales en el rango de años seleccionado.")

    # Análisis estadístico
    st.header("📈 Análisis Estadístico")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Estadísticas Descriptivas")
        stats_df = df_filtered.select(["CH4_eq", "CO2_eq", "N2O_eq", "Total_Emisiones", "Total_GWP_weighted", "Impacto_Combinado"]).describe()
        st.dataframe(stats_df.to_pandas())
    
    with col2:
        st.subheader("Correlaciones entre Gases")
        # Calcular correlaciones
        ch4_emissions = df_filtered["CH4_eq"].to_numpy()
        co2_emissions = df_filtered["CO2_eq"].to_numpy()
        n2o_emissions = df_filtered["N2O_eq"].to_numpy()
        
        # Eliminar NaN
        ch4_emissions = ch4_emissions[~np.isnan(ch4_emissions)]
        co2_emissions = co2_emissions[~np.isnan(co2_emissions)]
        n2o_emissions = n2o_emissions[~np.isnan(n2o_emissions)]
        
        # Asegurar misma longitud
        min_len = min(len(ch4_emissions), len(co2_emissions), len(n2o_emissions))
        if min_len > 1:
            ch4_emissions = ch4_emissions[:min_len]
            co2_emissions = co2_emissions[:min_len]
            n2o_emissions = n2o_emissions[:min_len]
            
            corr_ch4_co2, _ = stats.pearsonr(ch4_emissions, co2_emissions)
            corr_ch4_n2o, _ = stats.pearsonr(ch4_emissions, n2o_emissions)
            corr_co2_n2o, _ = stats.pearsonr(co2_emissions, n2o_emissions)
            
            st.write(f"**CH4 vs CO2:** {corr_ch4_co2:.3f}")
            st.write(f"**CH4 vs N2O:** {corr_ch4_n2o:.3f}")
            st.write(f"**CO2 vs N2O:** {corr_co2_n2o:.3f}")
        else:
            st.write("No hay suficientes datos para calcular correlaciones.")
    
    # Información sobre el impacto de los gases
    st.header("🔬 Impacto Detallado de los Gases")
    gas_info = get_gas_impact_info()
    for gas, info in gas_info.items():
        st.subheader(f"{info['name']} ({gas})")
        st.write(f"**Potencial de Calentamiento Global (GWP):** {info['gwp']} (CO2eq)")
        st.write(f"**Factor de Daño Ambiental:** {info['damage_factor']}/10")
        st.write(f"**Vida Útil en la Atmósfera:** {info['lifetime']}")
        st.write(f"**Fuentes Principales:** {info['sources']}")
        st.write(f"**Impacto Clave:** {info['impact']}")

    # Tabla de datos
    st.header("📋 Datos Detallados")
    st.dataframe(df_filtered.to_pandas(), use_container_width=True)
    
    # Información adicional
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Información del Dataset")
    st.sidebar.write(f"**Total de registros:** {len(df_filtered)}")
    st.sidebar.write(f"**Años disponibles:** {len(years)}")
    st.sidebar.write(f"**Clasificaciones únicas:** {df_filtered["Clasificacion"].n_unique()}")

if __name__ == "__main__":
    main()

