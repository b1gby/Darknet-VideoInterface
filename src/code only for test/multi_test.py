import sys
import os

if sys.version_info[0] < 3:
    import Tkinter as tkinter
else:
    import tkinter

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

# Needed for set_window_handle():
gi.require_version('GstVideo', '1.0')
from gi.repository import GstVideo

def set_frame_handle(bus, message, frame_id):
    if not message.get_structure() is None:
        if message.get_structure().get_name() == 'prepare-window-handle':
            display_frame = message.src
            display_frame.set_property('force-aspect-ratio', True)
            display_frame.set_window_handle(frame_id)

NUMBER_OF_FRAMES = 2 # with more frames than arguments, videos are repeated
relative_height = 1 / float(NUMBER_OF_FRAMES)

# Only argument number checked, not validity.
number_of_file_names_given = len(sys.argv) - 1
if number_of_file_names_given < 1:
    print('Give at least one video file name.')
    sys.exit()
if number_of_file_names_given < NUMBER_OF_FRAMES:
    print('Up to', NUMBER_OF_FRAMES, 'video file names can be given.')
file_names = list()
for index in range(number_of_file_names_given):
    file_names.append(sys.argv[index + 1])

window = tkinter.Tk()
window.title("Multiple videos in a column using Tk and GStreamer 1.0")
window.geometry('480x960')

Gst.init(None)
GObject.threads_init()

for number in range(NUMBER_OF_FRAMES):
    display_frame = tkinter.Frame(window, bg='')
    relative_y = number * relative_height
    display_frame.place(relx = 0, rely = relative_y,
            anchor = tkinter.NW, relwidth = 1, relheight = relative_height)
    frame_id = display_frame.winfo_id()

    player = Gst.ElementFactory.make('playbin', None)
    fullname = os.path.abspath(file_names[number % len(file_names)])
    player.set_property('uri', 'file://%s' % fullname)
    player.set_state(Gst.State.PLAYING)

    bus = player.get_bus()
    bus.enable_sync_message_emission()
    bus.connect('sync-message::element', set_frame_handle, frame_id)

window.mainloop()