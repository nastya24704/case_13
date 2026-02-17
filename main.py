import datetime
import math
import random
from typing import Dict, Optional, Any
import local as lcl


def get_information(initial_data: str) -> Dict[int, Dict[str, Any]]:
    """
    The function for reading information about automates from a file
    and creating a dictionary with column data.

    Args:
        initial_data (str): Path to the file containing automate data.

    Returns:
        Dict[int, Dict[str, Any]]: A dictionary where keys are automate numbers
         and values are dictionaries containing:
            - 'max_queue' (int): maximum queue length
            - 'brands' (List[str]): list of supported fuel brands
            - 'queue' (int): current queue length
            - 'previous_time' (datetime.datetime): the end time of the previous customer's service
            - 'current_client' (Optional[Any]): information about the current client
    """

    automates = {}
    try:
        with open(initial_data, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, start=1):
                stripped_line = line.strip()
                if not stripped_line:
                    continue

                parts = stripped_line.split()

                if len(parts) < 3:
                    print(f"Warning: {lcl.LINE} {line_num} {lcl.SKIPPEDD_LINE} {stripped_line}")
                    continue

                try:
                    num = int(parts[0])
                    max_queue = int(parts[1])
                    brands = parts[2:]
                except ValueError as ve:
                    print(f"Warning: {lcl.LINE} {line_num} {CONVERSION_ERROR} {ve}")
                    continue

                automates[num] = {
                    'max_queue': max_queue,
                    'brands': brands,
                    'queue': 0,
                    'previous_time': datetime.datetime.strptime('00:00', '%H:%M'),
                    'current_client': None
                }
    except FileNotFoundError:
        print(f"Error: {lcl.FILE} '{initial_data}' {lcl.FILE_NOT_FOUND}")
    except Exception as e:
        print(f"Error: {lcl.UNEXPECTED_ERROR } {e}")

    return automates


def get_request(line: str) -> Optional[Dict[str, Any]]:
    """
    The function converts the query string into a dictionary with the customer data.

    Args:
        line (str): A string containing time, volume, and brand information.

    Returns:
        Optional[Dict[str, Any]]: Dictionary with keys:
            - 'time' (datetime.datetime): client's arrival time
            - 'volume' (int): the requested volume of fuel in liters
            - 'brand' (str): fuel brand
        Or None in case of a parsing error.
    """

    try:
        parts = line.strip().split()
        if len(parts) != 3:
            print(f"Warning: {lcl.BAD_REQUEST_FORMAT} {line.strip()}")
            return None

        time_str, volume_str, brand = parts
        time = datetime.datetime.strptime(time_str, '%H:%M')
        volume = int(volume_str)

        return {
            'time': time,
            'volume': volume,
            'brand': brand
        }
    except ValueError as e:
        print(f"Warning: {lcl.REQUEST_TRANSFORM_ERROR} {e} — {lcl.LINE}: {line.strip()}")
        return None


def suitable_automates(request: Dict[str, Any], automates: Dict[int, Dict[str, Any]])\
        -> Dict[int, Dict[str, Any]]:
    """
    The function searches for a suitable automate that support the requested brand.

    Args:
        request: A dictionary with query data containing the key 'brand'.
        automates: A dictionary with the data of all automata.
    Returns:
        Dict[int, Dict[str, Any]]: Dictionary of suitable automata,
        where the keys are the numbers of the automata, and the values are their parameters.
    """

    brand = request.get('brand')
    if brand is None:
        print("Warning: {lcl.KEY_MISSING} 'brand'")
        return {}

    return {num: automates[num] for num in automates if brand in automates[num]['brands']}


def automate_num(suitable: Dict[int, Dict[str, Any]]) -> int:
    """
    The function selects automate with the shortest queue, not exceeding the maximum.

    Args:
        suitable: A dictionary of suitable automates.

    Returns:
        int: The number of the selected machine, or 0 if there are no suitable machines.
    """

    if not suitable:
        return 0

    available = {num: data for num, data in suitable.items()
                 if data['queue'] < data['max_queue']}

    if not available:
        return 0

    return min(available.keys(), key=lambda x: available[x]['queue'])


def refuel_time(volume: int) -> int:
    """
    The function calculates the refueling time based on the requested volume.

    Args:
        volume (int): The volume of fuel in liters.

    Returns:
        int: Estimated refueling time in minutes (minimum 1 minute).
    """

    base_time = math.ceil(volume / 10)

    variation = random.choice([-1, 0, 1])

    return max(1, base_time + variation)


def print_automates_state(automates: Dict[int, Dict[str, Any]]) -> None:
    """
    The function prints the current state of all automates.
    Displays for each vending machine its number and the maximum queue length.,
    supported fuel brands and the current queue in the form of stars.

    Args:
        automates: A dictionary with the data of all automata.

    Returns:
        None: The function don't return anything, only outputs information to the console.
    """

    for num in sorted(automates.keys()):
        automate = automates[num]
        queue_display = '*' * automate['queue']
        print(f'{lcl.AUTOMATE_NUMBER}{num} {lcl.MAX_QUEUE_LENGTH}: {automate["max_queue"]} '
              f'{lcl.GASOLINE_BRANDS}: {" ".join(automate["brands"])} '
              f'->{queue_display}')


def calculate_lost_profit(petrol_prices:  Dict[str, float],
                          fuel_sold_by_brand:  Dict[str, int],
                          lost_clients_by_brand:  Dict[str, int]) -> None:
    """
    The function calculates and analyzes lost profit and recommends a new fuel column.

    Args:
        petrol_prices: Dictionary of fuel prices by brand.
        fuel_sold_by_brand: A dictionary with volumes of fuel sold by brand.
        lost_clients_by_brand: A dictionary with the number of lost customers by brand.

    Returns:
        None: The function don't return anything, only outputs information to the console.
    """
    print(f"\n{'~' * 60}")
    print(f"{lcl.ANALYSIS_ADDITIONAL_RENTABILITY}")
    print(f"{'~' * 60}")

    print("f\n{lcl.LOST_CLIENTS_BY_BRANDS}}")
    total_lost_volume = 0
    total_lost_revenue = 0

    for brand in sorted(petrol_prices.keys()):
        lost_count = lost_clients_by_brand.get(brand, 0)
        if lost_count > 0:
            if fuel_sold_by_brand[brand] > 0:
                avg_volume = fuel_sold_by_brand[brand] / max(1, sum(fuel_sold_by_brand.values()))
            else:
                avg_volume = 30

            lost_volume = lost_count * avg_volume
            lost_revenue = lost_volume * petrol_prices[brand]

            total_lost_volume += lost_volume
            total_lost_revenue += lost_revenue

            print(f"  {brand}: {lost_count} {lcl.CLIENTS} "
                  f"{lcl.LOST} ~{lost_volume:.1f} {lcl.LITERS} "
                  f"{lcl.LOST_REVENUE} ~{lost_revenue:.2f} {lcl.RUBLES}")

    print(f"\n{lcl.TOTAL_REVENUE} {total_lost_volume:.1f} {lcl.LITERS} "
          f"{lcl.LOST_REVENUE} {total_lost_revenue:.2f} {lcl.RUBLES}")

    print(f"\n{lcl.ANALYZE_NEW_COLUMN}")

    if lost_clients_by_brand:
        most_lost_brand = max(lost_clients_by_brand.items(),
                              key=lambda x: x[1])[0]

        print(f"{lcl.HIGHEST_LOST_CLENTS} {most_lost_brand}")
        print(f"{lcl.RECOMMEND_INSTALLATION} {most_lost_brand}")

        monthly_lost_revenue = total_lost_revenue * 30
        column_cost = 1700000
        months_to_payback = column_cost / monthly_lost_revenue if monthly_lost_revenue > 0 else float('inf')

        print(f"\n{lcl.EVALUATION_RENTABILITY}")
        print(f"{lcl.MONTHLY_LOSS_BENEFIT} {monthly_lost_revenue:,.0f} {lcl.RUBLES}")
        print(f"{lcl.APPROXIMATE_COST_COLUMN} {column_cost:,.0f} {lcl.RUBLES}")

        if months_to_payback <= 12:
            print(f"{lcl.PAYBACK_PERIOD} {months_to_payback:.1f} {lcl.MONTHS} {lcl.PROFITABLE}")
        elif months_to_payback <= 24:
            print(f"{lcl.PAYBACK_PERIOD} {months_to_payback:.1f} {lcl.MONTHS} {lcl.MODERATELY_PROFITABLE}")
        else:
            print(f"{lcl.PAYBACK_PERIOD} {months_to_payback:.1f} {lcl.MONTHS} {lcl.UNPROFITABLE}")
    else:
        print(f"{lcl.NO_ADDITIONAL_CLIENTS}")


def main() -> None:
    """
    The main function of the program is to simulate the operation of a gas station.

    The function performs the following tasks:
    - Downloads fuel column data from a file 'azs_data.txt '
    - Downloads the client stream from a file 'input.txt '
    - Simulates the customer service process based on queues
    - Maintains statistics on sales and lost customers
    - Outputs  results and profitability analysis

    Returns:
        None
    """

    petrol_prices = {'АИ-80': 38.0, 'АИ-92': 60.5, 'АИ-95': 65.0, 'АИ-98': 82.3}

    fuel_sold = {'АИ-80': 0, 'АИ-92': 0, 'АИ-95': 0, 'АИ-98': 0}
    total_revenue = 0
    lost_clients = 0
    lost_clients_by_brand = {'АИ-80': 0, 'АИ-92': 0, 'АИ-95': 0, 'АИ-98': 0}

    automates = get_information('azs_data.txt')

    finish_events = {}

    with open('input.txt', 'r', encoding='utf-8') as requests_file:
        all_requests = [get_request(line) for line in requests_file if line.strip()]

    all_requests.sort(key=lambda x: x['time'])

    for request in all_requests:
        current_time = request['time']

        while finish_events and min(finish_events.keys()) <= current_time:
            finish_time = min(finish_events.keys())
            finish_info = finish_events[finish_time]

            print(f'\nВ {finish_time.strftime("%H:%M")} {lcl.CLIENT} {finish_info["arrival_time"].strftime("%H:%M")} '
                  f'{finish_info["brand"]} {finish_info["volume"]} {finish_info["duration"]} '
                  f'{lcl.FINISHED_REFUELING}')

            automate = automates[finish_info['num']]
            automate['queue'] -= 1
            automate['previous_time'] = finish_time
            automate['current_client'] = None

            del finish_events[finish_time]

            print_automates_state(automates)

        suitable = suitable_automates(request, automates)
        chosen_num = automate_num(suitable)

        if not chosen_num:
            lost_clients += 1
            lost_clients_by_brand[request['brand']] += 1
            print(f'\nВ {request["time"].strftime("%H:%M")} {lcl.CLIENT_LEFT} {request["brand"]} '
                  f'{lcl.CLIENT_LEFT_STATION}')
            print_automates_state(automates)
        else:
            duration = refuel_time(request['volume'])

            automates[chosen_num]['queue'] += 1

            print(f'\nВ {request["time"].strftime("%H:%M")} {lcl.NEW_CLIENT}: '
                  f'{request["time"].strftime("%H:%M")} {request["brand"]} {request["volume"]} {duration} '
                  f'{lcl.CLIENT_QUEUED}{chosen_num}')

            print_automates_state(automates)

            previous_finish = automates[chosen_num]['previous_time']
            start_time = max(previous_finish, request['time'])
            finish_time = start_time + datetime.timedelta(minutes=duration)

            finish_events[finish_time] = {
                'num': chosen_num,
                'arrival_time': request['time'],
                'brand': request['brand'],
                'volume': request['volume'],
                'duration': duration
            }

            fuel_sold[request['brand']] += request['volume']
            total_revenue += request['volume'] * petrol_prices[request['brand']]

    while finish_events:
        finish_time = min(finish_events.keys())
        finish_info = finish_events[finish_time]

        print(f'\nВ {finish_time.strftime("%H:%M")} {lcl.CLIENT} {finish_info["arrival_time"].strftime("%H:%M")} '
              f'{finish_info["brand"]} {finish_info["volume"]} {finish_info["duration"]} '
              f'{lcl.FINISHED_REFUELING}')

        automates[finish_info['num']]['queue'] -= 1
        automates[finish_info['num']]['previous_time'] = finish_time
        automates[finish_info['num']]['current_client'] = None

        del finish_events[finish_time]

        print_automates_state(automates)

    print(f'\n{"~" * 60}')
    print(f'{lcl.GASOLINE_SOLD}:')
    for brand in sorted(fuel_sold.keys()):
        print(f'  {brand}: {fuel_sold[brand]} л')

    print(f'\n{lcl.GASOLINE_SOLD_FINALL}: {sum(fuel_sold.values())} л')
    print(f'{lcl.REVENUE}: {total_revenue:.2f} {lcl.RUBLES}')
    print(f'{lcl.LOST_CLIENTS}: {lost_clients}')

    calculate_lost_profit(petrol_prices, fuel_sold, lost_clients_by_brand)


if __name__ == '__main__':
    main()
