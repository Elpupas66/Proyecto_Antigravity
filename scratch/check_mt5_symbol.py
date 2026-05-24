import os
import sys
from dotenv import load_dotenv
import MetaTrader5 as mt5

# Asegurar salida en UTF-8 para evitar problemas en terminales Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

MT5_LOGIN = os.getenv("MT5_LOGIN")
MT5_PASSWORD = os.getenv("MT5_PASSWORD")
MT5_SERVER = os.getenv("MT5_SERVER")
MT5_PATH = os.getenv("MT5_PATH")


def check_symbol(symbol: str) -> None:
    if MT5_PATH:
        initialized = mt5.initialize(path=MT5_PATH)
    else:
        initialized = mt5.initialize()

    if not initialized:
        print(f"Init failed: {mt5.last_error()}")
        return

    try:
        if MT5_LOGIN and MT5_PASSWORD and MT5_SERVER:
            logged_in = mt5.login(
                login=int(MT5_LOGIN),
                password=MT5_PASSWORD,
                server=MT5_SERVER,
            )
            if not logged_in:
                print(f"Login failed: {mt5.last_error()}")
                return

        info = mt5.symbol_info(symbol)
        if info is None:
            print(f"Error: Symbol {symbol} not found")
            return

        print(f"Symbol: {info.name}")
        print(f"Filling mode: {info.filling_mode}")

        if info.filling_mode == mt5.ORDER_FILLING_FOK:
            print("Supports ORDER_FILLING_FOK")
        elif info.filling_mode == mt5.ORDER_FILLING_IOC:
            print("Supports ORDER_FILLING_IOC")
        elif info.filling_mode == mt5.ORDER_FILLING_RETURN:
            print("Supports ORDER_FILLING_RETURN")
        else:
            print(f"Unknown filling mode: {info.filling_mode}")

    finally:
        mt5.shutdown()


if __name__ == "__main__":
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else os.getenv("MT5_SYMBOL", "BTCUSD")
    check_symbol(symbol)