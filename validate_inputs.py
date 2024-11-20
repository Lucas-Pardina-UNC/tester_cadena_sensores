#from typing import List

def validate_two_options(message: str = "") -> str:
    while True:
        menu_option = input(f"{message}")
        if menu_option in ('1', '2'):
            return menu_option
        else:
            print("Entrada inválida. Por favor, ingrese '1' o '2'.")

def validate_three_options(message: str = "") -> str:
    while True:
        menu_option = input(f"{message}")
        if menu_option in ('1', '2', '3'):
            return menu_option
        else:
            print("Entrada inválida. Por favor, ingrese '1', '2' o '3'.")

def validate_four_options(message: str = "") -> str:
    while True:
        menu_option = input(f"{message}")
        if menu_option in ('1', '2', '3', '4'):
            return menu_option
        else:
            print("Entrada inválida. Por favor, ingrese '1', '2', '3' o '4'.")

def validate_list_options(items: list, message: str = "") -> str:
    while True:
        user_input = input(f"{message}")
        if user_input.isdigit():
            option = int(user_input)
            if 1 <= option <= len(items):
                return user_input
            else:
                print(f"Entrada inválida. Por favor, ingrese un número entre 1 y {len(items)}.")
        else:
            print("Entrada inválida. Por favor, ingrese un número.")
