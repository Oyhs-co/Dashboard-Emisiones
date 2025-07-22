import polars as pl
import numpy as np

# Potenciales de Calentamiento Global (GWP) a 100 años según IPCC AR6
# Estos valores reflejan cuántas veces más potente es cada gas comparado con CO2
GWP_VALUES = {
    'CO2': 1,      # Dióxido de carbono (referencia)
    'CH4': 28,     # Metano (28 veces más potente que CO2)
    'N2O': 265     # Óxido nitroso (265 veces más potente que CO2)
}

# Factores de daño ambiental adicionales (escala 1-10, donde 10 es más dañino)
ENVIRONMENTAL_DAMAGE_FACTORS = {
    'CO2': 5,      # Daño moderado pero persistente
    'CH4': 8,      # Daño alto pero vida útil más corta
    'N2O': 9       # Daño muy alto y persistente
}

def process_data_with_weighting(file_path):
    """
    Procesa los datos aplicando ponderaciones basadas en el potencial de calentamiento global
    y factores de daño ambiental.
    """
    # Cargar y limpiar datos básicos
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
    
    # Convertir columnas numéricas
    numeric_cols = ['CH4_eq', 'CO2_eq', 'N2O_eq', 'Total_Emisiones', 'Emisiones_netas']
    for col in numeric_cols:
        if col in df.columns:
            df = df.with_columns(pl.col(col).cast(pl.String).str.replace_all(",", ".").cast(pl.Float64))
    
    # Rellenar valores nulos con 0
    for col in numeric_cols:
        if col in df.columns:
            df = df.with_columns(pl.col(col).fill_null(0))
    
    # Filtrar filas con años nulos
    df = df.filter(pl.col('Anio').is_not_null())
    
    # Calcular emisiones ponderadas por GWP (Potencial de Calentamiento Global)
    df = df.with_columns([
        (pl.col('CO2_eq') * GWP_VALUES['CO2']).alias('CO2_GWP_weighted'),
        (pl.col('CH4_eq') * GWP_VALUES['CH4']).alias('CH4_GWP_weighted'),
        (pl.col('N2O_eq') * GWP_VALUES['N2O']).alias('N2O_GWP_weighted')
    ])
    
    # Calcular total ponderado por GWP
    df = df.with_columns(
        (pl.col('CO2_GWP_weighted') + pl.col('CH4_GWP_weighted') + pl.col('N2O_GWP_weighted')).alias('Total_GWP_weighted')
    )
    
    # Calcular emisiones ponderadas por factor de daño ambiental
    df = df.with_columns([
        (pl.col('CO2_eq') * ENVIRONMENTAL_DAMAGE_FACTORS['CO2']).alias('CO2_damage_weighted'),
        (pl.col('CH4_eq') * ENVIRONMENTAL_DAMAGE_FACTORS['CH4']).alias('CH4_damage_weighted'),
        (pl.col('N2O_eq') * ENVIRONMENTAL_DAMAGE_FACTORS['N2O']).alias('N2O_damage_weighted')
    ])
    
    # Calcular total ponderado por daño ambiental
    df = df.with_columns(
        (pl.col('CO2_damage_weighted') + pl.col('CH4_damage_weighted') + pl.col('N2O_damage_weighted')).alias('Total_damage_weighted')
    )
    
    # Calcular índice de impacto combinado (GWP + Daño Ambiental)
    df = df.with_columns(
        ((pl.col('Total_GWP_weighted') * 0.7) + (pl.col('Total_damage_weighted') * 0.3)).alias('Impacto_Combinado')
    )
    
    # Calcular porcentajes de contribución por gas (basado en GWP)
    df = df.with_columns([
        (pl.col('CO2_GWP_weighted') / pl.col('Total_GWP_weighted') * 100).alias('CO2_porcentaje_contribucion'),
        (pl.col('CH4_GWP_weighted') / pl.col('Total_GWP_weighted') * 100).alias('CH4_porcentaje_contribucion'),
        (pl.col('N2O_GWP_weighted') / pl.col('Total_GWP_weighted') * 100).alias('N2O_porcentaje_contribucion')
    ])
    
    # Manejar divisiones por cero
    df = df.with_columns([
        pl.col('CO2_porcentaje_contribucion').fill_null(0),
        pl.col('CH4_porcentaje_contribucion').fill_null(0),
        pl.col('N2O_porcentaje_contribucion').fill_null(0)
    ])
    
    return df

def calculate_weighted_statistics(df):
    """
    Calcula estadísticas avanzadas con las ponderaciones aplicadas.
    """
    stats = {}
    
    # Estadísticas básicas de emisiones ponderadas
    stats['total_gwp_weighted'] = df['Total_GWP_weighted'].sum()
    stats['total_damage_weighted'] = df['Total_damage_weighted'].sum()
    stats['total_combined_impact'] = df['Impacto_Combinado'].sum()
    
    # Contribución promedio por gas
    stats['avg_co2_contribution'] = df['CO2_porcentaje_contribucion'].mean()
    stats['avg_ch4_contribution'] = df['CH4_porcentaje_contribucion'].mean()
    stats['avg_n2o_contribution'] = df['N2O_porcentaje_contribucion'].mean()
    
    # Gas más problemático por año
    emissions_by_year = df.group_by('Anio').agg([
        pl.sum('CO2_GWP_weighted').alias('CO2_total'),
        pl.sum('CH4_GWP_weighted').alias('CH4_total'),
        pl.sum('N2O_GWP_weighted').alias('N2O_total'),
        pl.sum('Total_GWP_weighted').alias('Total_GWP')
    ]).sort('Anio')
    
    stats['emissions_by_year'] = emissions_by_year
    
    # Clasificaciones más problemáticas
    top_classifications = df.group_by('Clasificacion').agg([
        pl.sum('Total_GWP_weighted').alias('Total_GWP_weighted'),
        pl.sum('Impacto_Combinado').alias('Impacto_Combinado')
    ]).sort('Total_GWP_weighted', descending=True).head(10)
    
    stats['top_classifications'] = top_classifications
    
    return stats

def get_gas_impact_info():
    """
    Retorna información detallada sobre el impacto de cada gas.
    """
    gas_info = {
        'CO2': {
            'name': 'Dióxido de Carbono',
            'gwp': GWP_VALUES['CO2'],
            'damage_factor': ENVIRONMENTAL_DAMAGE_FACTORS['CO2'],
            'lifetime': '300-1000 años',
            'sources': 'Combustibles fósiles, deforestación, industria',
            'impact': 'Principal responsable del calentamiento global, acidificación oceánica'
        },
        'CH4': {
            'name': 'Metano',
            'gwp': GWP_VALUES['CH4'],
            'damage_factor': ENVIRONMENTAL_DAMAGE_FACTORS['CH4'],
            'lifetime': '9 años',
            'sources': 'Ganadería, agricultura, vertederos, gas natural',
            'impact': 'Potente gas de efecto invernadero, contribuye a la formación de ozono troposférico'
        },
        'N2O': {
            'name': 'Óxido Nitroso',
            'gwp': GWP_VALUES['N2O'],
            'damage_factor': ENVIRONMENTAL_DAMAGE_FACTORS['N2O'],
            'lifetime': '114 años',
            'sources': 'Agricultura, combustión, industria química',
            'impact': 'Destruye la capa de ozono, potente gas de efecto invernadero'
        }
    }
    return gas_info

if __name__ == "__main__":
    # Procesar datos con ponderaciones
    file_path = "/home/ubuntu/upload/proyecto2.csv"
    df_weighted = process_data_with_weighting(file_path)
    
    print("DataFrame con ponderaciones aplicadas:")
    print(df_weighted.head())
    print(f"\nColumnas disponibles: {df_weighted.columns}")
    
    # Calcular estadísticas
    stats = calculate_weighted_statistics(df_weighted)
    print(f"\nTotal GWP ponderado: {stats['total_gwp_weighted']:,.0f}")
    print(f"Total daño ambiental ponderado: {stats['total_damage_weighted']:,.0f}")
    print(f"Impacto combinado total: {stats['total_combined_impact']:,.0f}")
    
    # Mostrar información de gases
    gas_info = get_gas_impact_info()
    print("\nInformación de gases:")
    for gas, info in gas_info.items():
        print(f"{gas} ({info['name']}): GWP={info['gwp']}, Factor de daño={info['damage_factor']}")

