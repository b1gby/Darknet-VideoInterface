#!/usr/bin/python3

import os
from threadProgressVideo import ThreadProgress, TextBufferSetter

import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GObject, Gtk, GstVideo, GdkPixbuf

class Interface(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self,title="Hat detector")
        self.connect("delete-event",Gtk.main_quit)
        self.set_default_size(1024,768)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)

        #Darknet path
        self.path=""
        #Islenecek resim dosyasinin yolu
        self.choosenimage=""

        self.grid=Gtk.Grid()
        self.add(self.grid)

        ## Menu ##

        self.menubar=Gtk.MenuBar()
        self.grid.attach(self.menubar,0,0,100,10)
        self.menubar.set_hexpand(True)

        filemenu=Gtk.MenuItem(label="File")
        self.menubar.append(filemenu)

        menu=Gtk.Menu()
        filemenu.set_submenu(menu)

        filechoosermenu=Gtk.MenuItem(label="Choose Image")
        filechoosermenu.connect("activate",self.get_file_chooser_dialog)
        menu.append(filechoosermenu)

        quitmenu=Gtk.MenuItem(label="Quit (ALt+F4)")
        quitmenu.connect("activate",self.all_quit)
        menu.append(quitmenu)

        ## *** ##

        ## Event Kismi ##

        self.vBoxevent=Gtk.VBox()
        self.grid.attach(self.vBoxevent,1,10,84,60)

        label=Gtk.Label()
        label.set_markup("<big><b>Output Video</b></big>")
        self.vBoxevent.pack_start(label,False,False,5)

        # output视频播放窗口
        self.movie_output = Gtk.DrawingArea()
        self.movie_output .set_size_request(700, 550)
        self.vBoxevent.add(self.movie_output)

        # output图片窗口
        # self.imageoutput=Gtk.Image()
        # self.vBoxevent.pack_start(self.imageoutput,True,True,25)
        # pix=GdkPixbuf.Pixbuf.new_from_file_at_scale("../images/blank.jpg",550,700,True)
        # self.imageoutput.set_from_pixbuf(pix)

        ## *** ##

        seperator=Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.grid.attach(seperator,86,10,1,84)


        ## View kismi ##

        self.vBoxview=Gtk.VBox(spacing=10)
        self.vBoxview.set_homogeneous(False)
        self.grid.attach(self.vBoxview,88,10,11,85)
        #self.fixed.put(self.vBoxview,740,15)

        label=Gtk.Label()
        label.set_markup("<b>Please select the image file to be processed!</b>")
        self.vBoxview.pack_start(label,False,False,0)

        self.filechooserbutton=Gtk.FileChooserButton(title="İşlenecek resmi seçiniz!")
        self.filechooserbutton.set_action(0)
        self.filechooserbutton.connect("file-set",self.file_changed)
        self.filechooserbutton.set_width_chars(15)
        self.vBoxview.pack_start(self.filechooserbutton,False,False,0)

        seperator=Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.vBoxview.pack_start(seperator,False,False,0)


        # input视频播放窗口
        self.movie_input = Gtk.DrawingArea()
        self.movie_input .set_size_request(400, 250)
        self.vBoxview.add(self.movie_input)

        # input图片窗口
        # self.imageinput=Gtk.Image()
        # self.vBoxview.pack_start(self.imageinput,False,False,0)
        # pix=GdkPixbuf.Pixbuf.new_from_file_at_size("../images/blank.jpg",250,400)
        # self.imageinput.set_from_pixbuf(pix)

        self.runbutton=Gtk.Button.new_with_label("Start Progress")
        fixedRunButton=Gtk.Fixed()
        self.vBoxview.pack_start(fixedRunButton,True,True,0)
        fixedRunButton.put(self.runbutton,100,450)
        #self.vBoxview.pack_start(self.runbutton,True,True,0)
        self.runbutton.connect("clicked",self.on_click_run_button)

        ## *** ##

        seperator=Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.grid.attach(seperator,0,81,86,1)

        ## Log Kismi ##

        self.logBox=Gtk.VBox()
        self.grid.attach(self.logBox,0,82,86,12)

        logToolbar=Gtk.Toolbar()
        self.logBox.pack_start(logToolbar,False,False,0)

        logClearButton=Gtk.ToolButton()
        logClearButton.set_icon_name("edit-clear-symbolic")
        logClearButton.connect("clicked",self.on_log_clear_button)
        logToolbar.insert(logClearButton,0)

        logSearchButton=Gtk.ToolButton()
        logSearchButton.set_icon_name("system-search-symbolic")
        logToolbar.insert(logSearchButton,1)

        self.logScrolledWindow=Gtk.ScrolledWindow()
        self.logScrolledWindow.set_hexpand(True)
        self.logScrolledWindow.set_vexpand(True)
        self.logBox.pack_start(self.logScrolledWindow,True,True,0)

        self.textView=Gtk.TextView()
        self.textView.set_editable(False)
        self.textView.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textView.set_cursor_visible(False)
        self.logScrolledWindow.add(self.textView)

        self.textBuffer=self.textView.get_buffer()

        ## *** ##

        seperator=Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.grid.attach(seperator,0,94,100,1)

        ## Status Bar ##

        self.statusBar=Gtk.HBox()
        self.grid.attach(self.statusBar,0,95,100,5)

        self.spinner=Gtk.Spinner()
        self.statusBar.pack_start(self.spinner,True,True,0)

        ## ** ##
        # 视频player、demuxer、queue、bus
        self.player = Gst.Pipeline.new("player")
        source = Gst.ElementFactory.make("filesrc", "file-source")

        demuxer = Gst.ElementFactory.make("qtdemux", "demuxer")
        demuxer.connect("pad-added", self.demuxer_callback)
        self.video_decoder = Gst.ElementFactory.make("avdec_h264", "video-decoder")
        # decodebina = Gst.ElementFactory.make("decodebin","decodea")
        

        # self.audio_decoder = Gst.ElementFactory.make("faad", "audio-decoder")
        # audioconv = Gst.ElementFactory.make("audioconvert", "converter")
        # audiosink = Gst.ElementFactory.make("autoaudiosink", "audio-output")
        videosink = Gst.ElementFactory.make("xvimagesink", "video-output")
        # self.queuea = Gst.ElementFactory.make("queue", "queuea")
        self.queuev = Gst.ElementFactory.make("queue", "queuev")
        colorspace = Gst.ElementFactory.make("videoconvert", "colorspace")
        #colorspace = Gst.ElementFactory.make("ffmpegcolorspace", "colorspace")

        # decodebina.connect("pad-added", self.cb_decodebin_newpad, self.queuev, self.queuea)

        self.player.add(source)
        self.player.add(demuxer)
        self.player.add(self.video_decoder)
        # self.player.add(self.audio_decoder)
        # self.player.add(audioconv)
        # self.player.add(audiosink)
        # self.player.add(decodebina)
        self.player.add(videosink)
        # self.player.add(self.queuea)
        self.player.add(self.queuev)
        self.player.add(colorspace)

        source.link(demuxer)
        self.queuev.link(self.video_decoder)
        self.video_decoder.link(colorspace)
        colorspace.link(videosink)
        # self.queuea.link(audioconv)
        # self.audio_decoder.link(audioconv)
        # audioconv.link(audiosink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

        self.message_count = 1

    def get_file_chooser_dialog(self,widget):
        filechooserdialog=Gtk.FileChooserDialog(title="İşlenecek resmi seçiniz!")
        filechooserdialog.set_action(0)
        filechooserdialog.add_button("_Open",Gtk.ResponseType.OK)
        filechooserdialog.add_button("_Cancel",Gtk.ResponseType.CANCEL)
        filechooserdialog.set_default_response(Gtk.ResponseType.OK)
        response=filechooserdialog.run()
        # print("response")
        if response == Gtk.ResponseType.OK :
            self.filechooserbutton.set_filename(filechooserdialog.get_filename())
            # pixinput=GdkPixbuf.Pixbuf.new_from_stream_at_scale(self.filechooserbutton.get_filename(),275,425,True)
            # self.imageinput.set_from_pixbuf(pixinput)
            self.player.get_by_name("file-source").set_property("location", self.filechooserbutton.get_filename())
            self.player.set_state(Gst.State.PLAYING)
            self.choosenimage=filechooserdialog.get_filename()
        filechooserdialog.destroy()

    def on_message(self, bus, message):
        # print(message.get_structure().get_name())
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.filechooserbutton.set_label("Start")
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print ("Error: %s" % err, debug)
            self.player.set_state(Gst.State.NULL)
            self.filechooserbutton.set_label("Start")


    def on_sync_message(self, bus, message):
        # print(message.get_structure().get_name())
        if message.get_structure().get_name() == 'prepare-window-handle':
            print(self.message_count)
            if self.message_count%2==1:
                # print(message.src)
                imagesink_in = message.src
                imagesink_in.set_property("force-aspect-ratio", True)
                xid_in = self.movie_input.get_property('window').get_xid()
                imagesink_in.set_window_handle(xid_in)
            else:
                # print(message.src)
                imagesink_out = message.src
                imagesink_out.set_property("force-aspect-ratio", True)
                xid_out = self.movie_output.get_property('window').get_xid()
                imagesink_out.set_window_handle(xid_out)
            self.message_count+=1


            # imagesink_out = message.src
            # imagesink_out.set_property("force-aspect-ratio", True)
            # xid_out = self.movie_output.get_property('window').get_xid()
            # imagesink_out.set_window_handle(xid_out)


    def demuxer_callback(self, demuxer, pad):
        if pad.get_property("template").name_template == "video_%u":
            qv_pad = self.queuev.get_static_pad("sink")
            pad.link(qv_pad)
        # elif pad.get_property("template").name_template == "audio_%u":
        #     qa_pad = self.queuea.get_static_pad("sink")
        #     pad.link(qa_pad)

    # #decodebin产生新pad的回调函数
    # def cb_decodebin_newpad(self, src, pad, dst ,dst2):
    #     # print("src")
    #     caps = Gst.Pad.get_current_caps(pad)
    #     structure_name = caps.to_string()
    #     if structure_name.startswith("video"):
    #         videorate_pad = dst.get_static_pad("sink")
    #         pad.link(videorate_pad)

    #     # elif structure_name.startswith("audio"):
    #     #     volume_pad = dst2.get_static_pad("sink")
    #     #     pad.link(volume_pad)


    def on_click_run_button(self,widget):

        if self.choosenimage=="":
            errormessage=Gtk.MessageDialog(self,0,Gtk.MessageType.ERROR,Gtk.ButtonsType.OK,
                                           "Hata!")
            errormessage.format_secondary_text(
                "Lütfen işlenecek resmi seçiniz!"
            )
            errormessage.run()
            errormessage.destroy()
            return

        # if self.path=="":
        #     filechooser=Gtk.FileChooserDialog(title="Darknet'in bulunduğu yolu seçiniz")
        #     filechooser.set_action(2)
        #     filechooser.add_button("_Open",Gtk.ResponseType.OK)
        #     filechooser.add_button("_Cancel",Gtk.ResponseType.CANCEL)
        #     filechooser.set_default_response(Gtk.ResponseType.OK)
        #     response=filechooser.run()
        #
        #     if response == Gtk.ResponseType.OK :
        #         self.path=filechooser.get_filename()
        #
        #     filechooser.destroy()

        os.chdir("../darknet-yolov4/")

        self.path = os.getcwd()

        if self.path=="" :
            return

        command="./darknet detector demo cfg/voc.data cfg/yolov3.cfg yolov3.weights "+self.choosenimage + " -out_filename output.mp4"

        progress=ThreadProgress(self.movie_output,self.player,self.spinner,command,self.path,self.textBuffer)
        progress.start()
        # textBufferProgress=TextBufferSetter(self.textBuffer)
        # textBufferProgress.start()
        # self.outputpath = progress.outputpath
        # self.player.get_by_name("file-source").set_property("location", self.outputpath)
        # self.player.set_state(Gst.State.PLAYING)

        self.spinner.start()
        self.vBoxview.show_all()
        self.vBoxevent.show_all()

    def all_quit(self,widget):
        Gtk.main_quit()

    def file_changed(self,widget):
        # print(self.filechooserbutton.get_filename())
        self.player.get_by_name("file-source").set_property("location", self.filechooserbutton.get_filename())
        self.player.set_state(Gst.State.PLAYING)
        self.choosenimage=self.filechooserbutton.get_filename()

        # pix=GdkPixbuf.Pixbuf.new_from_stream_at_scale(self.filechooserbutton.get_filename(),275,425,True)
        # self.imageinput.set_from_pixbuf(pix)
        # self.choosenimage=self.filechooserbutton.get_filename()

    def on_log_clear_button(self,widget):
        self.textBuffer.set_text("")


Gst.init(None)
window=Interface()
window.show_all()
GObject.threads_init()
Gtk.main()
