from pycbrf import ExchangeRates
import datetime

rates = ExchangeRates(str(datetime.datetime.now())[:10])

# Метод получения курса по отношению к рублю
def TO_RUB(value: str):
    return list(filter(lambda el: el.code == value, rates.rates))[0].rate