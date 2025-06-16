import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb
import pandas as pd



# def load_data(path: str) -> pd.DataFrame:
#     """Carrega o CSV e renomeia colunas conforme seu notebook."""
#     df = pd.read_csv(path)
#     df.rename(columns={
#         'Suburb': 'Subúrbio',
#         'Address': 'Endereço',
#         'Rooms': 'Salas',
#         'Type': 'Tipo',
#         'Price': 'Preço',
#         'Method': 'Método de Venda',
#         'SellerG': 'Vendedor',
#         'Date': 'Data',
#         'Distance': 'Distância',
#         'Postcode': 'Código Postal',
#         'Bedroom2': 'Quartos',
#         'Bathroom': 'Banheiros',
#         'Car': 'Garagem',
#         'Landsize': 'Tamanho do Terreno',
#         'BuildingArea': 'Área Construída',
#         'YearBuilt': 'Ano de Construção',
#         'CouncilArea': 'Área Administrativa',
#         'Lattitude': 'Latitude',
#         'Longtitude': 'Longitude',
#         'Regionname': 'Nome da Região',
#         'Propertycount': 'Quantidade de Imóveis na Região'
#     }, inplace=True)
#     # converte código de tipo
#     df['Tipo'] = df['Tipo'].map({'h': 'Casa', 'u': 'Apartamento', 't': 'Terreno'})
#     return df


def dados_estatisticos(df: pd.DataFrame) -> None:
    """Imprime estatísticas descritivas e plota histograma de preço."""
    print("Shape:", df.shape)
    print("Linhas completas:", df.dropna().shape[0])
    print("Missing por coluna:\n", df.isnull().sum().sort_values(ascending=False))
    print("\nDescrição numérica:\n", df.describe())
    for col in df.select_dtypes(include='object'):
        print(f"\nFrequência relativa {col}:\n", df[col].value_counts(normalize=True).head(5))
    if 'Preço' in df:
        print("\nCorrelação com Preço:\n", df.corr(numeric_only=True)['Preço'].sort_values(ascending=False))
        df['Preço'].hist(bins=50)
        plt.title("Distribuição de Preços")
        plt.show()
    print("Duplicados:", df.duplicated().sum())



def fill_missing_by_neighborhood(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Preenche NaN de `column` pela mediana do bairro ou global."""
    med = df.groupby('Subúrbio')[column].median()
    def _fill(row):
        if pd.isna(row[column]):
            return med.get(row['Subúrbio'], df[column].median())
        return row[column]
    df[column] = df.apply(_fill, axis=1)
    return df


def get_cleaned_df(path: str) -> pd.DataFrame:
    """Pipeline de limpeza completa."""
    df = load_data(path)
    df = drop_unused_columns(df)
    for col in ['Garagem', 'Banheiros', 'Quartos']:
        df = fill_missing_by_neighborhood(df, col)
    return df


def prepare_training_data(df: pd.DataFrame):
    # filtra linhas com Price não nulo
    df_pre = df[df['Price'].notna()].copy()
    # y alvo
    y = df_pre['Price']
    # remove colunas irrelevantes
    X = df_pre.drop(columns=['Price', 'Address', 'Date'], errors='ignore')
    # dummy encode e preencher NaN
    X = pd.get_dummies(X, drop_first=True)
    X = X.fillna(X.median(numeric_only=True))
    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_random_forest(X_train, y_train, **params) -> RandomForestRegressor:
    rf = RandomForestRegressor(**dict(n_estimators=300, random_state=42, **params))
    rf.fit(X_train, y_train)
    return rf


def train_xgboost(X_train, y_train, **params) -> xgb.XGBRegressor:
    model = xgb.XGBRegressor(**dict(n_estimators=200, learning_rate=0.05,
                                    max_depth=10, subsample=0.8,
                                    colsample_bytree=0.8,
                                    random_state=42, **params))
    model.fit(X_train, y_train, eval_set=[(X_train, y_train)], verbose=False)
    return model


def train_lightgbm(X_train, y_train, **params) -> lgb.LGBMRegressor:
    model = lgb.LGBMRegressor(**dict(n_estimators=400, max_depth=30, random_state=42, **params))
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test) -> dict:
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    return {'MAE': mae, 'R2': r2}


def predict_for_property(row: pd.Series, rf, xgb_model) -> dict:
   
    temp = row.to_frame().T
    temp = pd.get_dummies(temp, drop_first=True)
    temp = temp.reindex(columns=rf.feature_names_in_, fill_value=0)
    temp = temp.fillna(temp.median(numeric_only=True))
    return {
        'RandomForest': float(rf.predict(temp)[0]),
        'XGBoost':    float(xgb_model.predict(temp)[0])
    }