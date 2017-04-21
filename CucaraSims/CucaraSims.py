#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   CucaraSims.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

import os
import gtk
import gobject

from Widgets import Widget_Leccion
from Widgets import Toolbar
from Widgets import ToolbarEstado

BASE_PATH = os.path.dirname(__file__)


class CucaraSimsWidget(gtk.HPaned):

    __gsignals__ = {
    "exit": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, []),
    "set-cursor": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
    "volumen": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_FLOAT, ))}

    def __init__(self, escenario):

        gtk.HPaned.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))

        self.lecciones = []

        self.toolbar = Toolbar()
        vbox = gtk.VBox()
        vbox.pack_start(self.toolbar, False, False, 0)
        vbox.pack_start(escenario, True, True, 0)
        self.toolbarestado = ToolbarEstado()
        vbox.pack_end(self.toolbarestado, False, False, 0)

        self.pack1(vbox, resize=True, shrink=True)
        self.derecha = Derecha()
        self.pack2(self.derecha, resize=False, shrink=False)

        self.toolbarestado.connect("volumen", self.__volumen_changed)
        self.derecha.connect("select", self.__set_cursor)
        self.derecha.connect("lectura", self.__run_lectura)

        self.show_all()

        self.agua_cursor = False
        self.alimento_cursor = False
        self.cursor_root = False
        self.cursor_tipo = False

        gobject.idle_add(self.__config_cursors)

    def __volumen_changed(self, widget, valor):
        self.emit('volumen', valor)

    def __config_cursors(self):
        icono = os.path.join(BASE_PATH, "Imagenes", "jarra.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icono, -1, 24)
        self.agua_cursor = gtk.gdk.Cursor(
            gtk.gdk.display_get_default(), pixbuf, 0, 0)

        icono = os.path.join(BASE_PATH, "Imagenes", "pan.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icono, -1, 24)
        self.alimento_cursor = gtk.gdk.Cursor(
            gtk.gdk.display_get_default(), pixbuf, 0, 0)

        self.cursor_root = self.get_toplevel().get_property(
            "window").get_cursor()
        return False

    def __set_cursor(self, widget, tipo):
        """
        Cuando el usuario selecciona alimento o agua en la interfaz gtk,
        setea el cursor y manda una señal para hacerlo tambien en pygame.
        """
        win = self.get_toplevel().get_property("window")
        if tipo == "agua":
            if self.cursor_tipo == "agua":
                win.set_cursor(self.cursor_root)
                self.cursor_tipo = False
            else:
                win.set_cursor(self.agua_cursor)
                self.cursor_tipo = "agua"
        elif tipo == "alimento":
            if self.cursor_tipo == "alimento":
                win.set_cursor(self.cursor_root)
                self.cursor_tipo = False
            else:
                win.set_cursor(self.alimento_cursor)
                self.cursor_tipo = "alimento"
        else:
            win.set_cursor(self.cursor_root)
            self.cursor_tipo = False
        self.emit("set-cursor", self.cursor_tipo)

    def __run_lectura(self, derecha, lectura):
        """
        La Interfaz gtk manda abrir una lectura.
        """
        if lectura == "salir":
            self.emit("exit")
            return
        try:
            self.get_toplevel().juego.pause()
        except:
            # Para Sugar
            self.get_toplevel().interfaz.juego.pause()
        dialog = Widget_Leccion(
            parent=self.get_toplevel(), lectura=lectura)
        dialog.run()
        dialog.stop()
        dialog.destroy()
        try:
            self.get_toplevel().juego.unpause()
        except:
            # Para Sugar
            self.get_toplevel().interfaz.juego.unpause()

    def update(self, juego, _dict):
        """
        El juego pygame actualiza información en la interfaz gtk.
        """
        infocucas = " %sH + %sM = %s" % (_dict["hembras"],
            _dict["machos"], _dict["cucas"])
        infoootecas = " = %s" % _dict["ootecas"]
        infoagua = "= %s" % int(_dict["agua"])
        infoalimento = " = %s" % int(_dict["alimento"])
        tiempo = " Años: %s Dias: %s Horas: %s" % (_dict["Años"],
            _dict["Dias"], _dict["Horas"])
        self.toolbar.set_info(infocucas, infoootecas,
            infoagua, infoalimento, tiempo)

    def run_lectura(self, juego, lectura):
        """
        El Juego pygame manda abrir una lectura.
        """
        if not lectura in self.lecciones:
            self.lecciones.append(lectura)
            try:
                self.get_toplevel().juego.pause()
            except:
                # Para Sugar
                self.get_toplevel().interfaz.juego.pause()
            dialog = Widget_Leccion(
                parent=self.get_toplevel(), lectura=lectura)
            dialog.run()
            dialog.stop()
            dialog.destroy()
            try:
                self.get_toplevel().juego.unpause()
            except:
                # Para Sugar
                self.get_toplevel().interfaz.juego.unpause()
        if lectura == "muerte":
            self.toolbarestado.set_info(
                "Se han producido muertes en el habitat.")
        elif lectura == "reproducción":
            self.toolbarestado.set_info("Hay nuevas ootecas en el habitat.")
        elif lectura == "ciclo vital":
            self.toolbarestado.set_info(
                "Se han producido nacimientos en el habitat.")
        elif lectura == "muda de exoesqueleto":
            self.toolbarestado.set_info(
                "Algunas Cucarachas han realizado la muda de su exoesqueleto.")
        elif lectura == "plaga":
            self.toolbarestado.set_info(
                "Hay Demasiadas Cucarachas en el habitat. Algunas migrarán. !!!")
        elif lectura == "extinción":
            self.toolbarestado.set_info(
                "Ya no es Posible la Reproducción en el Habitat.")
        else:
            print lectura, self.run_lectura

    def clear_cursor(self, widget):
        """
        El juego pygame indica que ya no debe haber cursor personalizado.
        """
        self.__set_cursor(False, False)
        self.toolbarestado.set_info(
            "Las Cucarachas Detectan el Alimento con sus Antenas.")

    def puntos(self, juego, puntos):
        self.derecha.set_puntos(puntos)


class Derecha(gtk.EventBox):

    __gsignals__ = {
    "lectura": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_STRING, )),
    "select": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}

    def __init__(self):

        gtk.EventBox.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
        self.set_border_width(4)

        box = gtk.VBox()

        l = ["Ciclo Vital", "Muda de Exoesqueleto", "Reproducción",
            "Plaga", "Muerte", "Lectura General"]

        for leccion in l:
            button = gtk.Button(leccion)
            box.pack_start(button, False, False, 5)
            button.connect("clicked", self.__emit_lectura)

        button = ButtonImagen("agua")
        button.connect("select", self.__select_imagen)
        box.pack_start(button, False, False, 5)

        button = ButtonImagen("alimento")
        button.connect("select", self.__select_imagen)
        box.pack_start(button, False, False, 5)

        frame = gtk.Frame(" Migraciones: ")
        frame.set_label_align(0.5, 0.5)
        self.puntos = gtk.Label("0")
        frame.add(self.puntos)
        box.pack_start(frame, False, False, 5)

        button = gtk.Button("Salir")
        box.pack_end(button, False, False, 5)
        button.connect("clicked", self.__emit_lectura)

        self.add(box)
        self.show_all()

        self.set_size_request(175, -1)

    def __select_imagen(self, widget, tipo):
        self.emit("select", tipo)

    def __emit_lectura(self, button):
        self.emit("lectura", button.get_label().lower())

    def set_puntos(self, puntos):
        puntos = int(self.puntos.get_text()) + puntos
        self.puntos.set_text(str(puntos))


class ButtonImagen(gtk.EventBox):

    __gsignals__ = {
    "select": (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, (gobject.TYPE_STRING, ))}

    def __init__(self, tipo):

        gtk.EventBox.__init__(self)

        self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ffffff"))
        self.set_border_width(4)

        self.tipo = tipo

        archivo = "jarra.png"
        if self.tipo == "agua":
            archivo = "jarra.png"
        elif self.tipo == "alimento":
            archivo = "pan.png"

        imagen = gtk.Image()
        path = os.path.join(BASE_PATH, "Imagenes", archivo)
        imagen.set_from_file(path)

        self.add(imagen)
        self.show_all()
        self.connect("button-press-event", self.__clicked_image)

    def __clicked_image(self, imagen, event):
        if event.button == 1:
            self.emit("select", self.tipo)
