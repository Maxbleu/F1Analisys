from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

import numpy as np
import pandas as pd

def interpolate_telemetry(telemetry_df, distances):
    result = pd.DataFrame({'Distance': distances})
    for col in telemetry_df.columns:
        if col != 'Distance':
            if pd.api.types.is_numeric_dtype(telemetry_df[col]):
                result[col] = np.interp(distances, telemetry_df['Distance'], telemetry_df[col])
            else:
                result[col] = pd.Series(telemetry_df[col].iloc[
                    np.abs(telemetry_df['Distance'].values[:, np.newaxis] - distances).argmin(axis=0)
                ]).values
    return result

def track_dominance_prediction(vueltas_pilotos, drivers_map:dict):
    """
    Predicts the dominance of drivers based on telemetry data using KMeans clustering.

    Parameters:
    vueltas_pilotos (DataFrame): A data frame with the laps of each driver.
    drivers_map (dict): A dictionary mapping driver names to ref a ID..
    """

    drivers = vueltas_pilotos["Driver"].drop_duplicates()

    # Seleccionamos las columnas que nos interesan para el análisis
    vueltas_pilotos = vueltas_pilotos[['Driver', 'Time', 'RPM', 'Speed', 'nGear', 'Throttle', 'Brake', 'DRS', 
                'Distance', 'RelativeDistance', 'X', 'Y', 'Z']]

    # Interpolar los datos para asegurar puntos de distancia compatibles
    # Crear un rango común de distancias
    distance_range = np.arange(
    0, 
    min([max(vueltas_pilotos[vueltas_pilotos["Driver"] == piloto]["Distance"]) 
            for piloto in drivers]), 
    10
    )

    # Convertimos las columnas de tiempo a segundos
    if pd.api.types.is_timedelta64_dtype(vueltas_pilotos['Time']):
        vueltas_pilotos['Time'] = vueltas_pilotos['Time'].dt.total_seconds()

    # Interpolar datos para cada piloto
    data = pd.DataFrame()
    for piloto in drivers:
        piloto_data = vueltas_pilotos[vueltas_pilotos["Driver"] == piloto].copy()
        interpolated_data = interpolate_telemetry(piloto_data, distance_range)
        
        for col in interpolated_data.columns:
            if col != 'Distance': 
                data[f'{col}_{piloto}'] = interpolated_data[col].values

    # Eliminamos valores string de las columnas Driver_DriverName
    for col in data.columns:
        if col.startswith('Driver_'):
            for piloto in drivers:
                if col.endswith(f'_{piloto}'):
                    data[col] = drivers_map[piloto]

    # Declaramos la varaible X
    X = data
    print(X.head())

    # Aplicamos el escalado a los datos
    sc_X = StandardScaler()
    X_sc = sc_X.fit_transform(data)

    # Aplicamos el algoritmo KMeans
    kmeans = KMeans(n_clusters=len(drivers), init="k-means++", n_init=10, max_iter=300, random_state=0)
    y_kmeans = kmeans.fit_predict(X_sc)

    return y_kmeans