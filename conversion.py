import os
from collections import deque
from PS103J2_table import *

def convertTempString(filename):
    # Directorios de entrada/salida (ajusta según tu configuración)
    infile = filename + ".txt"
    outfile = "temp_string.txt"
    tempfile = "temp_string.tmp"
    convert_log_file = "convertion_log.txt"
    
    # Función de conversión de ADC a temperatura
    def adc_to_temperature(adc_value):
        RNTC = (adc_value * 20000) / (4096 - adc_value)
        # Conversión usando la tabla PS103J2_temp_array (ajusta según tu método)
        return PS103J2_temp_array[closest(PS103J2_array, RNTC)]
    
    try:
        # Leer archivo de entrada y preparar archivos de salida
        with open(infile, "r") as inf, open(outfile, "a+") as outf,\
            open(tempfile, "a+") as temp, open(convert_log_file, "a+") as conv_log:
            
            for line in inf:
                line = line.strip()
                # Saltar líneas vacías
                if not line:
                    continue
                
                # Extraer timestamp
                timestamp = line.split()[0].strip(":")
                outf.write(f"{timestamp}")
                temp.write(f"{timestamp}")
                
                # Recorre cada esclavo y convierte temperatura
                #for i in range(1, 18):  # Asumiendo 17 esclavos
                # Obtener valor de ADC
                temp_line = line.split("=")
                adc_value = int(temp_line[1].strip())
                
                if adc_value != 4444:  # Valor 4444 indica error
                    air_temp_C = adc_to_temperature(adc_value)
                    
                    # Control de valores fuera de rango
                    if air_temp_C < 0 or air_temp_C > 39:
                        conv_log.write(f"{timestamp}\t{air_temp_C}\tconvertTempString fuera de rango\n")
                        air_temp_C = 0
                else:
                    conv_log.write(f"{timestamp}\tconvertTempString 4444\n")
                    air_temp_C = 0
                
                # Escribir valores de temperatura en °C
                outf.write(f" {air_temp_C:.2f}")
                temp.write(f" {air_temp_C:.2f}")
                
                outf.write("\n")
                temp.write("\n")
        
        # Cerrar archivos
        inf.close()
        outf.close()
        temp.close()
        conv_log.close()

    except IOError:
        print(f"No existe el archivo {infile}")
