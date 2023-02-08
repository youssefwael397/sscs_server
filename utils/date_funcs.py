from datetime import datetime

def current_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
