criminal_vehicles = [
    "HR26DK1234",
    "DL8CAF1234",
    "UP32AB1234"
]

# def check_vehicle(number):
#     if number in criminal_vehicles:
#         return True
#     return False

def check_vehicle(number):
    number = number.strip().upper()
    return number in criminal_vehicles