#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Juego.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

import os
import gobject
import pygame
import gtk
import random
import platform

from pygame.locals import HWSURFACE
from Cucaracha import Cucaracha
from Cucaracha import Muerta
from Huevos import Huevo
from Timer import Timer
from Widgets import Cursor
from Widgets import Alimento

RESOLUCION_INICIAL = (800, 600)
TIME = 1
MAX = 15
BASE_PATH = os.path.dirname(__file__)
BASE_PATH = os.path.dirname(BASE_PATH)
OLPC = 'olpc' in platform.platform()

gobject.threads_init()


class CucaraSims(gobject.GObject):

    __gsignals__ = {
    "exit": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, []),
    "lectura": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_STRING, )),
    "clear-cursor-gtk": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, []),
    "update": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
    "puntos": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_INT, ))}

    def __init__(self):

        gobject.GObject.__init__(self)

        self.RESOLUCION_INICIAL = RESOLUCION_INICIAL
        self.resolucionreal = RESOLUCION_INICIAL
        self.ventana_real = False
        self.escenario = False
        self.ventana = False
        self.reloj = False
        self.estado = 0
        self.timer = False
        self.edad = {
            "Años": 0,
            "Dias": 0,
            "Horas": 0}

        self.musica = False

        self.cucas = pygame.sprite.RenderUpdates()
        self.huevos = pygame.sprite.RenderUpdates()
        self.muertas = pygame.sprite.RenderUpdates()
        self.mouse = pygame.sprite.GroupSingle()
        self.alimentos = pygame.sprite.RenderUpdates()

        self.cursor_agua = False
        self.cursor_pan = False

    def __handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.emit("exit")
                    return
            elif event.type == pygame.MOUSEMOTION:
                cursor = self.mouse.sprites()
                if cursor:
                    cursor[0].pos(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    cursor = self.mouse.sprites()
                    alimentos = self.alimentos.sprites()
                    if cursor:
                        tipo = cursor[0].tipo
                        self.set_cursor(False, False)
                        for alimento in alimentos:
                            if alimento.tipo == tipo:
                                self.alimentos.remove(alimento)
                                alimento.kill()
                        self.alimentos.add(Alimento(tipo, (event.pos)))
                        self.emit("clear-cursor-gtk")
                    else:
                        # Fixme: Casos a Considerar:
                        # Click sobre Cuca
                        for alimento in alimentos:
                            if alimento.rect.collidepoint(event.pos):
                                self.alimentos.remove(alimento)
                                alimento.kill()
                                self.emit("clear-cursor-gtk")
                        # Click sobre ooteca
                        # Click sobre muerta
                        # Click sobre el fondo
        pygame.event.clear()

    def __stop_timer(self, objeto):
        #objeto.disconnect_by_func(self.__update_edad)
        try:
            objeto.disconnect_by_func(self.__event_muerte)
        except:
            pass
        try:
            objeto.disconnect_by_func(self.__event_muda)
        except:
            pass
        try:
            objeto.disconnect_by_func(self.__event_repro)
        except:
            pass
        objeto.morir()

    def __connect_signals(self, objeto):
        #objeto.connect("new-edad", self.__update_edad)
        objeto.connect("muere", self.__event_muerte)
        objeto.connect("muda", self.__event_muda)
        objeto.connect("reproduce", self.__event_repro)

    def __update_time(self, widget, _dict):
        """
        Actualiza el Tiempo de Juego.
        """
        self.edad = dict(_dict)
        dic = dict(_dict)
        machos = 0
        hembras = 0
        cucas = self.cucas.sprites()
        for cuca in cucas:
            if cuca.sexo == "macho":
                machos += 1
            elif cuca.sexo == "hembra":
                hembras += 1
        alimentos = self.alimentos.sprites()
        alimento = 0
        agua = 0
        for alim in alimentos:
            if alim.tipo == "alimento":
                alimento = alim.cantidad
            elif alim.tipo == "agua":
                agua = alim.cantidad
        dic["cucas"] = len(cucas)
        dic["hembras"] = hembras
        dic["machos"] = machos
        dic["ootecas"] = len(self.huevos.sprites())
        dic["alimento"] = alimento
        dic["agua"] = agua
        self.emit("update", dic)

    def __event_muda(self, cuca):
        """
        Una Cucaracha Muda su Exoesqueleto.
        """
        self.emit("lectura", "muda de exoesqueleto")

    def __event_muerte(self, cuca, pos, escala):
        """
        Una Cucaracha Muere.
        """
        self.muertas.add(Muerta(pos, escala, TIME))
        self.emit("lectura", "muerte")

    def __event_repro(self, cuca, pos):
        """
        Cucarachas ponen Huevos.
        """
        huevo = Huevo(pos, TIME)
        self.huevos.add(huevo)
        huevo.connect("nacer", self.__event_nacer)
        self.emit("lectura", "reproducción")

    def __event_nacer(self, huevo, h_m, pos):
        """
        Una Ooteca eclosiona.
        """
        hembras, machos = h_m
        for h in range(hembras):
            cucaracha = Cucaracha("hembra", RESOLUCION_INICIAL[0],
                RESOLUCION_INICIAL[1], TIME)
            self.cucas.add(cucaracha)
            cucaracha.rect.centerx = pos[0]
            cucaracha.rect.centery = pos[1]
        for m in range(machos):
            cucaracha = Cucaracha("macho", RESOLUCION_INICIAL[0],
                RESOLUCION_INICIAL[1], TIME)
            self.cucas.add(cucaracha)
            cucaracha.rect.centerx = pos[0]
            cucaracha.rect.centery = pos[1]
        map(self.__connect_signals, self.cucas.sprites())
        self.emit("lectura", "ciclo vital")

    #def __update_edad(self, widget, _dict):
    #    print _dict

    def __pausar(self, objeto):
        objeto.timer.new_handle(False)

    def __des_pausar(self, objeto):
        objeto.timer.new_handle(True)

    def __control_de_poblacion(self):
        if len(self.cucas.sprites()) > 15:
            self.emit("lectura", "plaga")
            sprites = self.cucas.sprites()
            puntos = 0
            while len(sprites) > 15:
                sprite = random.choice(sprites)
                sprites.remove(sprite)
                sprite.timer.salir()
                sprite.kill()
                puntos += 1
            self.emit("puntos", puntos)
        else:
            huevos = self.huevos.sprites()
            cucas = self.cucas.sprites()
            machos = 0
            hembras = 0
            rh = 0
            for cuca in cucas:
                if cuca.sexo == "macho":
                    machos += 1
                elif cuca.sexo == "hembra":
                    hembras += 1
                    if cuca.edad["Dias"] < 331:
                        rh += 1
            if not huevos and (not rh and not machos):
                self.emit("lectura", "extinción")

    def set_volumen(self, widget, volumen):
        pygame.mixer.music.set_volume(volumen)

    def set_cursor(self, widget, tipo):
        """
        Cuando el usuario selecciona alimento o agua en la interfaz gtk,
        se setea el cursor tambien en pygame, esto tambien sucede cuando el
        mouse entra o sale del drawing donde dibuja pygame.
        """
        self.mouse.empty()
        if tipo:
            pygame.mouse.set_visible(False)
            if tipo == "agua":
                self.cursor_agua.pos((-100, -100))
                self.mouse.add(self.cursor_agua)
            elif tipo == "alimento":
                self.cursor_pan.pos((-100, -100))
                self.mouse.add(self.cursor_pan)
        else:
            pygame.mouse.set_visible(True)

    def pause(self):
        map(self.__pausar, self.cucas.sprites())
        map(self.__pausar, self.huevos.sprites())
        map(self.__pausar, self.muertas.sprites())
        self.timer.new_handle(False)

    def unpause(self):
        map(self.__des_pausar, self.cucas.sprites())
        map(self.__des_pausar, self.huevos.sprites())
        map(self.__des_pausar, self.muertas.sprites())
        self.timer.new_handle(True)

    def run(self):
        print "Corriendo CucaraSims . . ."
        self.estado = 1
        self.ventana.blit(self.escenario, (0, 0))
        self.ventana_real.blit(pygame.transform.scale(self.ventana,
            self.resolucionreal), (0, 0))
        pygame.display.update()

        try:
            while self.estado:
                if not OLPC:
                    self.reloj.tick(35)
                self.__control_de_poblacion()
                while gtk.events_pending():
                    gtk.main_iteration()
                self.huevos.clear(self.ventana, self.escenario)
                self.alimentos.clear(self.ventana, self.escenario)
                self.muertas.clear(self.ventana, self.escenario)
                self.cucas.clear(self.ventana, self.escenario)
                self.mouse.clear(self.ventana, self.escenario)
                #self.huevos.update()
                #self.muertas.update()
                self.cucas.update(self.alimentos.sprites())
                self.alimentos.update()
                self.mouse.update()
                self.__handle_event()
                self.huevos.draw(self.ventana)
                self.alimentos.draw(self.ventana)
                self.muertas.draw(self.ventana)
                self.cucas.draw(self.ventana)
                self.mouse.draw(self.ventana)
                self.ventana_real.blit(pygame.transform.scale(
                    self.ventana, self.resolucionreal), (0, 0))
                pygame.display.update()
                #pygame.time.wait(3)
        except:
            pass

    def salir(self, widget=False):
        self.emit("clear-cursor-gtk")
        self.estado = 0
        self.timer.salir()
        map(self.__stop_timer, self.cucas.sprites())
        map(self.__stop_timer, self.huevos.sprites())
        pygame.quit()

    def escalar(self, resolucion):
        self.resolucionreal = resolucion

    def config(self):
        pygame.init()
        self.reloj = pygame.time.Clock()

        from pygame.locals import MOUSEMOTION
        from pygame.locals import MOUSEBUTTONUP
        from pygame.locals import MOUSEBUTTONDOWN
        from pygame.locals import JOYAXISMOTION
        from pygame.locals import JOYBALLMOTION
        from pygame.locals import JOYHATMOTION
        from pygame.locals import JOYBUTTONUP
        from pygame.locals import JOYBUTTONDOWN
        from pygame.locals import VIDEORESIZE
        from pygame.locals import VIDEOEXPOSE
        from pygame.locals import USEREVENT
        from pygame.locals import QUIT
        from pygame.locals import ACTIVEEVENT
        from pygame.locals import KEYDOWN
        from pygame.locals import KEYUP

        pygame.event.set_blocked([
            JOYAXISMOTION, JOYBALLMOTION, JOYHATMOTION, JOYBUTTONUP,
            JOYBUTTONDOWN, ACTIVEEVENT, USEREVENT])
        pygame.event.set_allowed([QUIT, VIDEORESIZE, VIDEOEXPOSE,
            KEYDOWN, KEYUP, MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN])
        pygame.key.set_repeat(15, 15)

        pygame.display.set_mode(
            (0, 0), pygame.DOUBLEBUF | pygame.FULLSCREEN, 0)

        pygame.display.set_caption("CucaraSims")

        path = os.path.join(BASE_PATH, "CucaraSims", "Imagenes", "arena1.png")
        imagen = pygame.image.load(path)
        self.escenario = pygame.transform.scale(
            imagen, RESOLUCION_INICIAL).convert_alpha()

        self.ventana = pygame.Surface((RESOLUCION_INICIAL[0],
            RESOLUCION_INICIAL[1]), flags=HWSURFACE)
        self.ventana_real = pygame.display.get_surface()

        self.timer = Timer(TIME)  # 1 segundo == 1 hora
        self.timer.connect("new-time", self.__update_time)

        for x in range(2):
            cucaracha = Cucaracha("macho", RESOLUCION_INICIAL[0],
                RESOLUCION_INICIAL[1], TIME)
            random.seed()
            dias = random.randrange(90, 325, 1)
            horas = random.randrange(1, 24, 1)
            cucaracha.set_edad(dias, horas)
            self.cucas.add(cucaracha)

        for x in range(2):
            cucaracha = Cucaracha("hembra", RESOLUCION_INICIAL[0],
                RESOLUCION_INICIAL[1], TIME)
            random.seed()
            dias = 90
            horas = random.randrange(1, 24, 1)
            cucaracha.set_edad(dias, horas)
            self.cucas.add(cucaracha)

        map(self.__connect_signals, self.cucas.sprites())

        path = os.path.join(BASE_PATH, "CucaraSims", "Sonidos", "musica.ogg")
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1, 0.0)
        pygame.mixer.music.set_volume(0.20)

        self.cursor_agua = Cursor("agua")
        self.cursor_pan = Cursor("alimento")
