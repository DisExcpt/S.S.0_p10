import tkinter as tk
from tkinter import ttk
from threading import Thread
from queue import Queue, Empty
import time
import random

class Proceso:
    def __init__(self, name, arrival_time, burst_time, priority):
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority

def cargar_procesos_desde_archivo(archivo):
    procesos = []
    with open(archivo, 'r') as file:
        next(file)  # Saltar la primera línea (encabezado)
        for line in file:
            data = line.strip().split(',')
            nombre, tiempo_rafaga, prioridad = data
            tiempo_llegada = random.randint(0, 10)  # Generar tiempo de llegada aleatorio
            proceso = Proceso(nombre, tiempo_llegada, int(tiempo_rafaga), int(prioridad))
            procesos.append(proceso)
    return procesos

def round_robin(procesos, quantum, completados, q):
    tiempo_total = 0
    while procesos:
        proceso = procesos.pop(0)
        tiempo_restante = min(quantum, proceso.remaining_time)
        tiempo_espera = 0.1  # Ajusta el valor según lo que necesites
        time.sleep(tiempo_espera)
        tiempo_total += tiempo_restante
        proceso.remaining_time -= tiempo_restante

        if proceso.remaining_time > 0:
            procesos.append(proceso)
        else:
            completados.append((proceso.name, "Round Robin", tiempo_total))
            q.put((proceso.name, "Round Robin", tiempo_total))

def sjf(procesos, completados, q):
    procesos.sort(key=lambda x: x.burst_time)
    tiempo_total = 0
    for proceso in procesos[:]:
        tiempo_espera = 0.1  # Ajusta el valor según lo que necesites
        time.sleep(tiempo_espera)
        tiempo_total += proceso.burst_time
        completados.append((proceso.name, "SJF", tiempo_total))
        q.put((proceso.name, "SJF", tiempo_total))

def fifo(procesos, completados, q):
    tiempo_total = 0
    for proceso in procesos[:]:
        tiempo_espera = 0.1  # Ajusta el valor según lo que necesites
        time.sleep(tiempo_espera)
        tiempo_total += proceso.burst_time
        completados.append((proceso.name, "FIFO", tiempo_total))
        q.put((proceso.name, "FIFO", tiempo_total))

def prioridades(procesos, completados, q):
    procesos.sort(key=lambda x: x.priority)
    tiempo_total = 0
    for proceso in procesos[:]:
        tiempo_espera = 0.1  # Ajusta el valor según lo que necesites
        time.sleep(tiempo_espera)
        tiempo_total += proceso.burst_time
        completados.append((proceso.name, "Prioridades", tiempo_total))
        q.put((proceso.name, "Prioridades", tiempo_total))

class InterfazGrafica:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación de Planificación de Procesos")

        self.procesos = []
        self.completados = []
        self.queue = Queue()
        self.algoritmo_seleccionado = tk.StringVar(value="Round Robin")

        # Agregar un atributo para almacenar el hilo de la simulación
        self.simulacion_thread = None

        self.crear_widgets()

    def crear_widgets(self):
        frame_procesos = ttk.Frame(self.root)
        frame_procesos.grid(row=0, column=0, padx=10, pady=10)

        ttk.Label(frame_procesos, text="Nombre").grid(row=0, column=0)
        ttk.Label(frame_procesos, text="Tiempo Ráfaga").grid(row=0, column=1)
        ttk.Label(frame_procesos, text="Prioridad").grid(row=0, column=2)
        ttk.Label(frame_procesos, text="Tiempo Llegada").grid(row=0, column=3)

        self.entry_nombre = ttk.Entry(frame_procesos)
        self.entry_tiempo_rafaga = ttk.Entry(frame_procesos)
        self.entry_prioridad = ttk.Entry(frame_procesos)
        self.entry_tiempo_llegada = ttk.Entry(frame_procesos)

        self.entry_nombre.grid(row=1, column=0)
        self.entry_tiempo_rafaga.grid(row=1, column=1)
        self.entry_prioridad.grid(row=1, column=2)
        self.entry_tiempo_llegada.grid(row=1, column=3)

        ttk.Button(frame_procesos, text="Agregar Proceso", command=self.agregar_proceso).grid(row=1, column=4)

        self.tree_procesos = ttk.Treeview(frame_procesos, columns=("Nombre", "Ráfaga", "Prioridad", "Llegada"))
        self.tree_procesos.grid(row=2, column=0, columnspan=5, pady=10)

        ttk.Button(frame_procesos, text="Iniciar Simulación", command=self.iniciar_simulacion).grid(row=3, column=0, columnspan=5)

        frame_configuracion = ttk.Frame(self.root)
        frame_configuracion.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(frame_configuracion, text="Algoritmo de Planificación").grid(row=0, column=0)
        ttk.Combobox(frame_configuracion, textvariable=self.algoritmo_seleccionado,
                     values=["Round Robin", "SJF", "FIFO", "Prioridades"]).grid(row=0, column=1)

    def iniciar_simulacion(self):
        self.completados = []  # Reiniciar la lista de procesos completados
        algoritmo_seleccionado = self.algoritmo_seleccionado.get()

        # Hacer una copia de los procesos al inicio de la simulación
        procesos_copia = [Proceso(p.name, p.arrival_time, p.burst_time, p.priority) for p in self.procesos]

        if algoritmo_seleccionado == "Round Robin":
            round_robin(procesos_copia.copy(), 2, self.completados, self.queue)
        elif algoritmo_seleccionado == "SJF":
            sjf(procesos_copia.copy(), self.completados, self.queue)
        elif algoritmo_seleccionado == "FIFO":
            fifo(procesos_copia.copy(), self.completados, self.queue)
        elif algoritmo_seleccionado == "Prioridades":
            prioridades(procesos_copia.copy(), self.completados, self.queue)

        # Cambiar a una ejecución única en lugar de usar la iteración automática
        self.mostrar_resultados()

    def mostrar_resultados(self):
        try:
            proceso_completado = self.queue.get_nowait()
            nombre, algoritmo, tiempo = proceso_completado
            print(f"{nombre} completado con {algoritmo} en {tiempo} segundos")
            # No hay más resultados, detener la iteración
            # Llamar a la siguiente iteración automáticamente
            self.root.after(100, self.mostrar_resultados)
        except Empty:
            pass

    def agregar_proceso(self):
        nombre = self.entry_nombre.get()
        tiempo_rafaga = int(self.entry_tiempo_rafaga.get())
        prioridad = int(self.entry_prioridad.get())
        tiempo_llegada = int(self.entry_tiempo_llegada.get())

        proceso = Proceso(nombre, tiempo_llegada, tiempo_rafaga, prioridad)
        self.procesos.append(proceso)

        self.tree_procesos.insert("", "end", values=(nombre, tiempo_rafaga, prioridad, tiempo_llegada))

        # Si ya hay una simulación en ejecución, iniciar un hilo adicional para la simulación con el nuevo proceso
        if self.simulacion_thread and self.simulacion_thread.is_alive():
            t = Thread(target=self.iniciar_simulacion_nuevo_proceso, args=())
            t.start()
        else:
            # Si no hay simulación en ejecución, iniciar la simulación principal
            self.iniciar_simulacion()

    def iniciar_simulacion_nuevo_proceso(self):
        # Hacer una copia de los procesos antes de ejecutar la simulación con el nuevo proceso
        procesos_copia = [Proceso(p.name, p.arrival_time, p.burst_time, p.priority) for p in self.procesos]

        algoritmo_seleccionado = self.algoritmo_seleccionado.get()

        if algoritmo_seleccionado == "Round Robin":
            round_robin(procesos_copia, 2, self.completados, self.queue)
        elif algoritmo_seleccionado == "SJF":
            sjf(procesos_copia, self.completados, self.queue)
        elif algoritmo_seleccionado == "FIFO":
            fifo(procesos_copia, self.completados, self.queue)
        elif algoritmo_seleccionado == "Prioridades":
            prioridades(procesos_copia, self.completados, self.queue)

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazGrafica(root)
    # Cargar procesos desde archivo al inicio
    app.procesos = cargar_procesos_desde_archivo("procesos.txt")
    for proceso in app.procesos:
        app.tree_procesos.insert("", "end", values=(proceso.name, proceso.burst_time, proceso.priority, proceso.arrival_time))
    root.mainloop()
