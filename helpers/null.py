import pandas as pd
import numpy as np

def reemplazar_null_por_nulos(archivo_entrada, archivo_salida=None):
    """
    Reemplaza todas las ocurrencias de la cadena "NULL" en un archivo CSV por valores nulos reales (NaN)
    
    Args:
        archivo_entrada (str): Ruta al archivo CSV de entrada
        archivo_salida (str, optional): Ruta para guardar el archivo procesado. 
                                        Si no se proporciona, se sobrescribirá el archivo original.
    
    Returns:
        pandas.DataFrame: El DataFrame con los valores NULL reemplazados
    """
    # Si no se proporciona archivo de salida, sobrescribir el original
    if archivo_salida is None:
        archivo_salida = archivo_entrada
    
    # Leer el archivo CSV
    print(f"Leyendo archivo: {archivo_entrada}")
    df = pd.read_csv(archivo_entrada, sep=';')
    
    # Contar el número de valores "NULL" antes del reemplazo
    null_count_before = (df == "NULL").sum().sum()
    print(f"Número de valores 'NULL' encontrados: {null_count_before}")
    
    # Reemplazar "NULL" por valores nulos (NaN)
    df.replace("NULL", np.nan, inplace=True)
    
    # Verificar que se hayan reemplazado todos los "NULL"
    null_string_count_after = (df == "NULL").sum().sum()
    print(f"Valores 'NULL' restantes después del reemplazo: {null_string_count_after}")
    print(f"Valores nulos (NaN) en el DataFrame: {df.isna().sum().sum()}")
    
    # Guardar el resultado
    df.to_csv(archivo_salida, sep=';', index=False)
    print(f"Archivo guardado como: {archivo_salida}")
    
    return df

if __name__ == "__main__":
    import sys
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python script.py archivo_entrada.csv [archivo_salida.csv]")
        sys.exit(1)
    
    # Obtener nombre del archivo de entrada
    archivo_entrada = sys.argv[1]
    
    # Obtener nombre del archivo de salida (opcional)
    archivo_salida = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Ejecutar la función principal
    reemplazar_null_por_nulos(archivo_entrada, archivo_salida)