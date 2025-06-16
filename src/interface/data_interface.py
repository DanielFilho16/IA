import pandas as pd
from typing import List, Optional, Any


"""
Função para a manipulação de dados de um arquivo CSV.
Esta classe fornece métodos para carregar, filtrar, descrever e salvar dados,
bem como para listar propriedades e obter informações específicas de imóveis.
"""
class DataInterface:
    """
    Interface for accessing and manipulating a CSV data table.
    """
    def __init__(self, filepath: str):
        """
        Inicializa a interface com o caminho do arquivo CSV.
        """
        self.filepath = filepath
        self._data: Optional[pd.DataFrame] = None

    def load(self) -> pd.DataFrame:
        """
        Carrega os dados do arquivo CSV em um DataFrame.
        """
        if self._data is None:
            self._data = pd.read_csv(self.filepath)
        return self._data

    def get_columns(self) -> List[str]:
        """
        Retorna uma lista com os nomes das colunas do DataFrame.
        """
        df = self.load()
        return list(df.columns)

    def head(self, n: int = 5) -> pd.DataFrame:
        """
        Retorna as primeiras n linhas do DataFrame.
        """
        df = self.load()
        return df.head(n)

    def filter(self, **conditions: Any) -> pd.DataFrame:

        df = self.load()
        for col, val in conditions.items():
            df = df[df[col] == val]
        return df

    def describe(self) -> pd.DataFrame:

        df = self.load()
        return df.describe()

    def get_value(self, index: int, column: str) -> Any:

        df = self.load()
        return df.at[index, column]

    def save(self, df: pd.DataFrame, filepath: Optional[str] = None) -> None:

        target = filepath if filepath is not None else self.filepath
        df.to_csv(target, index=False)

    def list_properties(self) -> pd.DataFrame:

        df = self.load()
        df_reset = df.reset_index(drop=True)
        df_reset['PropertyID'] = 'Imovel ' + (df_reset.index + 1).astype(str)
        return df_reset[['PropertyID', 'Lattitude', 'Longtitude']]

    def get_property_info(self, index: int) -> dict:

        df = self.load().reset_index(drop=True)
        row = df.iloc[index - 1]
        return {
            "Preço": row.get("Price"),
            "Quartos": row.get("Bedroom2"),
            "Banheiros": row.get("Bathroom"),
            "Car": row.get("Car")
        }
