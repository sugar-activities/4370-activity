#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Widgets.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

import os
import gtk
import gobject
import pygame
from pygame.sprite import Sprite
from JAMediaImagenes.ImagePlayer import ImagePlayer
from JAMediaReproductor.JAMediaReproductor import JAMediaReproductor

BASE_PATH = os.path.dirname(__file__)


def get_separador(draw=False, ancho=0, expand=False):
    separador = gtk.SeparatorToolItem()
    separador.props.draw = draw
    separador.set_size_request(ancho, -1)
    separador.set_expand(expand)
    return separador


def describe_archivo(archivo):
    import commands
    datos = commands.getoutput('file -ik %s%s%s' % ("\"", archivo, "\""))
    retorno = ""
    for dat in datos.split(":")[1:]:
        retorno += " %s" % (dat)
    return retorno


class Widget_Leccion(gtk.Dialog):

    def __init__(self, parent=None, lectura=""):

        gtk.Dialog.__init__(self, parent=parent,
            buttons=("Cerrar", gtk.RESPONSE_ACCEPT))

        self.set_decorated(False)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
        self.set_border_width(15)

        self.panel = Panel(lectura)
        self.vbox.pack_start(self.panel, True, True, 0)
        self.vbox.show_all()

        rect = parent.get_allocation()
        self.set_size_request(rect.width, rect.height)

        parent.connect("check-resize", self.__resize)

    def __resize(self, parent):
        rect = parent.get_allocation()
        self.set_size_request(rect.width, rect.height)

    def stop(self):
        for visor in self.panel.players:
            visor.player.stop()


class Panel(gtk.HPaned):

    def __init__(self, lectura):

        gtk.HPaned.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))

        dirpath = False
        if lectura == "ciclo vital":
            dirpath = os.path.join(BASE_PATH, "Lecturas", "001-Ciclo-Vital")
        elif lectura == "muda de exoesqueleto":
            dirpath = os.path.join(BASE_PATH, "Lecturas", "002-Muda")
        elif lectura == "reproducción":
            dirpath = os.path.join(BASE_PATH, "Lecturas", "003-Reproducion")
        elif lectura == "plaga":
            dirpath = os.path.join(BASE_PATH, "Lecturas", "004-Plaga")
        elif lectura == "muerte":
            dirpath = os.path.join(BASE_PATH, "Lecturas", "005-Muerte")
        elif lectura == "lectura general":
            dirpath = os.path.join(BASE_PATH, "Lecturas", "General")
        elif lectura == "extinción":
            dirpath = os.path.join(BASE_PATH, "Lecturas", "Extincion")

        self.players = []
        vbox = gtk.VBox()
        for archivo in sorted(os.listdir(dirpath)):
            tipo = describe_archivo(os.path.join(dirpath, archivo))
            if 'video' in tipo or 'application/ogg' in tipo or "image" in tipo:
                drawing = Visor(os.path.join(dirpath, archivo))
                self.players.append(drawing)
                vbox.pack_start(drawing, True, True, 0)

        self.pack1(vbox, resize=True, shrink=True)

        self.lectura = gtk.TextView()
        self.lectura.set_editable(False)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.add(self.lectura)
        self.pack2(scroll, resize=False, shrink=False)

        path = os.path.join(dirpath, "lectura.txt")
        arch = open(path, "r")
        text = arch.read()
        arch.close()
        self.lectura.get_buffer().set_text(text)

        self.show_all()


class Visor(gtk.DrawingArea):

    def __init__(self, archivo):

        gtk.DrawingArea.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))

        self.archivo = archivo
        self.player = False

        self.connect("realize", self.__realize)

        self.show_all()

    def __realize(self, widget):
        tipo = describe_archivo(self.archivo)
        if "image" in tipo:
            self.player = ImagePlayer(self)
        elif 'video' in tipo or 'application/ogg':
            self.player = JAMediaReproductor(self.get_property('window').xid)
        gobject.idle_add(self.player.load, self.archivo)


class Cursor(Sprite):

    def __init__(self, tipo):

        Sprite.__init__(self)

        self.tipo = tipo

        path = ""
        if self.tipo == "agua":
            path = os.path.join(BASE_PATH, "Imagenes", "jarra.png")
        elif self.tipo == "alimento":
            path = os.path.join(BASE_PATH, "Imagenes", "pan.png")

        self.image = pygame.image.load(path)
        self.rect = self.image.get_bounding_rect()

    def pos(self, pos):
        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]


class Alimento(Sprite):

    def __init__(self, tipo, pos):

        Sprite.__init__(self)

        self.tipo = tipo
        self.cantidad = 1500.0

        path = ""
        if self.tipo == "agua":
            path = os.path.join(BASE_PATH, "Imagenes", "jarra.png")
        elif self.tipo == "alimento":
            path = os.path.join(BASE_PATH, "Imagenes", "pan.png")

        self.image = pygame.image.load(path)
        self.rect = self.image.get_bounding_rect()
        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]

    def update(self):
        if self.cantidad <= 0.0:
            self.kill()


class Toolbar(gtk.EventBox):

    def __init__(self):

        gtk.EventBox.__init__(self)

        toolbar = gtk.Toolbar()

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
        toolbar.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        imagen = gtk.Image()
        icono = os.path.join(BASE_PATH, "Imagenes", "cucaracha2.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icono,
            -1, 24)
        imagen.set_from_pixbuf(pixbuf)
        imagen.show()
        item = gtk.ToolItem()
        item.add(imagen)
        toolbar.insert(item, -1)

        item = gtk.ToolItem()
        self.labelcucas = gtk.Label(" 0H + 0M = 0")
        self.labelcucas.modify_fg(gtk.STATE_NORMAL,
            gtk.gdk.color_parse("#000000"))
        self.labelcucas.show()
        item.add(self.labelcucas)
        toolbar.insert(item, -1)

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        imagen = gtk.Image()
        icono = os.path.join(BASE_PATH, "Imagenes", "huevos.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icono,
            -1, 24)
        imagen.set_from_pixbuf(pixbuf)
        imagen.show()
        item = gtk.ToolItem()
        item.add(imagen)
        toolbar.insert(item, -1)

        item = gtk.ToolItem()
        self.labelootecas = gtk.Label(" = 0")
        self.labelootecas.modify_fg(gtk.STATE_NORMAL,
            gtk.gdk.color_parse("#000000"))
        self.labelootecas.show()
        item.add(self.labelootecas)
        toolbar.insert(item, -1)

        imagen = gtk.Image()
        icono = os.path.join(BASE_PATH, "Imagenes", "jarra.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icono, -1, 24)
        imagen.set_from_pixbuf(pixbuf)
        imagen.show()
        item = gtk.ToolItem()
        item.add(imagen)
        toolbar.insert(item, -1)

        item = gtk.ToolItem()
        self.labelagua = gtk.Label(" = 0")
        self.labelagua.modify_fg(gtk.STATE_NORMAL,
            gtk.gdk.color_parse("#000000"))
        self.labelagua.show()
        item.add(self.labelagua)
        toolbar.insert(item, -1)

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        imagen = gtk.Image()
        icono = os.path.join(BASE_PATH, "Imagenes", "pan.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icono, -1, 24)
        imagen.set_from_pixbuf(pixbuf)
        imagen.show()
        item = gtk.ToolItem()
        item.add(imagen)
        toolbar.insert(item, -1)

        item = gtk.ToolItem()
        self.labelalimento = gtk.Label(" = 0")
        self.labelalimento.modify_fg(gtk.STATE_NORMAL,
            gtk.gdk.color_parse("#000000"))
        self.labelalimento.show()
        item.add(self.labelalimento)
        toolbar.insert(item, -1)

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = gtk.ToolItem()
        self.labeltiempo = gtk.Label(" Años: 0 Dias: 0 Horas: 0")
        self.labeltiempo.modify_fg(gtk.STATE_NORMAL,
            gtk.gdk.color_parse("#000000"))
        self.labeltiempo.show()
        item.add(self.labeltiempo)
        toolbar.insert(item, -1)

        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.add(toolbar)
        self.show_all()

    def set_info(self, infocucas, infoootecas, infoagua, infoalimento, tiempo):
        self.labelcucas.set_text(infocucas)
        self.labelootecas.set_text(infoootecas)
        self.labelagua.set_text(infoagua)
        self.labelalimento.set_text(infoalimento)
        self.labeltiempo.set_text(tiempo)


class ToolbarEstado(gtk.EventBox):

    __gsignals__ = {
    "volumen": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_FLOAT, ))}

    def __init__(self):

        gtk.EventBox.__init__(self)

        toolbar = gtk.Toolbar()

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
        toolbar.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = gtk.ToolItem()
        self.label = gtk.Label()
        self.label.modify_fg(gtk.STATE_NORMAL,
            gtk.gdk.color_parse("#000000"))
        self.label.show()
        item.add(self.label)
        toolbar.insert(item, -1)

        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        item = gtk.ToolItem()
        self.volumen = ControlVolumen()
        self.volumen.connect("value-changed", self.__value_changed)
        self.volumen.show()
        item.add(self.volumen)
        toolbar.insert(item, -1)

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.add(toolbar)
        self.show_all()

    def __value_changed(self, widget, valor):
        self.emit('volumen', valor)

    def set_info(self, info):
        self.label.set_text(info)


class ControlVolumen(gtk.VolumeButton):

    __gsignals__ = {
    "volumen": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_FLOAT, ))}

    def __init__(self):

        gtk.VolumeButton.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))

        self.connect("value-changed", self.__value_changed)
        self.show_all()

        self.set_value(0.1)

    def __value_changed(self, widget, valor):
        valor = int(valor * 10)
        self.emit('volumen', valor)
