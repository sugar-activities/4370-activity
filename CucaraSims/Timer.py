#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Timer.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

import time
import gobject


class Timer(gobject.GObject):

    __gsignals__ = {
    "new-time": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}

    def __init__(self, demora):

        gobject.GObject.__init__(self)

        self.actualizador = False
        self.init = int(time.time())

        self.demora = demora
        self.anios = 0
        self.dias = 0
        self.horas = 0
        self.segundos = 0

        self.new_handle(True)

    def __handle(self):
        self.segundos = int(time.time()) - self.init
        if self.segundos >= self.demora:
            self.init = int(time.time())
            self.horas += 1
        if self.horas >= 24:
            self.horas = 0
            self.dias += 1
        if self.dias >= 365:
            self.dias = 0
            self.anios += 1
        self.emit("new-time",
            {"Años": self.anios,
            "Dias": self.dias,
            "Horas": self.horas})
        return bool(self.actualizador)

    def new_handle(self, reset):
        if self.actualizador:
            gobject.source_remove(self.actualizador)
            self.actualizador = False
        if reset:
            self.actualizador = gobject.timeout_add(1000, self.__handle)

    def salir(self):
        self.new_handle(False)
