import json
import requests

FAVORITE_CURRENCIES = ["USD", "EUR", "GBP", "RUB"]
DATA_FILE = "currency_rate.json"

def get_currency_rate(currency_code: str) -> dict:
    """
    Получает актуальные курсы валют относительно указанной валюты из API.
    """
    URL = f"https://open.er-api.com/v6/latest/{currency_code}"
    try:
        response = requests.get(URL, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка при запросе к API: статус {response.status_code}")
            return None
    except Exception as e:
        print(f"Ошибка подключения к сети: {e}")
        return None

def save_to_file(data: dict):
    """
    Сохраняет данные в файл currency_rate.json.
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    except OSError as e:
        print(f"Ошибка при сохранении файла: {e}")

def update_currency_rates():
    """
    Обновляет курсы для избранных базовых валют и сохраняет их в файл.
    Если API недоступно для всех валют, мы пытаемся сохранить хотя бы одну.
    """
    all_data = {}
    print("Обновление курсов валют через API...")
    for currency in FAVORITE_CURRENCIES:
        data = get_currency_rate(currency)
        if data:
            all_data[currency] = data
    if all_data:
        save_to_file(all_data)
        print("Данные успешно сохранены в currency_rate.json")
    else:
        print("Не удалось получить данные ни для одной валюты.")

def read_from_file() -> dict:
    """
    Читает данные из файла currency_rate.json.
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print("Файл currency_rate.json поврежден.")
        return None

def extract_rates(data: dict) -> dict:
    """
    Извлекает блок 'rates' или 'conversion_rates' из загруженных данных.
    Поддерживает как плоскую структуру (один ответ API), так и вложенную.
    """
    if not isinstance(data, dict):
        return None
    
    # 1. Если rates или conversion_rates находятся на верхнем уровне
    if "rates" in data:
        return data["rates"]
    if "conversion_rates" in data:
        return data["conversion_rates"]
    
    # 2. Если структура вложенная (ключи - валюты, значения - ответы API)
    for key, val in data.items():
        if isinstance(val, dict):
            if "rates" in val:
                return val["rates"]
            if "conversion_rates" in val:
                return val["conversion_rates"]
                
    return None

def calculate_cross_rate(rates: dict, src: str, tgt: str) -> float:
    """
    Вычисляет кросс-курс валюты SRC к TGT через базовую валюту.
    """
    src_rate = rates.get(src)
    tgt_rate = rates.get(tgt)
    
    if src_rate is None or tgt_rate is None:
        return None
        
    if src_rate <= 0 or tgt_rate <= 0:
        return None
        
    # Формула кросс-курса:
    # 1 SRC = (1 / src_rate) * tgt_rate TGT
    return tgt_rate / src_rate

def print_currency_list(rates: dict):
    """
    Красиво выводит список доступных валют.
    """
    currencies = sorted(list(rates.keys()))
    print(f"\nДоступно валют: {len(currencies)}")
    # Выводим по 10 штук в строку
    for i in range(0, len(currencies), 10):
        print("  " + ", ".join(currencies[i:i+10]))

def main():
    print("=========================================")
    print("      КОНВЕРТЕР ВАЛЮТ (CLI)              ")
    print("=========================================")
    
    # Загружаем данные из файла
    data = read_from_file()
    
    # Если файла нет, пробуем обновить/скачать данные
    if data is None:
        print("Локальный файл курсов валют не найден.")
        update_currency_rates()
        data = read_from_file()
        if data is None:
            print("Не удалось инициализировать базу курсов валют. Проверьте подключение к сети.")
            return

    while True:
        # Извлекаем курсы при каждой итерации (на случай обновления)
        rates = extract_rates(data)
        if not rates:
            print("Ошибка: не удалось извлечь курсы валют из файла.")
            # Попробуем обновить
            update_currency_rates()
            data = read_from_file()
            rates = extract_rates(data)
            if not rates:
                print("Завершение работы из-за некорректного формата файла.")
                return

        print("\nМеню:")
        print("1. Конвертация валюты")
        print("2. Показать список доступных валют")
        print("3. Обновить курсы валют через API")
        print("4. Выход")
        
        try:
            choice = input("\nВыберите действие (1-4): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nВыход из программы...")
            break
            
        if choice == "1":
            print("\n--- Режим Конвертации ---")
            try:
                src = input("Введите исходную валюту (например, USD): ").strip().upper()
                if not src:
                    print("Ошибка: код исходной валюты не может быть пустым.")
                    continue
                if src not in rates:
                    print(f"Ошибка: валюта '{src}' отсутствует в списке доступных.")
                    continue
                    
                tgt = input("Введите целевую валюту (например, EUR): ").strip().upper()
                if not tgt:
                    print("Ошибка: код целевой валюты не может быть пустым.")
                    continue
                if tgt not in rates:
                    print(f"Ошибка: валюта '{tgt}' отсутствует в списке доступных.")
                    continue
                    
                amount_str = input("Введите сумму для конвертации: ").strip()
                if not amount_str:
                    print("Ошибка: сумма не может быть пустой.")
                    continue
                    
                # Поддержка запятой в качестве разделителя
                amount = float(amount_str.replace(",", "."))
                if amount < 0:
                    print("Ошибка: сумма должна быть неотрицательной.")
                    continue
                    
            except ValueError:
                print("Ошибка: введено не число.")
                continue
            except (KeyboardInterrupt, EOFError):
                print("\nОперация отменена.")
                continue
                
            cross_rate = calculate_cross_rate(rates, src, tgt)
            if cross_rate is None:
                print("Ошибка при расчете кросс-курса (некорректные данные в файле).")
            else:
                result = amount * cross_rate
                print("\n-----------------------------------------")
                print(f"Результат: {amount:,.2f} {src} = {result:,.2f} {tgt}")
                print(f"Курс: 1 {src} = {cross_rate:.6f} {tgt}")
                print("-----------------------------------------")
                
        elif choice == "2":
            print_currency_list(rates)
            
        elif choice == "3":
            update_currency_rates()
            data = read_from_file()
            
        elif choice == "4":
            print("Выход. Спасибо за использование!")
            break
        else:
            print("Некорректный выбор. Введите число от 1 до 4.")

if __name__ == "__main__":
    main()
