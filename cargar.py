import random

def cargar_procesos_desde_archivo(archivo):
    procesos = []
    with open(archivo, 'r') as file:
        for line in file:
            data = line.strip().split(',')
            nombre = data[0]
            tiempo_llegada = random.uniform(0, 10)  # Asigna un tiempo de llegada aleatorio entre 0 y 10
            tiempo_rafaga = int(data[1])
            prioridad = int(data[2])

            proceso = Proceso(nombre, tiempo_llegada, tiempo_rafaga, prioridad)
            procesos.append(proceso)

    return procesos
