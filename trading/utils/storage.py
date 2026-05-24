import pandas as pd
from pathlib import Path

class DataStorage:
    """
    Utilidades para guardar y cargar datos optimizados al disco.
    """
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def save_parquet(self, df: pd.DataFrame, symbol: str, timeframe: str) -> str:
        """
        Guarda el DataFrame estandarizado en formato parquet de alta compresión.
        """
        clean_symbol = symbol.replace('/', '').replace('\\', '').upper()
        filename = f"{clean_symbol}_{timeframe}.parquet"
        filepath = self.base_dir / filename
        
        # Necesita pyarrow instalado
        df.to_parquet(filepath, index=False)
        print(f"[OK] Archivo guardado correctamente en: {filepath}")
        return str(filepath)
        
    def load_parquet(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """
        Carga el archivo Parquet a memoria ultrarrápido.
        """
        clean_symbol = symbol.replace('/', '').replace('\\', '').upper()
        filename = f"{clean_symbol}_{timeframe}.parquet"
        filepath = self.base_dir / filename
        
        if not filepath.exists():
             raise FileNotFoundError(f"No se encuentra histórico local: {filepath}. Usa un Fetcher primero.")
             
        return pd.read_parquet(filepath)
