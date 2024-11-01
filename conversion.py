import os
from collections import deque
from PS103J2_table import *

# Función de conversión de ADC a temperatura
def adc_to_temperature(adc_value):
    RNTC = (adc_value * 20000) / (4096 - adc_value)
    # Conversión usando la tabla PS103J2_temp_array (ajusta según tu método)
    return PS103J2_temp_array[closest(PS103J2_array, RNTC)]