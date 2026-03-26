# services/corridor.py

def green_corridor(route_lanes):
    signals = {}

    for lane in range(4):
        if lane in route_lanes:
            signals[lane] = "GREEN"
        else:
            signals[lane] = "RED"

    return signals