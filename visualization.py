import polars as pl
import plotly.express as px

def process_data_for_viz(file_path):
    df = pl.read_csv(file_path)
    df = df.rename({
        'AÑO': 'Anio',
        'CLASIFICACION': 'Clasificacion',
        'CH4_eq': 'CH4_eq',
        'CO2_eq': 'CO2_eq',
        'N2O_eq': 'N2O_eq',
        'Total_Emisiones': 'Total_Emisiones',
        'Emisiones_netas': 'Emisiones_netas'
    })
    numeric_cols = ['CH4_eq', 'CO2_eq', 'N2O_eq', 'Total_Emisiones', 'Emisiones_netas']
    for col in numeric_cols:
        if col in df.columns:
            df = df.with_columns(pl.col(col).cast(pl.String).str.replace_all(",", ".").cast(pl.Float64))
    for col in numeric_cols:
        if col in df.columns:
            df = df.with_columns(pl.col(col).fill_null(0))
    return df

def generate_visualizations(df):
    # Visualización 1: Emisiones Totales por Año
    emisiones_por_anio = df.group_by('Anio').agg(pl.sum('Total_Emisiones').alias('Total_Emisiones_Anual')).sort('Anio')
    fig1 = px.line(emisiones_por_anio.to_pandas(), x='Anio', y='Total_Emisiones_Anual',
                   title='Tendencia de Emisiones Totales por Año',
                   labels={'Anio': 'Año', 'Total_Emisiones_Anual': 'Emisiones Totales (CO2eq)'})
    fig1.write_html("emisiones_totales_por_anio.html")
    print("Gráfico 'emisiones_totales_por_anio.html' generado exitosamente.")

    # Visualización 2: Emisiones por Tipo de Gas a lo largo del Tiempo (Área Stacked)
    # Filtrar para clasificaciones que son la suma total o relevantes para evitar duplicados en la visualización
    # Para este ejemplo, vamos a sumar por año y por tipo de gas
    emisiones_gases_por_anio = df.group_by('Anio').agg(
        pl.sum('CH4_eq').alias('CH4_eq'),
        pl.sum('CO2_eq').alias('CO2_eq'),
        pl.sum('N2O_eq').alias('N2O_eq')
    ).sort('Anio')

    # Convertir a formato largo para Plotly Express
    emisiones_gases_por_anio_pd = emisiones_gases_por_anio.to_pandas().melt(id_vars=['Anio'],
                                                                           value_vars=['CH4_eq', 'CO2_eq', 'N2O_eq'],
                                                                           var_name='Tipo_Gas',
                                                                           value_name='Emisiones')

    fig2 = px.area(emisiones_gases_por_anio_pd, x='Anio', y='Emisiones', color='Tipo_Gas',
                   title='Emisiones por Tipo de Gas a lo largo del Tiempo',
                   labels={'Anio': 'Año', 'Emisiones': 'Emisiones (CO2eq)', 'Tipo_Gas': 'Tipo de Gas'})
    fig2.write_html("emisiones_por_tipo_gas.html")
    print("Gráfico 'emisiones_por_tipo_gas.html' generado exitosamente.")

    # Visualización 3: Top 10 Clasificaciones con Mayores Emisiones (Barra Horizontal)
    # Sumar emisiones por clasificación en todos los años
    emisiones_por_clasificacion = df.group_by('Clasificacion').agg(
        pl.sum('Total_Emisiones').alias('Suma_Total_Emisiones')
    ).sort('Suma_Total_Emisiones', descending=True).head(10)

    fig3 = px.bar(emisiones_por_clasificacion.to_pandas(), x='Suma_Total_Emisiones', y='Clasificacion',
                   orientation='h', title='Top 10 Clasificaciones con Mayores Emisiones',
                   labels={'Suma_Total_Emisiones': 'Emisiones Totales (CO2eq)', 'Clasificacion': 'Clasificación'})
    fig3.update_layout(yaxis={'categoryorder':'total ascending'})
    fig3.write_html("top_clasificaciones_emisiones.html")
    print("Gráfico 'top_clasificaciones_emisiones.html' generado exitosamente.")

if __name__ == "__main__":
    file_path = "data/proyecto2.csv"
    processed_df = process_data_for_viz(file_path)
    generate_visualizations(processed_df)


