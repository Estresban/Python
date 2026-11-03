import numpy as np

print(np.__version__)

ventas = np.array([150,200,180,250,300,220,190])

ceros = np.zeros(7)
print("Ceros:", ceros)

unos = np.ones(7)
print("Unos:", unos)        

constantes = np.full(7, 100)
print("Constantes:", constantes)

secuencia = np.arange( 0, 20, 2 )
print("Secuencia:", secuencia)

espaciados = np.linspace(0, 100, 5)
print("Espaciados:", espaciados)    

vacio = np.empty(3)
print("Vacio:", vacio)  


print ("Numeros de dimensiones:", ventas.ndim)

print ("Forma del array:", ventas.shape)

print ("Tamaño del array:", ventas.size)

print ("Tipo de datos del array:", ventas.dtype)

print ("Tamaño de cada elemento del array:", ventas.itemsize, "bytes")

print ("Tamaño total del array en bytes:", ventas.nbytes, "bytes")

print("Memoria total del array:", ventas.nbytes, "bytes ")

matriz = np.array([
    [150, 200, 180, 250, 300, 220, 190], 
    [100, 120, 110, 130, 150, 140, 160], 
    [80, 90, 85, 95, 100, 105, 110],
    [50, 60, 55, 65, 70, 75, 80],
    [30, 40, 35, 45, 50, 55, 60],
    [20, 25, 22, 28, 30, 32, 35],
    [10, 15, 12, 18, 20, 22, 25]
])

print("Matriz:\n", matriz)

print("Número de dimensiones de la matriz:", matriz.ndim)

print("Forma de la matriz:", matriz.shape)  
print("Tamaño de la matriz:", matriz.size)

transpuesta = np.transpose(matriz)
print("Matriz transpuesta:\n", transpuesta)

array = np.arange(12)
print("Array:", array)
matriz_reshaped = array.reshape(3, 4)
print("Matriz reshaped:\n", matriz_reshaped)

matriz_reshaped2 = matriz.flatten()
print("Matriz aplanada:\n", matriz_reshaped2)   

print ("Primer elemento de ventas:", ventas[0])
print ("Segundo elemento de ventas:", ventas[1])
print ("Último elemento de ventas:", ventas[-1])
print ("Primeros 3 elementos de ventas:", ventas[0:3])
print ("Primeros 3 elementos de ventas:", ventas[:3])
print ("Elementos de ventas desde el índice 2 hasta el final:", ventas[2:])

print ("primera fila de la matriz:", matriz[0, :])
print ("segunda fila de la matriz:", matriz[1, :])
print ("tercera fila de la matriz:", matriz[2, :])  


print ("primera columna de la matriz:", matriz[:, 0])
print ("segunda columna de la matriz:", matriz[:, 1])

print ("Fila 2, columna 3 de la matriz:", matriz[1, 2])


datos = np.array([10, 20, 30, 40, 50])
print("Array original:", datos)

print(np.pi)  # Valor de pi

datos[0] = 100
print("Array modificado:", datos)

datos[1:3] = [200, 300]
print("Array modificado:", datos)

copia_datos = datos.copy()
print("Copia del array:", copia_datos)

precios = np.array([10, 20, 30, 40, 50])
print("Array de precios:", precios)

precios_con_iva = precios * 1.21
print("Array de precios con IVA:", precios_con_iva)

potencias_precios = precios ** 2
print("Array de precios al cuadrado:", potencias_precios)

raiz_cuadrada_precios = np.sqrt(precios)
print("Raíz cuadrada de los precios:", raiz_cuadrada_precios)

valor_absoluto_precios = np.abs(precios)
print("Valor absoluto de los precios:", valor_absoluto_precios)

redondeo_precios = np.round(precios_con_iva)
print("Precios con IVA redondeados:", redondeo_precios)

redondeo_arriba_precios = np.ceil(precios_con_iva)
print("Precios con IVA redondeados hacia arriba:", redondeo_arriba_precios)     

redondeo_abajo_precios = np.floor(precios_con_iva)
print("Precios con IVA redondeados hacia abajo:", redondeo_abajo_precios)

coseno_precios = np.cos(precios)
print("Coseno de los precios:", coseno_precios)

seno_precios = np.sin(precios)
print("Seno de los precios:", seno_precios)

tangente_precios = np.tan(precios)
print("Tangente de los precios:", tangente_precios)

suma_precios = np.sum(precios)
print("Suma de los precios:", suma_precios)

promedio_precios = np.mean(precios)
print("Promedio de los precios:", promedio_precios)

resta_precios = np.subtract(precios, 5)
print("Precios después de restar 5:", resta_precios)

mediana_precios = np.median(precios)
print("Mediana de los precios:", mediana_precios)

maximo_precios = np.max(precios)
print("Máximo de los precios:", maximo_precios)

minimo_precios = np.min(precios)
print("Mínimo de los precios:", minimo_precios)

varianza_precios = np.var(precios)
print("Varianza de los precios:", varianza_precios) 

posicion_maximo = np.argmax(precios)
print("Posición del máximo de los precios:", posicion_maximo)

posicion_minimo = np.argmin(precios)
print("Posición del mínimo de los precios:", posicion_minimo)



