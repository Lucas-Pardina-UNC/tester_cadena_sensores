

def validate_two_options(message = ""):
    while True:
            menu_option = input(f"{message}")
            if menu_option in ('1', '2'):
                return menu_option
            else:
                print("Invalid input. Please enter '1' or '2'.")

def validate_three_options(message = ""):
    while True:
            menu_option = input(f"{message}")
            if menu_option in ('1', '2', '3'):
                return menu_option
            else:
                print("Invalid input. Please enter '1', '2' or '3'.")

def validate_four_options(message = ""):
    while True:
            menu_option = input(f"{message}")
            if menu_option in ('1', '2', '3', '4'):
                return menu_option
            else:
                print("Invalid input. Please enter '1', '2', '3' or '4'.")

def validate_list_options(items, message=""):
    while True:
        user_input = input(f"{message}")
        if user_input.isdigit():
            option = int(user_input)
            if 1 <= option <= len(items):
                return user_input
            else:
                print(f"Invalid input. Please enter a number between 1 and {len(items)}.")
        else:
            print("Invalid input. Please enter a number.")

     