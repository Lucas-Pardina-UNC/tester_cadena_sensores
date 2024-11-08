import re

def parse_time_input(time_str: str) -> int:
    days, hours, minutes, seconds = map(int, time_str.split(":"))
    return days * 86400 + hours * 3600 + minutes * 60 + seconds

def validate_time_input(prompt: str) -> str:
    while True:
        time_input = input(prompt)
        # Regular expression for matching format "DD:HH:MM:SS"
        if re.match(r"^\d+:\d{2}:\d{2}:\d{2}$", time_input):
            return time_input
        else:
            print("Formato inválido. Por favor ingrese el tiempo en el formato 'DD:HH:MM:SS'.")
