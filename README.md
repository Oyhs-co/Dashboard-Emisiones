# Dashboard de Análisis de Emisiones 🌍

Este proyecto proporciona un análisis completo de datos de emisiones de gases de efecto invernadero, utilizando herramientas modernas de Python para el procesamiento, análisis y visualización de datos.

## Objetivo

Analizar la cantidad y gravedad de las emisiones, su impacto en la contaminación y las repercusiones que afectan al medio ambiente, respondiendo preguntas clave sobre cómo inciden cada uno de los gases en la contaminación.

## Herramientas Utilizadas

### Procesamiento de Datos
- **Polars**: Procesamiento ultrarrápido de datasets
- **NumPy**: Cálculos numéricos avanzados

### Análisis Exploratorio
- **JupyterLab**: Entorno interactivo de notebooks
- **SciPy**: Análisis estadístico y matemático

### Visualización Interactiva
- **Plotly Express**: Gráficos interactivos profesionales

### Dashboard y Aplicación
- **Streamlit**: Dashboard interactivo para análisis en tiempo real

## Estructura del Proyecto

```
├── enhanced_data_processing.py # Procesamiento de datos con ponderación de gases
├── main.py      # Dashboard principal de Streamlit
├── requirements.txt            # Dependencias del proyecto
├── README.md                   # Documentación del proyecto
```

## Instalación

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecutar el dashboard:
```bash
streamlit run main.py
```

## Funcionalidades del Dashboard

### Métricas Principales
- Emisiones totales de CO2 equivalente (original y ponderadas)
- Emisiones por tipo de gas (CO2, CH4, N2O) con y sin ponderación
- **Nuevas métricas ponderadas**: Emisiones ponderadas por GWP (Potencial de Calentamiento Global) e Impacto Combinado.
- Filtros interactivos por año

### Visualizaciones
1. **Tendencia de Emisiones Totales**: Gráfico de líneas que muestra la evolución temporal (original y ponderadas)
2. **Emisiones por Tipo de Gas**: Gráfico de área apilada para comparar contribuciones (original y ponderadas)
3. **Principales Fuentes de Emisiones**: Ranking de clasificaciones con mayores emisiones (original y ponderadas)
4. **Distribución Porcentual de Emisiones por Clasificación**: Gráfico de pastel para ver la contribución de cada clasificación.
5. **Matriz de Correlación entre Gases**: Visualización de la relación entre los diferentes gases de efecto invernadero.

### Análisis Estadístico
- Estadísticas descriptivas de los datos
- Análisis de correlación entre diferentes tipos de gases
- Tabla de datos detallados con filtros

### Análisis Específico de la Industria
- **Filtrado y análisis de datos industriales**: Secciones dedicadas a clasificaciones que contienen 'Industr' o 'Fabricación'.
- **Visualizaciones industriales**: Tendencias, distribución por tipo de gas y top clasificaciones específicas del sector industrial.

### Impacto Detallado de los Gases
- Información detallada sobre el GWP, factor de daño ambiental, vida útil y fuentes de CO2, CH4 y N2O.

## Análisis de Impacto Ambiental

### Gases de Efecto Invernadero Analizados

1. **CO2 (Dióxido de Carbono)**
   - Principal contribuyente al efecto invernadero
   - Proviene principalmente de la quema de combustibles fósiles
   - Permanece en la atmósfera durante décadas

2. **CH4 (Metano)**
   - **28 veces más potente que el CO2** en términos de calentamiento global (GWP)
   - Fuentes: agricultura, ganadería, vertederos
   - Vida útil más corta pero impacto inmediato mayor

3. **N2O (Óxido Nitroso)**
   - **265 veces más potente que el CO2** (GWP)
   - Fuentes: agricultura, industria, combustión
   - Permanece en la atmósfera por más de 100 años

### Repercusiones Ambientales

- **Calentamiento Global**: Aumento de temperaturas globales
- **Cambio Climático**: Alteración de patrones climáticos
- **Acidificación de Océanos**: Absorción de CO2 por los océanos
- **Pérdida de Biodiversidad**: Cambios en ecosistemas
- **Eventos Climáticos Extremos**: Mayor frecuencia e intensidad

## Despliegue en Streamlit Cloud

Para desplegar en Streamlit Cloud:

1. Subir el proyecto a un repositorio de GitHub
2. Conectar con Streamlit Cloud
3. Configurar el archivo principal como `main.py`
4. Asegurar que `requirements.txt` esté en el directorio raíz

## Uso del Proyecto

1. **Análisis Exploratorio**: Ejecutar el notebook `emissions_eda.ipynb`
2. **Visualizaciones Estáticas**: Ejecutar `visualization.py` para generar gráficos HTML
3. **Dashboard Interactivo**: Ejecutar `streamlit run main.py`

## Contribuciones

Este proyecto está diseñado para ser extensible. Posibles mejoras:
- Integración con APIs de datos ambientales en tiempo real
- Modelos predictivos de emisiones futuras
- Análisis geoespacial si se dispone de datos de ubicación
- Comparaciones internacionales de emisiones

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia GNU GPL-3.0 .

