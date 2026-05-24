from abc import ABC, abstractmethod
import pandas as pd

class BaseFetcher(ABC):
    """
    Clase base abstracta para la ingestión de datos de diferentes orígenes.
    Garantiza que todos los conectores devuelvan los datos con un formato uniforme.
    """
    @abstractmethod
    def fetch_historical_data(self, symbol: str, timeframe: str, n_bars: int) -> pd.DataFrame:
        """
        Descarga datos históricos y los retorna en formato estandarizado.
        El DataFrame devuelto debe tener obligatoriamente las columnas:
        ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        """
        pass
