from datetime import datetime


def current_datetime():
    formatted_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    return formatted_date


