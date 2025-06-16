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

        # Garante que a coluna Preço é float, removendo símbolos se necessário
        if self.df['Preço'].dtype != float:
            self.df['Preço'] = (
                self.df['Preço']
                .astype(str)
                .str.replace(r'[^\d.]', '', regex=True)
                .replace('', '0')
                .astype(float)
            )
        self.lista_imoveis = self.df.copy()

        # --- constrói GUI ---
        frame_top = tk.Frame(root)
        frame_top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.combo_imovel = ttk.Combobox(
            frame_top,
            values=[f"Imovel {i+1}" for i in range(len(self.lista_imoveis))],
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

        # Botão para abrir o formulário de recomendação de bairro
        self.btn_recomendar = tk.Button(
            frame_top,
            text="Recomendar Bairro e Imóvel",
            command=self.abrir_formulario_recomendacao
        )
        self.btn_recomendar.pack(side=tk.LEFT, padx=5)

        # Botão para abrir o formulário de avaliação de preço
        self.btn_avaliar = tk.Button(
            frame_top,
            text="Avaliar Preço de Imóvel",
            command=self.abrir_formulario_avaliacao
        )
        self.btn_avaliar.pack(side=tk.LEFT, padx=5)

        self.map_widget = TkinterMapView(root, width=820, height=500, corner_radius=0)
        self.map_widget.set_position(-37.8136, 144.9631)
        self.map_widget.set_zoom(10)
        self.map_widget.pack(pady=5)

        self.label_info = tk.Label(root, text="", justify=tk.LEFT, font=("Segoe UI", 11))
        self.label_info.pack(pady=5)

    def exibir_detalhes(self):
        escolha = self.combo_imovel.get()
        if not escolha.startswith("Imovel "):
            self.label_info.config(text="Selecione um imóvel válido.")
            return

        idx = int(escolha.replace("Imovel ", "")) - 1

        # dados cadastrais
        dados = self.lista_imoveis.iloc[idx]
        lat   = dados.get("Latitude", "")
        lon   = dados.get("Longitude", "")

        def safe_str(val):
            if pd.isnull(val):
                return "N/A"
            return str(val)

        info = [
            f"Subúrbio: {safe_str(dados.get('Subúrbio'))}",
            f"Endereço: {safe_str(dados.get('Endereço'))}",
            f"Salas: {safe_str(dados.get('Salas'))}",
            f"Tipo: {safe_str(dados.get('Tipo'))}",
            f"Preço real: {safe_str(dados.get('Preço real', dados.get('Preço')))}",
            f"Preço Previsto LightGBM: {safe_str(dados.get('Preço Previsto LightGBM', dados.get('Preço Previsto LightGBM')))}",
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

        self.label_info.config(text="\n".join(info))

        # atualiza o mapa
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

        # Campos do formulário
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

            # Carrega o DataFrame de imóveis
            df = self.df

            # Filtra imóveis dentro do preço máximo
            df_filtrado = df[df['Preço'] <= preco_max].copy()
            if df_filtrado.empty:
                resultado_label.config(text="Nenhum imóvel encontrado dentro do preço informado.")
                return

            # Calcula uma "distância" para cada imóvel em relação ao desejado
            df_filtrado['distancia'] = (
                abs(df_filtrado['Garagem'] - carros) +
                abs(df_filtrado['Quartos'] - quartos)
            )

            # Encontra o imóvel com menor distância e menor preço
            melhor_imovel = df_filtrado.sort_values(['distancia', 'Preço']).iloc[0]
            melhor_bairro = melhor_imovel['Subúrbio']

            info = [
                f"Melhor bairro para você: {melhor_bairro}",
                f"Imóvel recomendado:",
                f"  Endereço: {melhor_imovel.get('Endereço', 'N/A')}",
                f"  Preço: R$ {melhor_imovel['Preço']:.2f}",
                f"  Quartos: {melhor_imovel['Quartos']}",
                f"  Garagem: {melhor_imovel['Garagem']}",
                f"  Tipo: {melhor_imovel.get('Tipo', 'N/A')}",
            ]
            resultado_label.config(text="\n".join(info))

        btn_buscar = ttk.Button(frame, text="Buscar", command=buscar_melhor_bairro)
        btn_buscar.grid(row=3, column=0, columnspan=2, pady=10)

    def abrir_formulario_avaliacao(self):
        form = tk.Toplevel(self.root)
        form.title("Avaliação de Preço de Imóvel")
        frame = ttk.Frame(form, padding=20)
        frame.pack(fill="both", expand=True)

        # Subúrbio
        tk.Label(frame, text="Subúrbio (obrigatório):").grid(row=0, column=0, sticky="w", pady=2)
        suburbios = sorted(self.df['Subúrbio'].dropna().unique())
        combo_suburbio = ttk.Combobox(frame, values=suburbios, state="readonly")
        combo_suburbio.grid(row=0, column=1, pady=2)

        # Quartos
        tk.Label(frame, text="Quartos (obrigatório):").grid(row=1, column=0, sticky="w", pady=2)
        entry_quartos = ttk.Entry(frame)
        entry_quartos.grid(row=1, column=1, pady=2)

        # Banheiros
        tk.Label(frame, text="Banheiros (obrigatório):").grid(row=2, column=0, sticky="w", pady=2)
        entry_banheiros = ttk.Entry(frame)
        entry_banheiros.grid(row=2, column=1, pady=2)

        # Garagem
        tk.Label(frame, text="Garagem (opcional):").grid(row=3, column=0, sticky="w", pady=2)
        entry_garagem = ttk.Entry(frame)
        entry_garagem.grid(row=3, column=1, pady=2)

        # Ano de Construção
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

            # Validação obrigatórios
            if not suburbio or not quartos or not banheiros:
                resultado_label.config(text="Preencha Subúrbio, Quartos e Banheiros.")
                return
            try:
                quartos = int(quartos)
                banheiros = int(banheiros)
                if not (0 <= quartos <= 30 and 0 <= banheiros <= 30):
                    raise ValueError
            except ValueError:
                resultado_label.config(text="Quartos e Banheiros devem ser inteiros entre 0 e 30.")
                return

            # Garagem (opcional)
            if garagem.strip():
                try:
                    garagem = int(garagem)
                    if not (0 <= garagem <= 30):
                        raise ValueError
                except ValueError:
                    resultado_label.config(text="Garagem deve ser inteiro entre 0 e 30 ou vazio.")
                    return
            else:
                garagem = None

            # Ano de construção (opcional)
            if ano.strip():
                try:
                    ano = int(ano)
                    if not (1900 <= ano <= 2025):
                        raise ValueError
                except ValueError:
                    resultado_label.config(text="Ano de Construção deve ser entre 1900 e 2025 ou vazio.")
                    return
            else:
                ano = None

            # Busca imóveis similares no CSV
            df = self.df
            filtro = (
                (df['Subúrbio'] == suburbio) &
                (df['Quartos'] == quartos) &
                (df['Banheiros'] == banheiros)
            )
            if garagem is not None:
                filtro = filtro & (df['Garagem'] == garagem)
            if ano is not None:
                filtro = filtro & (df['Ano de Construção'] == ano)

            similares = df[filtro]
            if similares.empty:
                resultado_label.config(text="Nenhum imóvel similar encontrado.")
                return

            preco_medio = similares['Preço'].mean()
            resultado_label.config(
                text=f"Preço médio dos imóveis similares: R$ {preco_medio:.2f}\n({len(similares)} encontrado(s))"
            )

        btn_avaliar = ttk.Button(frame, text="Avaliar", command=avaliar_preco)
        btn_avaliar.grid(row=5, column=0, columnspan=2, pady=10)


if __name__ == "__main__":
    app = tb.Window(themename="flatly")
    ImovelApp(app)
    app.mainloop()