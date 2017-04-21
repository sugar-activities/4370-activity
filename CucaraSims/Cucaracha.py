#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Cucaracha.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

import os
import gobject
import pygame
from pygame.sprite import Sprite
import random
from math import sin
from math import cos
from math import atan2
from math import radians
from math import degrees

from Timer import Timer

BASE_PATH = os.path.dirname(__file__)

INDICE_ROTACION = 5


class Cucaracha(Sprite, gobject.GObject):

    __gsignals__ = {
    #"new-edad": (gobject.SIGNAL_RUN_LAST,
    #    gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
    "muere": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,
        gobject.TYPE_PYOBJECT)),
    "muda": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, []),
    "reproduce": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}

    def __init__(self, sexo, ancho, alto, TIME):

        Sprite.__init__(self)
        gobject.GObject.__init__(self)

        self.acciones = ["camina", "gira", "quieto"]
        self.sexo = sexo
        self.alimento = 0.0
        self.agua = 0.0
        self.accion = "camina"
        self.contador = 0
        random.seed()
        self.sentido = random.choice(["+", "-"])

        random.seed()
        path = ""
        if self.sexo == "macho":
            self.imagen = random.choice(["cucaracha1.png", "cucaracha2.png"])
            path = os.path.join(BASE_PATH, "Imagenes", self.imagen)
            self.imagen = pygame.image.load(path)
        elif self.sexo == "hembra":
            self.imagen = random.choice(["cucaracha3.png", "cucaracha4.png"])
            path = os.path.join(BASE_PATH, "Imagenes", self.imagen)
            self.imagen = pygame.image.load(path)

        self.escala = (53, 40)
        imagen_escalada = pygame.transform.scale(self.imagen, self.escala)
        self.imagen_original = imagen_escalada.convert_alpha()

        self.dx = 0
        self.dy = 0
        self.angulo = 0
        self.velocidad = 8
        self.escena = pygame.Rect(35, 35, ancho - 70, alto - 70)

        self.image = self.imagen_original.copy()
        self.rect = self.image.get_bounding_rect()

        self.rect.centerx = self.escena.w / 2
        self.rect.centery = self.escena.h / 2

        random.seed()
        self.muerte = random.randrange(340, 365, 1)  # morirá este dia
        self.mudas = {
            10: (63, 50),
            50: (73, 60),
            60: (83, 70),
            90: (103, 90)}
        self.repro = range(91, 330, random.randrange(15, 30, 1))

        self.timer = Timer(TIME)
        self.edad = {
            "Años": 0,
            "Dias": 0,
            "Horas": 0}
        self.timer.connect("new-time", self.__update_time)

    def __update_time(self, widget, _dict):
        self.edad = dict(_dict)
        #self.emit("new-edad", self.edad)
        if self.edad["Dias"] in self.mudas.keys() and self.edad["Horas"] == 0:
            self.__set_muda(escala=self.mudas[self.edad["Dias"]])
            self.emit("muda")
        elif self.edad["Dias"] in self.repro and self.edad["Horas"] == 0:
            if self.sexo == "hembra":
                grupo = self.groups()
                cucas = grupo[0].sprites()
                for cuca in cucas:
                    if cuca != self and cuca.sexo == "macho" and \
                        cuca.edad["Dias"] >= 190:
                        self.emit("reproduce", (self.angulo,
                            self.rect.centerx, self.rect.centery))
                        break
        elif self.edad["Dias"] >= self.muerte:
            self.emit("muere", (self.angulo,
                self.rect.centerx, self.rect.centery), self.escala)
            self.morir()

        self.agua -= 1.0
        self.alimento -= 1.0
        if self.agua < -180.0 or self.alimento < -300.0:
            self.morir()

    def __actualizar_posicion(self):
        x = self.rect.centerx + self.dx
        y = self.rect.centery + self.dy
        # FIXME: Sin límite en el habitat
        #if not self.escena.colliderect(self.rect):
        #    if x > self.escena.width:
        #        x = 0
        #    elif x < 0:
        #        x = self.escena.width
        #    if y > self.escena.height:
        #        y = 0
        #    elif y < 0:
        #        y = self.escena.height
        #self.rect.centerx = x
        #self.rect.centery = y
        if self.escena.collidepoint(x, y):
            self.rect.centerx = x
            self.rect.centery = y
        else:
            if self.sentido == "+":
                self.angulo += int(0.7 * INDICE_ROTACION)
                if self.angulo > 360:
                    self.angulo -= 360
            else:
                self.angulo -= int(0.7 * INDICE_ROTACION)
                if self.angulo < -360:
                    self.angulo += 360
            self.image = pygame.transform.rotate(
                self.imagen_original, -self.angulo)
            self.dx = 0
            self.dx = 0

    def __get_vector(self, angulo):
        radianes = radians(angulo)
        x = int(cos(radianes) * self.velocidad)
        y = int(sin(radianes) * self.velocidad)
        return x, y

    def __set_muda(self, escala=(63, 50)):
        """
        Muda de exoesqueleto, cambia de tamaño.
        """
        self.escala = escala
        self.imagen_original = pygame.transform.scale(self.imagen, self.escala)
        self.image = pygame.transform.rotate(
            self.imagen_original, -self.angulo)
        x = self.rect.centerx
        y = self.rect.centery
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

    def __check_collide_alimentos(self, alimentos):
        valor = False
        for alimento in alimentos:
            if self.rect.colliderect(alimento.rect):
                if alimento.tipo == "agua":
                    if self.agua >= 250:
                        pass
                    elif self.agua < 250:
                        self.agua += 0.1
                        alimento.cantidad -= 0.1
                        valor = True
                elif alimento.tipo == "alimento":
                    if self.alimento >= 250:
                        pass
                    else:
                        self.alimento += 0.1
                        alimento.cantidad -= 0.1
                        valor = True
        return valor

    def __buscar(self, alimentos):
        random.seed()
        self.accion = random.choice(["camina", "gira"])
        if self.accion == "camina":
            self.__actualizar_posicion()
        elif self.accion == "gira":
            necesidad = "agua"
            alimento = False
            if self.alimento < self.agua:
                necesidad = "alimento"
            for alim in alimentos:
                if alim.tipo == necesidad:
                    alimento = alim
                    break
            if not alimento:
                alimento = alimentos[0]
            x2, y2 = alimento.rect.centerx, alimento.rect.centery
            x1, y1 = self.rect.centerx, self.rect.centery
            # http://www.vitutor.com/geo/rec/d_4.html
            self.angulo = int(degrees(atan2(y2 - y1, x2 - x1)))
            self.image = pygame.transform.rotate(
                self.imagen_original, -self.angulo)
            self.dx, self.dy = self.__get_vector(self.angulo)

    def __decidir(self):
        if self.contador >= 10:
            random.seed()
            self.accion = random.choice(self.acciones)
            self.contador = 0

        if self.accion == "gira":
            sent = random.randrange(1, 3, 1)
            if sent == 1:
                self.angulo -= int(0.7 * INDICE_ROTACION)
                if self.angulo < -360:
                    self.angulo += 360
            elif sent == 2:
                self.angulo += int(0.7 * INDICE_ROTACION)
                if self.angulo > 360:
                    self.angulo -= 360

            self.image = pygame.transform.rotate(
                self.imagen_original, -self.angulo)
            self.dx, self.dy = self.__get_vector(self.angulo)
            self.__actualizar_posicion()

        elif self.accion == "camina":
            self.__actualizar_posicion()

        self.contador += 1

    def update(self, alimentos):
        if self.__check_collide_alimentos(alimentos):
            return

        if alimentos:
            self.__buscar(alimentos)
        else:
            self.__decidir()

    def set_edad(self, dias, horas):
        """
        Para Forzar edad.
        """
        self.timer.dias = dias
        self.timer.horas = horas
        m = self.mudas.keys()
        mudas = []
        for x in m:
            mudas.append(int(x))
        mudas.sort()
        if self.timer.dias in range(0, mudas[0]):
            self.escala = (60, 50)
        elif self.timer.dias in range(mudas[0], mudas[1] + 1):
            self.escala = self.mudas[mudas[0]]
        elif self.timer.dias in range(mudas[1], mudas[2] + 1):
            self.escala = self.mudas[mudas[1]]
        elif self.timer.dias in range(mudas[2], mudas[3] + 1):
            self.escala = self.mudas[mudas[2]]
        else:
            self.escala = self.mudas[mudas[3]]
        self.__set_muda(escala=self.escala)

    def morir(self):
        self.timer.salir()
        self.emit("muere", (self.angulo, self.rect.centerx,
            self.rect.centery), self.escala)
        self.kill()


class Muerta(Sprite):

    def __init__(self, pos, escala, TIME):

        Sprite.__init__(self)

        path = os.path.join(BASE_PATH, "Imagenes", "muerta.png")
        imagen = pygame.image.load(path)
        imagen_escalada = pygame.transform.scale(imagen, escala)
        self.image = imagen_escalada.convert_alpha()
        self.rect = self.image.get_rect()

        self.image = pygame.transform.rotate(self.image, -pos[0])
        self.rect.centerx = pos[1]
        self.rect.centery = pos[2]

        self.timer = Timer(TIME)
        self.edad = {
            "Años": 0,
            "Dias": 0,
            "Horas": 0}
        self.timer.connect("new-time", self.__update_time)

    def __update_time(self, widget, _dict):
        self.edad = dict(_dict)
        if self.edad["Dias"] >= 3:
            self.morir()

    def morir(self):
        self.timer.salir()
        self.kill()
