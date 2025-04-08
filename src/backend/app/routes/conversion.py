import struct
from typing import Union
from .PS103J2_table import *

# Función de conversión de ADC a temperatura
def adc_to_temperature(adc_value):
    if(adc_value != 4444):
        RNTC = (adc_value * 20000) / (4096 - adc_value)
        # Conversión usando la tabla PS103J2_temp_array (ajusta según tu método)
        return PS103J2_temp_array[closest(PS103J2_array, RNTC)]
    else:
        return 4444

# Función de conversión de ADC a temperatura
def adc_to_humidity(adc_value):
    if(adc_value != 4444):
        air_hum_C = (adc_value/65536)*100
        return air_hum_C
    else:
        return 4444

def adc_to_wind_direction(adc_value):
    wind_dir_mV = adc_value/4096.0

    if(adc_value != 4444):
        if((wind_dir_mV - 20.0) < 0):
            wind_dir = 360.0 + (wind_dir_mV-20.0)
        else:
            wind_dir = wind_dir_mV-20.0
    else:
        wind_dir = 0

    return wind_dir

def adc_to_wind_speed(adc_value):
    if(adc_value != 4444):
        wind_speed_ms = adc_value * (50/250)
        wind_speed_Kmh = wind_speed_ms * 3.6
    else:
        wind_speed_Kmh = 0

    return wind_speed_Kmh    

def adc_to_direct_radiation(adc_value):
    if(adc_value != 4444):
        direct_radiation = (adc_value - 368) * 0.42
    else:
        direct_radiation = 0

    return direct_radiation

def adc_to_net_radiation(adc_value):
    if(adc_value != 4444 and adc_value > 2000 and adc_value < 4000):
        net_radiation = ((((adc_value/4096)*4096)-2541)/100)/0.013
    else:
        net_radiation = 0

    return net_radiation

def adc_to_air_pressure(adc_value_temp_comp, adc_value_pressure, coefficients):
    [dig_t1, dig_t2, dig_t3, dig_p1, dig_p2, dig_p3, dig_p4, dig_p5, dig_p6, dig_p7, dig_p8, dig_p9] = coefficients
    
    raw_temperature = float(adc_value_temp_comp)
    raw_pressure = float(adc_value_pressure)
    
    if(raw_pressure != 4444):
        # TEMPERATURA
        var1 = (raw_temperature / 16384.0 - dig_t1 / 1024.0) * dig_t2
        var2 = raw_temperature / 131072.0 - dig_t1 / 8192.0
        var2 = var2 * var2 * dig_t3
        temperature_fine = (var1 + var2)
        temp_degC = temperature_fine / 5120.0
        air_temperature = temp_degC
        # PRESION
        var1 = temperature_fine / 2.0 - 64000.0
        var2 = var1 * var1 * dig_p6 / 32768.0
        var2 = var2 + var1 * dig_p5 * 2
        var2 = var2 / 4.0 + dig_p4 * 65536.0
        var1 = (dig_p3 * var1 * var1 / 524288.0 + dig_p2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * dig_p1
        pressure = 1048576.0 - raw_pressure
        pressure = (pressure - var2 / 4096.0) * 6250.0 / var1
        var1 = dig_p9 * pressure * pressure / 2147483648.0
        var2 = pressure * dig_p8 / 32768.0
        pressure_Pa = pressure + (var1 + var2 + dig_p7) / 16.0
        pressure_Pa = pressure_Pa / 100
        air_pressure = pressure_Pa
    else:
        air_temperature = 0
        air_pressure = 0

    return air_pressure

def adc_to_energy_current_value(adc_value):
    if adc_value < 35534:
        i_energy_value = adc_value / 10.0
        i_energy_value = round(i_energy_value, 3)  # Limit to 3 decimal digits
    else:
        i_energy_value = 4444

    return i_energy_value

def adc_to_energy_voltage_value(adc_value):
    if adc_value < 35534:
        v_energy_value = adc_value * 0.004
        v_energy_value = round(v_energy_value, 3)  # Limit to 3 decimal digits
    else:
        v_energy_value = 4444

    return v_energy_value

# ----------------------------------- Sonda -----------------------------------
def adc_to_pH_value(adc_value):
    pH_hex = adc_value
    pH_value = struct.unpack('!f', bytes.fromhex(pH_hex))[0]

    if (pH_value < 0.0 or pH_value > 14.0):
        pH_value = 0

    return pH_value

def adc_to_pHORP_value(adc_value):
    pHORP_hex = adc_value
    pHORP_value = struct.unpack('!f', bytes.fromhex(pHORP_hex))[0]
    pHORP_value = '%.2f'%(pHORP_value)

    # Validar???

    return pHORP_value

def adc_to_OD_temp(adc_value):
    temp_hex = adc_value
    temp_value = struct.unpack('!f', bytes.fromhex(temp_hex))[0]
    temp_value = '%.2f'%(temp_value)

    return temp_value 

def adc_to_OD_value(adc_value):
    OD_hex = adc_value
    OD_value = struct.unpack('!f', bytes.fromhex(OD_hex))[0]

    if (OD_value < 0.0 or OD_value > 100.0):
        OD_value = 0

    return OD_value 

def adc_to_ODmgL_Value(adc_value):
    ODmgL_hex = adc_value
    ODmgL_value = struct.unpack('!f', bytes.fromhex(ODmgL_hex))[0]
    ODmgL_value = '%.2f'%(ODmgL_value)

    return ODmgL_value

def adc_to_ODPPM_Value(adc_value):
    ODPPM_hex = adc_value
    ODPPM_value = struct.unpack('!f', bytes.fromhex(ODPPM_hex))[0]
    ODPPM_value = '%.2f'%(ODPPM_value)

    return ODPPM_value

# Algas
def adc_to_phycocyanin_value(algae_fields):
    Phycocyanin_value = 0.0
    try:
        Phycocyanin_value = float(algae_fields[1].lstrip("0"))
    except:
        print("convert_algae except",flush=True)
        Phycocyanin_value = 0.0

    return Phycocyanin_value

def adc_to_chlorophyll_value(algae_fields):
    try:
        chlA_value = float(algae_fields[0].lstrip("0"))
    except:
        print("convert_algae except",flush=True)
        chlA_value = 0.0

    return chlA_value

def adc_to_turbidity_value(algae_fields):
    try:
        turbidity_value = float(algae_fields[2].lstrip("0"))
    except:
        print("convert_algae except",flush=True)
        turbidity_value = 0.0

    return turbidity_value
# ----------------------------------- \Sonda -----------------------------------

def get_sensor_type(sensor_id: Union[str, int]) -> str:
    sensor_type_map = {
        100 : "Energy",                
        200 : "Air",                  
        400 : "Radiation",            
        500 : "Anemometer",            
        900 : "Temperature",     
        999 : "Temperature",     
        1000 : "Probe",               
        # ----------------------- Energy Board (100 equivalent) -----------------------
        'EP' : "Energy (Panel)",  # Panel          
        'EB' : "Energy (Battery)",  # Battery
        'EC' : "Energy (Consumption)",  # Consumption
        # ----------------------- Air Sensors (200 equivalent)-------------------------
        'HU' : "Humidity",
        'PE' : "Pressure",
        'PA' : "Pressure",
        'TE' : "Temperature",  # Temperature chain (900, 999 equivalent)
        # -------------------- Radiation Sensor (400 equivalent)-----------------------
        'RD': "Direct Radiation",
        'RN': "Net Radiation",
        # ------------------------ Anemometer (500 equivalent)--------------------------
        'WD': "Wind Direction",
        'WS': "Wind Speed",
    }

    return sensor_type_map.get(sensor_id, "Unidentified Sensor")

