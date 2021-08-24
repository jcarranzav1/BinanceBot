from binance.client import Client
from binance import ThreadedWebsocketManager, BinanceSocketManager, AsyncClient
import configparser


def Connection(account: bool = True):
    config = configparser.ConfigParser()
    config.read_file(open('config.cfg'))
    if account:
        api_key = config.get('BINANCE', 'ACTUAL_API_KEY')
        secret_key = config.get('BINANCE', 'ACTUAL_SECRET_KEY')
        client = Client(api_key, secret_key)
        print('You are using your real account')
    else:
        api_key = config.get('BINANCE', 'TEST_API_KEY')
        secret_key = config.get('BINANCE', 'TEST_SECRET_KEY')
        client = Client(api_key, secret_key)
        client.API_URL = 'https://testnet.binance.vision/api'
        print('You are using your test account')

    twn = ThreadedWebsocketManager(
        api_key=api_key, api_secret=secret_key)

    return client, twn
