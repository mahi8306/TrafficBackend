# services/traffic_engine.py

def calculate_signal_times(lanes):
    total = sum(lanes)

    timings = []
    for lane in lanes:
        if total == 0:
            timings.append(10)
        else:
            timings.append(int((lane / total) * 60))

    return timings