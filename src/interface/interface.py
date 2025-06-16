import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk
from tkintermapview import TkinterMapView
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import math
import pandas as pd  # necessário para manipulação de DataFrame

class ImovelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Propriedades com Mapa")

        # --- leitura direta do CSV já limpo ---
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/dataset_cleaned.csv"))
        self.df = pd.read_csv(csv_path)
        if self.df['Preço'].dtype != float:
            self.df['Preço'] = (
                self.df['Preço']
                .astype(str)
                .str.replace(r'[^\d.]', '', regex=True)
                .replace('', '0')
                .astype(float)
            )
        self.lista_imoveis = self.df.copy()

        # --- frame superior: centraliza os controles ---
        frame_top = tk.Frame(root)
        frame_top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        control_frame = tk.Frame(frame_top)
        control_frame.pack(expand=True)

        self.combo_imovel = ttk.Combobox(
            control_frame,
            values=[f"Imovel {i+1}" for i in range(len(self.lista_imoveis))],
            width=30
        )
        self.combo_imovel.set("Selecione o imóvel")
        self.combo_imovel.pack(side=tk.LEFT, padx=5)

        self.btn_detalhes = tk.Button(
            control_frame,
            text="Mostrar Detalhes",
            command=self.exibir_detalhes
        )
        self.btn_detalhes.pack(side=tk.LEFT, padx=5)

        self.btn_recomendar = tk.Button(
            control_frame,
            text="Recomendar Bairro e Imóvel",
            command=self.abrir_formulario_recomendacao
        )
        self.btn_recomendar.pack(side=tk.LEFT, padx=5)

        self.btn_avaliar = tk.Button(
            control_frame,
            text="Avaliar Preço de Imóvel",
            command=self.abrir_formulario_avaliacao
        )
        self.btn_avaliar.pack(side=tk.LEFT, padx=5)

        # --- frame do mapa: ocupa toda área restante ---
        frame_map = tk.Frame(root)
        frame_map.pack(fill=tk.BOTH, expand=True)

        self.map_widget = TkinterMapView(frame_map, corner_radius=0)
        self.map_widget.set_position(-37.8136, 144.9631)
        self.map_widget.set_zoom(10)
        self.map_widget.pack(fill=tk.BOTH, expand=True)


        self.info_frame = tk.Frame(root)                 
        self.info_frame.pack(fill=tk.BOTH, padx=10, pady=5)

    def exibir_detalhes(self):
        escolha = self.combo_imovel.get()
        if not escolha.startswith("Imovel "):
            self.label_info.config(text="Selecione um imóvel válido.")
            return

        idx = int(escolha.replace("Imovel ", "")) - 1
        dados = self.lista_imoveis.iloc[idx]
        lat = dados.get("Latitude", "")
        lon = dados.get("Longitude", "")

        def safe_str(val):
            return "N/A" if pd.isnull(val) else str(val)

        info = [
            f"Subúrbio: {safe_str(dados.get('Subúrbio'))}",
            f"Endereço: {safe_str(dados.get('Endereço'))}",
            f"Salas: {safe_str(dados.get('Salas'))}",
            f"Tipo: {safe_str(dados.get('Tipo'))}",
            f"Preço real: ${dados.get('Preço real', dados.get('Preço')):,.2f}",
            f"Preço Previsto LightGBM: {safe_str(dados.get('Preço Previsto LightGBM'))}",
            f"Distância: {safe_str(dados.get('Distância'))}",
            f"Código postal: {safe_str(dados.get('Código postal'))}",
            f"Quartos: {safe_str(dados.get('Quartos'))}",
            f"Banheiros: {safe_str(dados.get('Banheiros'))}",
            f"Garagem: {safe_str(dados.get('Garagem'))}",
            f"Tamanho do Terreno: {safe_str(dados.get('Tamanho do Terreno'))}",
            f"Área Construída: {safe_str(dados.get('Área Construída'))}",
            f"Ano de Construção: {safe_str(dados.get('Ano de Construção'))}",
            f"Latitude: {safe_str(lat)}",
            f"Longitude: {safe_str(lon)}",
            f"Nome da Região: {safe_str(dados.get('Nome da Região'))}",
            f"Quantidade de Imóveis na Região: {safe_str(dados.get('Quantidade de Imóveis na Região'))}",
            "",
        ]

        for w in self.info_frame.winfo_children():
            w.destroy()

        cols = 3
        rows = math.ceil(len(info) / cols)
        for idx, txt in enumerate(info):
            r = idx % rows
            c = idx // rows
            lbl = tk.Label(
                self.info_frame,
                text=txt,
                font=("Arial", 11, "bold"),   
                justify="center",
            )
            lbl.grid(row=r, column=c, sticky="w", padx=10, pady=2)

        # self.label_info.config(text="\n".join(info))

        if lat and lon:
            self.map_widget.set_position(lat, lon)
            self.map_widget.set_zoom(14)
            self.map_widget.delete_all_marker()
            self.map_widget.set_marker(lat, lon, text=escolha)

    def abrir_formulario_recomendacao(self):
        form = tk.Toplevel(self.root)
        form.title("Recomendação de Bairro e Imóvel")
        frame = ttk.Frame(form, padding=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Quantidade de carros:").grid(row=0, column=0, sticky="w", pady=2)
        entry_carros = ttk.Entry(frame)
        entry_carros.grid(row=0, column=1, pady=2)

        tk.Label(frame, text="Quantidade de quartos:").grid(row=1, column=0, sticky="w", pady=2)
        entry_quartos = ttk.Entry(frame)
        entry_quartos.grid(row=1, column=1, pady=2)

        tk.Label(frame, text="Preço máximo (R$):").grid(row=2, column=0, sticky="w", pady=2)
        entry_preco = ttk.Entry(frame)
        entry_preco.grid(row=2, column=1, pady=2)

        resultado_label = tk.Label(frame, text="", justify=tk.LEFT, font=("Segoe UI", 10))
        resultado_label.grid(row=4, column=0, columnspan=2, pady=10)

        def buscar_melhor_bairro():
            try:
                carros = int(entry_carros.get())
                quartos = int(entry_quartos.get())
                preco_max = float(entry_preco.get())
            except ValueError:
                resultado_label.config(text="Preencha todos os campos corretamente.")
                return

            df_filtrado = self.df[self.df['Preço'] <= preco_max].copy()
            if df_filtrado.empty:
                resultado_label.config(text="Nenhum imóvel encontrado dentro do preço informado.")
                return

            df_filtrado['distancia'] = (
                abs(df_filtrado['Garagem'] - carros) +
                abs(df_filtrado['Quartos'] - quartos)
            )
            melhor = df_filtrado.sort_values(['distancia', 'Preço']).iloc[0]
            info = [
                f"Melhor bairro para você: {melhor['Subúrbio']}",
                f"Imóvel recomendado:",
                f"  Endereço: {melhor.get('Endereço', 'N/A')}",
                f"  Preço: R$ {melhor['Preço']:.2f}",
                f"  Quartos: {melhor['Quartos']}",
                f"  Garagem: {melhor['Garagem']}",
                f"  Tipo: {melhor.get('Tipo', 'N/A')}",
            ]
            resultado_label.config(text="\n".join(info))

        ttk.Button(frame, text="Buscar", command=buscar_melhor_bairro)\
            .grid(row=3, column=0, columnspan=2, pady=10)

    def abrir_formulario_avaliacao(self):
        form = tk.Toplevel(self.root)
        form.title("Avaliação de Preço de Imóvel")
        frame = ttk.Frame(form, padding=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Subúrbio (obrigatório):").grid(row=0, column=0, sticky="w", pady=2)
        suburbios = sorted(self.df['Subúrbio'].dropna().unique())
        combo_suburbio = ttk.Combobox(frame, values=suburbios, state="readonly")
        combo_suburbio.grid(row=0, column=1, pady=2)

        tk.Label(frame, text="Quartos (obrigatório):").grid(row=1, column=0, sticky="w", pady=2)
        entry_quartos = ttk.Entry(frame)
        entry_quartos.grid(row=1, column=1, pady=2)

        tk.Label(frame, text="Banheiros (obrigatório):").grid(row=2, column=0, sticky="w", pady=2)
        entry_banheiros = ttk.Entry(frame)
        entry_banheiros.grid(row=2, column=1, pady=2)

        tk.Label(frame, text="Garagem (opcional):").grid(row=3, column=0, sticky="w", pady=2)
        entry_garagem = ttk.Entry(frame)
        entry_garagem.grid(row=3, column=1, pady=2)

        tk.Label(frame, text="Ano de Construção (opcional):").grid(row=4, column=0, sticky="w", pady=2)
        entry_ano = ttk.Entry(frame)
        entry_ano.grid(row=4, column=1, pady=2)

        resultado_label = tk.Label(frame, text="", justify=tk.LEFT, font=("Segoe UI", 10))
        resultado_label.grid(row=6, column=0, columnspan=2, pady=10)

        def avaliar_preco():
            suburbio = combo_suburbio.get()
            quartos = entry_quartos.get()
            banheiros = entry_banheiros.get()
            garagem = entry_garagem.get()
            ano = entry_ano.get()

            if not suburbio or not quartos or not banheiros:
                resultado_label.config(text="Preencha Subúrbio, Quartos e Banheiros.")
                return
            try:
                quartos = int(quartos); banheiros = int(banheiros)
                if not (0 <= quartos <= 30 and 0 <= banheiros <= 30): raise ValueError
            except ValueError:
                resultado_label.config(text="Quartos e Banheiros devem ser inteiros entre 0 e 30.")
                return

            garagem = int(garagem) if garagem.strip() else None
            ano = int(ano) if ano.strip() else None

            filtro = (
                (self.df['Subúrbio'] == suburbio) &
                (self.df['Quartos'] == quartos) &
                (self.df['Banheiros'] == banheiros)
            )
            if garagem is not None:
                filtro &= (self.df['Garagem'] == garagem)
            if ano is not None:
                filtro &= (self.df['Ano de Construção'] == ano)

            similares = self.df[filtro]
            if similares.empty:
                resultado_label.config(text="Nenhum imóvel similar encontrado.")
                return

            preco_medio = similares['Preço'].mean()
            resultado_label.config(
                text=f"Preço médio: R$ {preco_medio:.2f}\n({len(similares)} encontrado(s))"
            )

        ttk.Button(frame, text="Avaliar", command=avaliar_preco)\
            .grid(row=5, column=0, columnspan=2, pady=10)


if __name__ == "__main__":
    app = tb.Window(themename="flatly")
    app.geometry("1024x768")
    ImovelApp(app)
    app.mainloop()