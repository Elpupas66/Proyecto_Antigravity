
import os
import MetaTrader5 as mt5
from dotenv import load_dotenv

load_dotenv()

def test():
    path = os.getenv("MT5_PATH")
    login = int(os.getenv("MT5_LOGIN"))
    password = os.getenv("MT5_PASSWORD")
    server = os.getenv("MT5_SERVER")
    
    print(f"Path: {path}")
    print(f"Login: {login}")
    print(f"Server: {server}")
    
    if path:
        res = mt5.initialize(path=path)
    else:
        res = mt5.initialize()
        
    if not res:
        print(f"Init failed: {mt5.last_error()}")
        return
        
    print("Init success")
    
    if not mt5.login(login=login, password=password, server=server):
        print(f"Login failed: {mt5.last_error()}")
        return
        
    print("Login success")
    print(f"Account Info: {mt5.account_info()}")
    print(f"Positions: {mt5.positions_total()}")
    
    # Test a symbol
    symbol = "BTCUSD"
    si = mt5.symbol_info(symbol)
    if si is None:
        print(f"Symbol {symbol} not found")
    else:
        print(f"Symbol {symbol} found: {si.bid}/{si.ask}")
        
    mt5.shutdown()

if __name__ == "__main__":
    test()
