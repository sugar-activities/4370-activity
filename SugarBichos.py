#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   SugarBichos.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

import os
import sys
import gtk
import gobject

from EventTraductor.EventTraductor import KeyPressTraduce
from EventTraductor.EventTraductor import KeyReleaseTraduce

from Intro.Intro import Intro
from Widgets import Escenario
from CantaBichos.CantaBichos import CantaBichos
from CucaraSims.CucaraSims import CucaraSimsWidget
from CucaraSims.Juego import CucaraSims
from OjosCompuestos.OjosCompuestos import OjosCompuestos

from sugar.activity.activity import Activity


class Bichos(Activity):

    def __init__(self, handle):

        Activity.__init__(self, handle, False)
        self.socket = gtk.Socket()
        self.set_canvas(self.socket)
        self.interfaz = Interfaz()
        self.socket.add_id(self.interfaz.get_id())
        self.show_all()

        self.connect("key-press-event", self.interfaz.key_press_even)
        self.connect("key-release-event", self.interfaz.key_release_even)

    def read_file(self, file_path):
        pass

    def write_file(self, file_path):
        pass


class Interfaz(gtk.Plug):

    def __init__(self):

        gtk.Plug.__init__(self, 0L)

        self.juego = False
        self.widgetjuego = False

        self.connect("delete-event", self.__salir)
        self.connect("realize", self.__do_realize)

        self.show_all()

    def key_press_even(self, widget, event):
        if self.juego:
            KeyPressTraduce(event)
        else:
            if gtk.gdk.keyval_name(event.keyval) == "Escape":
                self.widgetjuego.salir()
                self.switch(False, 1)
        return False

    def key_release_even(self, widget, event):
        if self.juego:
            KeyReleaseTraduce(event)
        return False

    def __do_realize(self, widget):
        self.switch(False, 1)

    def __salir(self, widget=None, event=None):
        sys.exit(0)

    def __redraw(self, widget, size):
        if self.juego:
            self.juego.escalar(size)

    def __run_intro(self, escenario):
        xid = escenario.get_property('window').xid
        os.putenv('SDL_WINDOWID', str(xid))
        self.juego = Intro()
        self.juego.connect("exit", self.__salir)
        self.juego.connect("go", self.__run_games)
        self.juego.config()
        self.juego.run()
        return False

    def __run_cucarasims(self, escenario):
        xid = escenario.get_property('window').xid
        os.putenv('SDL_WINDOWID', str(xid))
        self.juego = CucaraSims()
        self.widgetjuego.connect("set-cursor", self.juego.set_cursor)
        self.widgetjuego.connect("exit", self.__dialog_exit_game, "CucaraSims")
        self.widgetjuego.connect("volumen", self.juego.set_volumen)
        self.juego.connect("exit", self.__dialog_exit_game, "CucaraSims")
        self.juego.connect("lectura", self.widgetjuego.run_lectura)
        self.juego.connect("clear-cursor-gtk", self.widgetjuego.clear_cursor)
        self.juego.connect("update", self.widgetjuego.update)
        self.juego.connect("puntos", self.widgetjuego.puntos)
        self.juego.config()
        self.juego.run()
        return False

    def __dialog_exit_game(self, widget, juego_name):
        self.juego.pause()
        dialog = gtk.Dialog(parent=self,
            buttons=("Salir", gtk.RESPONSE_ACCEPT,
            "Cancelar", gtk.RESPONSE_CANCEL))
        dialog.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
        label = gtk.Label("Salir de %s" % juego_name)
        label.show()
        dialog.set_border_width(10)
        dialog.vbox.pack_start(label, True, True, 0)
        resp = dialog.run()
        dialog.destroy()
        if resp == gtk.RESPONSE_ACCEPT:
            self.__run_games(False, "menu")
            return
        self.juego.unpause()

    def __mouse_enter(self, widget, valor):
        """
        Cuando el mouse entra o sale del drawing donde dibuja pygame, setea
        el cursor para que no siga en pantalla en pygame si el mouse está fuera
        """
        if self.juego and not valor:
            self.juego.set_cursor(False, False)
        elif self.juego and valor:
            self.juego.set_cursor(False, self.widgetjuego.cursor_tipo)

    def __run_games(self, intro, game):
        if self.juego:
            self.juego.salir()
            del(self.juego)
            self.juego = False
            self.queue_draw()
        if game == "menu":
            self.switch(False, 1)
        elif game == "cucarasims":
            self.switch(False, 2)
        elif game == "cantores":
            self.switch(False, 3)
        elif game == "ojos":
            self.switch(False, 4)

    def switch(self, widget, valor):
        for child in self.get_children():
            self.remove(child)
            child.destroy()
        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))

        if valor == 1:
            self.widgetjuego = Escenario()
            self.widgetjuego.connect("new-size", self.__redraw)
            self.add(self.widgetjuego)
            gobject.idle_add(self.__run_intro, self.widgetjuego)

        elif valor == 2:
            self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
            escenario = Escenario()
            escenario.modify_bg(
                gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))
            escenario.connect("new-size", self.__redraw)
            escenario.connect("mouse-enter", self.__mouse_enter)
            self.widgetjuego = CucaraSimsWidget(escenario)
            self.add(self.widgetjuego)
            gobject.idle_add(self.__run_cucarasims, escenario)

        elif valor == 3:
            self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
            self.widgetjuego = CantaBichos()
            self.add(self.widgetjuego)

        elif valor == 4:
            self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
            escenario = Escenario()
            escenario.modify_bg(
                gtk.STATE_NORMAL, gtk.gdk.color_parse("#000000"))
            self.widgetjuego = OjosCompuestos(escenario)
            self.add(self.widgetjuego)
