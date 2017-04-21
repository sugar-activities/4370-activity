#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gtk
import gobject

from player import Player

BASE_PATH = os.path.dirname(__file__)


class CantaBichos(gtk.Table):

    def __init__(self):

        gtk.Table.__init__(self, rows=5, columns=6, homogeneous=True)

        print "Corriendo Canta Bichos . . ."

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
        self.set_property("column-spacing", 2)
        self.set_property("row-spacing", 2)
        self.set_border_width(2)

        archivos = []
        for arch in os.listdir(os.path.join(BASE_PATH, "Imagenes")):
            archivos.append(os.path.join(os.path.join(
                BASE_PATH, "Imagenes", arch)))

        index = 0
        for col in range(0, 6):
            for row in range(0, 5):
                boton = Button(archivos[index])
                self.attach(boton, col, col + 1, row, row + 1)
                index += 1

        self.connect("realize", self.__realize)
        self.show_all()

    def __realize(self, widget):
        gobject.idle_add(self.__dialog_run)

    def __dialog_run(self):
        dialog = Dialog(parent=self.get_toplevel(),
            text="Presiona Escape Cuando Desees Salir")
        dialog.run()
        return False

    def get_sounds(self):
        sounds = 0
        for child in self.get_children():
            if child.active:
                sounds += 1
        return sounds

    def salir(self):
        for child in self.get_children():
            child.salir()


class Button(gtk.EventBox):

    def __init__(self, image_path):

        gtk.EventBox.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#778899"))

        audio = "%s.%s" % (os.path.basename(image_path).split(".")[0], "ogg")
        self.sonido = os.path.join(BASE_PATH, "Sonidos", audio)
        self.player = Player()
        self.player.connect("endfile", self.__replay)

        self.image_path = image_path
        self.nombre = os.path.basename(self.image_path).split(".")[0]
        self.active = False

        boton = gtk.ToolButton()
        boton.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#778899"))

        self.imagen = gtk.Image()
        self.imagen.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#778899"))
        boton.set_icon_widget(self.imagen)

        boton.connect("size-allocate", self.__size_request)
        boton.connect("expose-event", self.__redraw)
        boton.connect("clicked", self.__clicked)

        self.add(boton)
        self.show_all()

    def __replay(self, player):
        if self.player:
            self.player.stop()
            self.player.disconnect_by_func(self.__replay)
            del(self.player)
            self.player = False
        self.player = Player()
        self.player.connect("endfile", self.__replay)
        self.player.load(self.sonido)

    def __clicked(self, widget):
        if self.active == False:
            if self.get_parent().get_sounds() < 8:
                self.active = True
                self.modify_bg(
                    gtk.STATE_NORMAL, gtk.gdk.color_parse("#e9b96e"))
                self.imagen.modify_bg(
                    gtk.STATE_NORMAL, gtk.gdk.color_parse("#e9b96e"))
                self.player.load(self.sonido)
            else:
                dialog = Dialog(parent=self.get_toplevel(),
                    text="No Puedes Activar mas de 8 Sonidos Simultaneos")
                dialog.run()

        elif self.active == True:
            self.active = False
            self.modify_bg(
                gtk.STATE_NORMAL, gtk.gdk.color_parse("#778899"))
            self.imagen.modify_bg(
                gtk.STATE_NORMAL, gtk.gdk.color_parse("#778899"))
            self.player.stop()

    def __size_request(self, widget, event):
        rect = self.get_allocation()
        gobject.idle_add(self.imagen.set_from_pixbuf,
            gtk.gdk.pixbuf_new_from_file_at_size(
            self.image_path, rect.width, -1))

    def __redraw(self, widget, event):
        rect = self.get_allocation()
        gobject.idle_add(self.imagen.set_from_pixbuf,
            gtk.gdk.pixbuf_new_from_file_at_size(
            self.image_path, rect.width, -1))

    def salir(self):
        self.player.stop()


class Dialog(gtk.Dialog):

    def __init__(self, parent=None, text=""):

        gtk.Dialog.__init__(self, parent=parent)

        self.set_decorated(False)
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
        self.set_border_width(15)

        label = gtk.Label(text)

        self.vbox.pack_start(label, True, True, 0)
        self.vbox.show_all()

        gobject.timeout_add(3000, self.destroy)
