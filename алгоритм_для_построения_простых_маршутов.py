import requests
import json
from itertools import product
# API-ключ для доступа к Яндекс.Расписаниям
API_KEY = "95e48825-709d-4296-952b-eed993562fd5"

# Функция для получения списка всех городов и их кодов
def get_cities_mapping():
    url = "https://api.rasp.yandex.net/v3.0/stations_list/"
    params = {
        "apikey": API_KEY,
        "format": "json",
        "lang": "ru_RU"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        cities_mapping = {}

        # Проходим по всем странам, регионам и населенным пунктам
        for country in data.get("countries", []):
            for region in country.get("regions", []):
                for settlement in region.get("settlements", []):
                    city_name = settlement.get("title")
                    city_code = settlement.get("codes", {}).get("yandex_code")
                    if city_name and city_code:
                        cities_mapping[city_name] = city_code

        return cities_mapping
    return None

# Функция для сохранения сопоставления городов и их кодов в JSON-файл
def save_cities_mapping(cities_mapping, filename="cities_mapping.json"):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(cities_mapping, file, indent=4, ensure_ascii=False)
    print(f"Сопоставление городов и их кодов сохранено в {filename}.")

# Основной код
if __name__ == "__main__":
    # Получаем список всех городов и их кодов
    cities_mapping = get_cities_mapping()
    # Сохраняем сопоставление городов и их кодов в JSON-файл
    save_cities_mapping(cities_mapping)

import requests
import json
from itertools import product

# Функция для получения списка всех станций в указанных городах
def get_stations_in_cities(data, city_codes):
    stations_in = []
    stations_out = []
    for country in data.get("countries", []):
        for region in country.get("regions", []):
            for settlement in region.get("settlements", []):
                if settlement.get("codes", {}).get("yandex_code") in city_codes:
                    for station in settlement.get("stations", []):
                        station_data = {
                            "code": station["codes"]["yandex_code"],
                            "title": station["title"]
                        }
                        # Разделяем станции на два списка
                        if settlement["codes"]["yandex_code"] == city_codes[0]:  # Первый город
                            stations_in.append(station_data)
                        elif settlement["codes"]["yandex_code"] == city_codes[1]:  # Второй город
                            stations_out.append(station_data)
    return stations_in, stations_out

# Функция для поиска расписания между двумя станциями
def get_schedule_between_stations(from_station, to_station, date):
    url_search = "https://api.rasp.yandex.net/v3.0/search/"
    params = {
        "apikey": "95e48825-709d-4296-952b-eed993562fd5",
        "lang": "ru_RU",
        "format": "json",
        "from": from_station,
        "to": to_station,
        "date": date  # Дата в формате "YYYY-MM-DD"
    }

    response = requests.get(url_search, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("segments"):  # Если есть расписание
            return data["segments"][0]["duration"]  # Возвращаем duration первого сегмента
    return None

# Основной код
if __name__ == "__main__":

    with open("cities_mapping.json", "r", encoding="utf-8") as file:
        cities_mapping = json.load(file)
    # Запрос списка всех станций
    url_stations_list = "https://api.rasp.yandex.net/v3.0/stations_list/"
    params_1 = {
        "apikey": "95e48825-709d-4296-952b-eed993562fd5",
        "lang": "ru_RU",
        "format": "json"
    }

    response_stations_list = requests.get(url_stations_list, params=params_1)
    if response_stations_list.status_code != 200:
        print("Ошибка при получении списка станций")
        exit()

    data_1 = response_stations_list.json()

    # Пользователь вводит названия городов
    city_names = input("Введите названия двух городов через пробел (например, Ульяновск Димитровград): ").split()
    if len(city_names) != 2:
        print("Необходимо ввести ровно два кода городов.")
        exit()

    city_codes = [cities_mapping.get(city) for city in city_names]

    # Получаем списки станций в указанных городах
    stations_in, stations_out = get_stations_in_cities(data_1, city_codes)
    if not stations_in or not stations_out:
        print("Станции в указанных городах не найдены.")
        exit()

    # Формируем уникальные пары станций
    unique_pairs = list(product(stations_in, stations_out))  # Декартово произведение

    # Пользователь вводит дату
    date = input("Введите дату в формате YYYY-MM-DD (например, 2025-03-28): ")

    # Словарь для сохранения результатов
    routes = {}

    # Проходим по всем уникальным парам станций
    for pair in unique_pairs:
        from_station = pair[0]["code"]
        to_station = pair[1]["code"]

        duration = get_schedule_between_stations(from_station, to_station, date)
        if duration:
            route_name = f"{pair[0]['title']} - {pair[1]['title']}"
            routes[route_name] = duration

    # Выводим результаты в удобном для чтения формате
    if routes:
        print("\nНайденные рейсы:")
        for route, duration in routes.items():
            hours = int(duration // 3600)  # Преобразуем часы в целое число
            minutes = int((duration % 3600) // 60)  # Преобразуем минуты в целое число
            print(f"{route}: {hours} ч {minutes} мин")
    else:
        print("Рейсов не найдено.")