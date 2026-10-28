from parser import Parser
import time
import logging
from functools import wraps

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("parser.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def time_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"Вызываемая функция: '{func.__name__}' | Время выполнения: {end_time - start_time:.2f} сек.")
        return result
    return wrapper

@time_logger
def main():
    parser = Parser('https://mile.by/catalog/799-elektroobogrevateli/obogrevatel-elektricheskiy/')
    try:
        while True:
            time.sleep(5)
            parser.get_links_on_page()
            print(len(parser.links_list))
            time.sleep(5)
            parser.go_to_the_next_page()

    except Exception as e:
        print(e)

    parser.get_info()
    print(parser.info_list)
    parser.creating_csv_file()


if __name__ == "__main__":
    main()