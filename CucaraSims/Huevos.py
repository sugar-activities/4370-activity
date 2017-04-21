#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Huevos.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

import os
import gobject
import pygame
from pygame.sprite import Sprite
import random

from Timer import Timer

BASE_PATH = os.path.dirname(__file__)


class Huevo(Sprite, gobject.GObject):

    __gsignals__ = {
    "nacer": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,
        gobject.TYPE_PYOBJECT))}

    def __init__(self, pos, TIME):

        Sprite.__init__(self)
        gobject.GObject.__init__(self)

        path = os.path.join(BASE_PATH, "Imagenes", "huevos.png")
        self.imagen = pygame.image.load(path)
        self.imagen_original = self.imagen.convert_alpha()

        self.image = self.imagen_original.copy()
        self.image = pygame.transform.rotate(
            self.imagen_original, -pos[0])
        self.rect = self.image.get_bounding_rect()

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
        if self.edad["Dias"] >= 9:
            random.seed()
            huevos = random.randrange(10, 41, 1)
            hembras = random.randrange(0, huevos, 1)
            machos = huevos - hembras
            self.emit("nacer", (hembras, machos),
                (self.rect.centerx, self.rect.centery))
            self.morir()

    def morir(self):
        self.timer.salir()
        self.kill()
