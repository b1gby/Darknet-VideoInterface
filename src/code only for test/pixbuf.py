#!/usr/bin/env python3
# Created by xiaosanyu at 16/7/19
# section 132
# 
# author: xiaosanyu
# website: yuxiaosan.tk \
#          http://blog.csdn.net/a87b01c14
# created: 16/7/19

TITLE = "Pixbuf"
DESCRIPTION = """
A GdkPixbuf represents an image, normally in RGB or RGBA format.
Pixbufs are normally used to load files from disk and perform
image scaling.

This demo is not all that educational, but looks cool. It was written
by Extreme Pixbuf Hacker Federico Mena Quintero. It also shows
off how to use GtkDrawingArea to do a simple animation.

Look at the Image demo for additional pixbuf usage examples.
"""

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import os
from math import *

background_name = "background.jpg"
image_names = ("apple-red.png",
               "gnome-applets.png",
               "gnome-calendar.png",
               "gnome-foot.png",
               "gnome-gmush.png",
               "gnome-gimp.png",
               "gnome-gsame.png",
               "gnu-keys.png")
images = []
prefix = os.path.realpath(os.path.join(os.path.dirname(__file__), "Data"))
start_time = 0
CYCLE_TIME = 3000000


class PixbufsWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Pixbuf demo")
        self.set_resizable(False)
        self.background = None
        self.back_width = 10
        self.back_height = 10
        rlt = self.load_pixbufs()
        if not rlt[0]:
            dialog = Gtk.MessageDialog(self,
                                       Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                       Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.CLOSE,
                                       "Failed to load an image: %s" % rlt[1])

            dialog.run()
            dialog.destroy()

        else:
            self.set_size_request(self.back_width, self.back_height)

            self.pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, False, 8, self.back_width, self.back_height);

            da = Gtk.DrawingArea.new()

            da.connect("draw", self.draw_cb)

            self.add(da)

            da.add_tick_callback(self.on_tick, da)

    def load_pixbufs(self):
        if self.background:
            return True, ""  # already loaded earlier
        try:
            self.background = GdkPixbuf.Pixbuf.new_from_file(os.path.join(prefix, background_name))
            self.back_width = self.background.get_width()
            self.back_height = self.background.get_height()

            for image in image_names:
                images.append(GdkPixbuf.Pixbuf.new_from_file(os.path.join(prefix, image)))
        except GLib.Error as e:
            return False, e.message

        return True, ""

    def draw_cb(self, drawingarea, cr):
        Gdk.cairo_set_source_pixbuf(cr, self.pixbuf, 0, 0)
        cr.paint()

        return True

    def on_tick(self, da, frame_clock, *data):
        global start_time
        self.background.copy_area(0, 0, self.back_width, self.back_height,
                                  self.pixbuf, 0, 0)

        if start_time == 0:
            start_time = frame_clock.get_frame_time()

        current_time = frame_clock.get_frame_time()
        f = ((current_time - start_time) % CYCLE_TIME) / CYCLE_TIME

        xmid = self.back_width / 2.0
        ymid = self.back_height / 2.0

        radius = min(xmid, ymid) / 2.0

        for i, image in enumerate(images):
            r1 = Gdk.Rectangle()
            r2 = Gdk.Rectangle()
            dest = Gdk.Rectangle()

            ang = 2.0 * GLib.PI * i / len(images) - f * 2.0 * GLib.PI

            iw = image.get_width()
            ih = image.get_height()

            r = radius + (radius / 3.0) * sin(f * 2.0 * GLib.PI)

            xpos = floor(xmid + r * cos(ang) - iw / 2.0 + 0.5)
            ypos = floor(ymid + r * sin(ang) - ih / 2.0 + 0.5)

            k = sin(f * 2.0 * GLib.PI) if i & 1 else cos(f * 2.0 * GLib.PI)
            k = 2.0 * pow(k, 2)
            k = max(0.25, k)

            r1.x = xpos
            r1.y = ypos
            r1.width = iw * k
            r1.height = ih * k

            r2.x = 0
            r2.y = 0
            r2.width = self.back_width
            r2.height = self.back_height
            rlt = Gdk.rectangle_intersect(r1, r2)
            if rlt[0]:
                dest = rlt[1]
                image.composite(self.pixbuf,
                                dest.x, dest.y,
                                dest.width, dest.height,
                                xpos, ypos,
                                k, k,
                                GdkPixbuf.InterpType.NEAREST,
                                max(127, fabs(255 * sin(f * 2.0 * GLib.PI))) if (i & 1) else \
                                    max(127, fabs(255 * cos(f * 2.0 * GLib.PI))))

        da.queue_draw()

        return GLib.SOURCE_CONTINUE


def main():
    win = PixbufsWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
