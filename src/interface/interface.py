import tkinter as tk
from tkinter import ttk
from tkintermapview import TkinterMapView
from data_interface import DataInterface

"""
Aqui é onde realmente há o print do mapa, com a interface gráfica
e a interação com o usuário.
"""

class ImovelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Propriedades com Mapa")
        
        # Inicializa a interface de dados
        self.data_iface = DataInterface("/home/baile/IA/data/dataset.csv")
        self.lista_imoveis = self.data_iface.list_properties()
        
        # Frame para conter o ComboBox e o botão
        frame_top = tk.Frame(root)
        frame_top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # Criar ComboBox
        self.combo_imovel = ttk.Combobox(frame_top, values=self.lista_imoveis["PropertyID"].tolist(), width=30)
        self.combo_imovel.set("Selecione o imóvel")
        self.combo_imovel.pack(side=tk.LEFT, padx=5)
        
        # Botão para exibir detalhes
        self.btn_detalhes = tk.Button(frame_top, text="Mostrar Detalhes", command=self.exibir_detalhes)
        self.btn_detalhes.pack(side=tk.LEFT, padx=5)
        
        # Mapa
        self.map_widget = TkinterMapView(root, width=820, height=500, corner_radius=0)

        self.map_widget.set_position(-37.8136, 144.9631)
        self.map_widget.set_zoom(10)
        self.map_widget.pack(pady=5)
        
 
        self.label_info = tk.Label(root, text="", justify=tk.LEFT)
        self.label_info.pack(pady=5)

    def exibir_detalhes(self):
        escolha = self.combo_imovel.get()
        if escolha.startswith("Imovel "):
            index = int(escolha.replace("Imovel ", ""))
            dados = self.data_iface.get_property_info(index)
            lat = self.lista_imoveis.iloc[index - 1]["Lattitude"]
            lon = self.lista_imoveis.iloc[index - 1]["Longtitude"]
            
            info_text = (
                f"Preço: {dados['Preço']}\n"
                f"Quartos: {dados['Quartos']}\n"
                f"Banheiros: {dados['Banheiros']}\n"
                f"Car: {dados['Car']}\n"
                f"Latitude: {lat}\n"
                f"Longitude: {lon}"
            )
            self.label_info.config(text=info_text)
            
            self.map_widget.set_position(lat, lon)
            self.map_widget.set_zoom(14)
            self.map_widget.delete_all_marker()
            self.map_widget.set_marker(lat, lon, text=escolha)
        else:
            self.label_info.config(text="Selecione um imóvel válido.")



if __name__ == "__main__":
    root = tk.Tk()
    app = ImovelApp(root)
    root.mainloop()