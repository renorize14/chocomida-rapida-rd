class ProductClass:
    def __init__(self, id, producto, valor, cantidad):
        self.id = id
        self.producto = producto
        self.valor = int(valor)  
        try:
        	self.cantidad = int(cantidad) 
        except:
        	self.cantidad = -1

    def __repr__(self):
        return f"Producto(id={self.id}, producto={self.producto}, valor={self.valor}, cantidad={self.cantidad})"
