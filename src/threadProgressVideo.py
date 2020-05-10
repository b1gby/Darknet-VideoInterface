#!/usr/bin/python3

import threading
import os
import gi
import shlex
import time
from subprocess import Popen, PIPE

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GObject, Gtk, GstVideo, GdkPixbuf


class ThreadProgress(threading.Thread):

    def __init__(self, movie_output, player, spinner, command, path, textBuffer):
        threading.Thread.__init__(self)
        self.movie_output = movie_output
        self.player = player
        self.spinner = spinner
        self.command = command
        self.path = path
        self.outputpath = self.path + "/output.mp4"
        self.textBuffer = textBuffer

    def run(self):
        args = shlex.split(self.command)

        tmpWrite = open("tmpout", "wb")

        process = Popen(args, cwd=self.path, stdout=tmpWrite, stderr=tmpWrite, bufsize=1)

        process.wait()

        tmpWrite.close()

        f = open("tmpout", "r")
        self.textBuffer.set_text(f.read())
        f.close()

        self.spinner.stop()

        # 发送player准备播放的消息
        self.player.get_by_name("file-source").set_property("location", self.outputpath)
        self.player.set_state(Gst.State.PLAYING)


class TextBufferSetter(threading.Thread):

    def __init__(self, textBuffer):
        threading.Thread.__init__(self)
        self.textBuffer = textBuffer

    def run(self):
        tmpRead = open("tmpout", "r")
        print("start")
        while (True):
            print("in loop")
            self.textBuffer.set_text(tmpRead.read())
            time.sleep(2)

        tmpRead.close()
