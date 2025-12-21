from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNNoDataException
from obspy.core import UTCDateTime

import numpy as np
# import matplotlib.pyplot as plt  # если понадобится

client = Client("IRIS", timeout = 30)  # или "GFZ", в зависимости от того, что нужно

lat = 45.04
lon = 38.98

max_rad = 10

hourse_back = 6  # часы назад для проверки/скачивания данных

channel_patterns = ["BH*", "HH*", "EH*", "SH*"]

required_dir = 3  # минимум направлений с рабочими станциями


def distance(station):
    return np.sqrt((lat - station.latitude) ** 2 + (lon - station.longitude) ** 2)


def get_direction(station):
    stlat = station.latitude - lat
    stlon = station.longitude - lon

    if abs(stlat) > abs(stlon) and stlat > 0:
        return "N"
    elif abs(stlat) > abs(stlon) and stlat < 0:
        return "S"
    elif abs(stlon) > abs(stlat) and stlon > 0:
        return "E"
    elif abs(stlon) > abs(stlat) and stlon < 0:
        return "W"
    elif stlat > 0 and stlon > 0:
        return "NE"
    elif stlat > 0 and stlon < 0:
        return "NW"
    elif stlat < 0 and stlon > 0:
        return "SE"
    elif stlat < 0 and stlon < 0:
        return "SW"
    else:
        return None  # на всякий случай


def check_station(network, station):
    """
    Проверяем, есть ли у станции данные по любому из channel_patterns
    за последние hourse_back часов.
    """
    t_end = UTCDateTime.now()
    t_start = t_end - hourse_back * 3600

    # Если передали объект Station – берём его код
    if hasattr(station, "code"):
        station_code = station.code
    else:
        station_code = station

    for ch in channel_patterns:
        try:
            st = client.get_waveforms(
                network=network,
                station=station_code,
                location="*",
                channel=ch,
                starttime=t_start,
                endtime=t_end,
            )
            if len(st) > 0:
                return True
        except Exception:
            # Любая ошибка при запросе – пробуем следующий тип канала
            continue

    return False


def get_station_data(network, station, t_start, t_end):
    """
    Получаем реальные данные (Stream) по станции за заданный интервал времени.
    Перебираем channel_patterns, пока что-то не найдём.
    Возвращаем (stream, использованный_шаблон_канала) или (None, None).
    """
    if hasattr(station, "code"):
        station_code = station.code
    else:
        station_code = station

    for ch in channel_patterns:
        try:
            st = client.get_waveforms(
                network=network,
                station=station_code,
                location="*",
                channel=ch,
                starttime=t_start,
                endtime=t_end,
            )
            if len(st) > 0:
                return st, ch
        except Exception:
            continue

    return None, None


try:
    inv = client.get_stations(
        latitude=lat,
        longitude=lon,
        network="*",
        maxradius=max_rad,  # используем max_rad
        level="station",
    )

    arr_stations = []

    for net in inv:
        for st in net:
            arr_stations.append({
                "network": net.code,
                "station": st,              # сохраняем объект Station
                "distance": distance(st),
                "direction": get_direction(st),
            })

    # Словарь направлений
    directions = {
        "N": [], "S": [], "E": [], "W": [],
        "NE": [], "NW": [], "SE": [], "SW": []
    }

    # Раскладываем станции по направлениям
    for s in arr_stations:
        d = s["direction"]
        if d is not None:
            directions[d].append(s)

    # Сортируем станции в каждом направлении по расстоянию
    for d in directions:
        directions[d].sort(key=lambda x: x["distance"])

    # Печатаем по 2 ближайшие станции в каждом направлении
    order8 = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    for d in order8:
        print(f"\n{d} (станций: {len(directions[d])}):")
        for s in directions[d][:2]:
            sta = s["station"]
            print(
                f"  {s['network']}.{sta.code} — "
                f"{s['distance']:.2f}° "
                f"({sta.latitude:.2f}, {sta.longitude:.2f})"
            )

    # Ищем по одной "рабочей" станции в N, E, S, W
    best_stations = []
    order4 = ["N", "E", "S", "W"]

    for d in order4:
        cand = directions[d]
        if not cand:
            print(f"\nВ направлении {d} станций нет.")
            continue

        best = None
        for s in cand:
            if check_station(s["network"], s["station"]):
                best = s
                break

        if best is None:
            print(f"\nВ направлении {d} нет станций с доступными данными (каналы {channel_patterns}).")
            continue

        best_stations.append(best)
        sta = best["station"]
        print(
            f"\nЛучший кандидат в направлении {d}: "
            f"{best['network']}.{sta.code} — {best['distance']:.2f}°"
        )

    if len(best_stations) < required_dir:
        print(
            f"\nНедостаточно направлений с рабочими станциями: "
            f"найдено {len(best_stations)}, нужно минимум {required_dir}."
        )
    else:
        # Получаем данные по этим станциям за последние hourse_back часов
        t_end_data = UTCDateTime.now()
        t_start_data = t_end_data - hourse_back * 3600

        for s in best_stations:
            net = s["network"]
            sta_obj = s["station"]

            print(f"\nПолучаю данные для {net}.{sta_obj.code}...")

            st_data, used_ch = get_station_data(net, sta_obj, t_start_data, t_end_data)
            if st_data is None:
                print(f"  Не удалось получить данные по каналам {channel_patterns}")
                continue

            print(f"  Получены данные, канал {used_ch}, трасс: {len(st_data)}")

            # Простой вывод графика (ObsPy сам использует matplotlib)
            st_data.plot(
                type="relative",
                title=f"{net}.{sta_obj.code} {used_ch}"
            )

except FDSNNoDataException:
    print("У данного FDSN-провайдера нет станций в радиусе 3° от этих координат.")