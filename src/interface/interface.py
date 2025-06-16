import os
import sys
# Allow importing dados1.py from src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk
from tkintermapview import TkinterMapView
from data_interface import DataInterface

# importa as funções de ML
from dados1 import (
    prepare_training_data,
    train_random_forest,
    train_xgboost,
    evaluate_model,
    predict_for_property
)

class ImovelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Propriedades com Mapa")

        # --- configura ML usando o CSV já limpo ---
        # carrega o DataFrame limpo via DataInterface
        self.data_iface = DataInterface("/home/baile/IA/data/dataset_cleaned.csv")
        df_ml = self.data_iface.load()

        # separa treino/teste e treina os modelos
        X_train, X_test, y_train, y_test = prepare_training_data(df_ml)
        self.rf_model  = train_random_forest(X_train, y_train)
        self.xgb_model = train_xgboost   (X_train, y_train)

        # avalia XGBoost para obter o R²
        self.xgb_metrics = evaluate_model(self.xgb_model, X_test, y_test)

        # lista de imóveis para a interface
        self.lista_imoveis = self.data_iface.list_properties()

        # --- constrói GUI ---
        frame_top = tk.Frame(root)
        frame_top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.combo_imovel = ttk.Combobox(
            frame_top,
            values=self.lista_imoveis["PropertyID"].tolist(),
            width=30
        )
        self.combo_imovel.set("Selecione o imóvel")
        self.combo_imovel.pack(side=tk.LEFT, padx=5)

        self.btn_detalhes = tk.Button(
            frame_top,
            text="Mostrar Detalhes",
            command=self.exibir_detalhes
        )
        self.btn_detalhes.pack(side=tk.LEFT, padx=5)

        self.map_widget = TkinterMapView(root, width=820, height=500, corner_radius=0)
        self.map_widget.set_position(-37.8136, 144.9631)
        self.map_widget.set_zoom(10)
        self.map_widget.pack(pady=5)

        self.label_info = tk.Label(root, text="", justify=tk.LEFT)
        self.label_info.pack(pady=5)

    def exibir_detalhes(self):
        escolha = self.combo_imovel.get()
        if not escolha.startswith("Imovel "):
            self.label_info.config(text="Selecione um imóvel válido.")
            return

        idx = int(escolha.replace("Imovel ", "")) - 1

        # dados cadastrais
        dados = self.data_iface.get_property_info(idx + 1)
        lat   = self.lista_imoveis.iloc[idx]["Lattitude"]
        lon   = self.lista_imoveis.iloc[idx]["Longtitude"]

        info = [
            f"Preço Real: {dados.get('Preço', 'N/A')}",
            f"Quartos: {dados.get('Quartos', 'N/A')}",
            f"Banheiros: {dados.get('Banheiros', 'N/A')}",
            f"Garagem: {dados.get('Car', 'N/A')}",
            f"Latitude: {lat}",
            f"Longitude: {lon}"
        ]

        # previsão XGBoost
        row  = self.data_iface.load().reset_index(drop=True).iloc[idx]
        preds = predict_for_property(row, self.rf_model, self.xgb_model)
        r2    = self.xgb_metrics['R2']
        info += [
            "",
            f"Preço Previsto (XGBoost): R$ {preds['XGBoost']:.2f}",
            f"R² (XGBoost): {r2:.4f}"
        ]

        self.label_info.config(text="\n".join(info))

        # atualiza o mapa
        self.map_widget.set_position(lat, lon)
        self.map_widget.set_zoom(14)
        self.map_widget.delete_all_marker()
        self.map_widget.set_marker(lat, lon, text=escolha)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImovelApp(root)
    root.mainloop()