#
# Implementa la simulacion del problema de eleccion usando el algoritmos de Le, Chang y Roberts
#
# Elaboro: Edgar Daniel Rodriguez Herrera
#

import sys
from event import Event
from model import Model
from process import Process
from simulator import Simulator
from simulation import Simulation
import random
import time

class algoritmoEleccionDist(Model):#se ejecuta por cada proceso/modelo que se asocia con cada nodo del grafo
  # Esta clase desciende de la clase Model e implementa los metodos
  # "init()" y "receive()", que en la clase madre se definen como abstractos

  def init(self):
      # Aqui se definen e inicializan los atributos particulares del algoritmo
      print("Inicio funciones", self.id)
      print("Mis vecinos son: ", end=" ")
      for neighbor in self.neighbors:
          # self.sucesor = neighbor
          print(neighbor, end=" ")
      print("\n")

      #Variables de estado
      #por el valor de los nodos en el grafo 2 (no estan ordenados de menor a mayor o viceversa),
      #decimos que el sucesor del nodo j es el nodo que se inserto por ultimo en su lista de vecinos,
      #eso sirve ya que asi se formateo la representacion textual del grafo:
      #[vecino por detras] [vecino por delante]
      #en este caso el sentido del anillo es unidireccional en el sentido de las manecillas del reloj
      self.sucesor = self.neighbors[1]
      #0->dormido(no esta participando en la eleccion)
      #1->despierto(esta participando en la eleccion)
      #estado inicialmente dormido (==1)
      self.estado = 0
      #lider inicialmente tiene un valor no usado por los ids de los nodos
      self.lider = 0

  def receive(self, event):
    # Aqui se definen las acciones concretas que deben ejecutarse cuando se recibe un evento
    #Al principio a todos los nodos se les manda un mensaje de INICIA
    if event.getName() == "INICIA":
        print("[", self.id, "]: recibi INICIA en t=", self.clock, "\n")
        #luego deciden si lanzan su candidatura
        """
        ### para reproducir el peor caso en mensajes ###
        p = 1
        """

        p = random.randint(1, 5)
        #la probabilidad de que salga cualquier valor de 1 a 5 es de 0.20

        #si deciden lanzar la candidatura
        if p == 1:
            #despiertan de manera autonoma (participa en la eleccion)
            self.estado = 1
            print("Lanzo candidatura!", "\n")
            candidatura = Event("CANDIDATURA", self.clock + 1, self.sucesor, self.id, self.id)
            #(name, time, target, source, candidatura)
            if candidatura.time <= maxtime:
                #lanzan su candidatura a su sucesor
                self.transmit(candidatura)
            else:
                print("Tiempo maximo agotado!")
        #si deciden NO lanzar su candidatura
        else:
            print("NO lanzo candidatura!", "\n")
    elif event.getName() == "CANDIDATURA":
        print("[", self.id, "]: recibi CANDIDATURA de [", event.source, "] en t=", self.clock, "\n")
        print("El candidato es: [", event.candidatura, "]", "\n")
        #cada nodo al recibir el mensaje de candidatura,
        #checa si el id de su antecesor es mayor que su propio id
        #si SI lo es,
        if event.candidatura > self.id:
            print("[", self.id, "]: soy menor que [", event.candidatura, "]", "\n")
            print("El candidato sigue siendo: [", event.candidatura, "]", "\n" )
            #entonces continua la transmision del mensaje CANDIDATURA con el mismo candidato
            self.estado = 1
            candidatura = Event("CANDIDATURA", self.clock + 1, self.sucesor, self.id, event.candidatura)
            self.transmit(candidatura)
        #si NO lo es,
        else:
            #y es mayor que su antecesor y esta dormido (no esta participando en la eleccion)
            if self.id > event.candidatura and self.estado == 0:
                print("[", self.id, "]: soy mayor que [", event.candidatura, "]", "\n")
                print("[", self.id, "]: soy el nuevo candidato\n")
                self.estado = 1
                candidatura = Event("CANDIDATURA", self.clock + 1, self.sucesor, self.id, self.id)
                self.transmit(candidatura)
            #Si es igual a su antecesor y esta despierto
            elif self.id == event.candidatura:
                #se hace electo
                print("[", self.id, "]: me hago electo!\n")
                #se marca como no participante (dormido)
                self.estado = 0
                #envia ELECTO a su sucesor
                electo = Event("ELECTO", self.clock + 1, self.sucesor, self.id, event.candidatura)
                self.transmit(electo)
            # Si es mayor que su antecesor y esta participando (despierto),
            # elif self.id > event.candidatura and self.estado == 1:
            # descarta el mensaje de candidatura.
            else:
                print("[", self.id, "]: soy mayor que [", event.candidatura, "] y ya estoy participando", "\n")
                print("Descarto la candidatura!")
    elif event.getName() == "ELECTO":
        print("[", self.id, "]: recibi ELECTO de [", event.source, "] en t=", self.clock, "\n")
        #al recibir electo, se denomina en su variable de estado lider al nodo electo
        self.lider = event.candidatura
        print("El nodo electo es [", event.candidatura, "]\n")
        #si no ha llegado al nodo que se denomino electo,
        if event.candidatura != self.id:
            #sigue transmitiendo el mensaje de electo
            electo = Event("ELECTO", self.clock + 1, self.sucesor, self.id, event.candidatura)
            self.transmit(electo)
        #si llega al nodo que se denomino electo
        else:
            print("Termina la eleccion!")
            print("Numero de mensajes transmitidos: ", Process.counter)
        #al final se duerme
        self.estado = 0
# ----------------------------------------------------------------------------------------
# "main()"
# ----------------------------------------------------------------------------------------
# construye una instancia de la clase Simulation recibiendo como parametros el nombre del
# archivo que codifica la lista de adyacencias de la grafica y el tiempo max. de simulacion
if len(sys.argv) != 2:
   print ("Por favor proporcione el nombre de la grafica de comunicaciones")
   raise SystemExit(1)

maxtime= 20
experiment = Simulation(sys.argv[1], maxtime)#filename, maxtime

# imprime lista de nodos que se extraen del archivo
# experiment.graph[indice+1 == nodo] == vecino
print("Lista de nodos: ", experiment.graph)

# asocia un pareja proceso/modelo con cada nodo de la grafica
for i in range(1,len(experiment.graph)+1):
    m = algoritmoEleccionDist()
    experiment.setModel(m, i)

# inserta un evento semilla en la agenda y arranca

for nodo in range(1, len(experiment.graph)+1):
    seed = Event("INICIA", nodo-1, nodo, nodo, 0)#name, time, target, source, candidatura
    experiment.init(seed)
experiment.run()

### para reproducir el mejor caso en mensajes y tiempo###
"""
seed = Event("INICIA", 0, len(experiment.graph), len(experiment.graph), 0)#name, time, target, source, candidatura
experiment.init(seed)
experiment.run()
"""
### para reproducir el peor caso en tiempo ###
"""
numNodos = len(experiment.graph)
vecinosNodoMayor = experiment.graph[numNodos-1]
sucesor = vecinosNodoMayor[1]
seed = Event("INICIA", 0, sucesor, sucesor, 0)#name, time, target, source, candidatura
experiment.init(seed)
experiment.run()
"""



