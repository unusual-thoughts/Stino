#!/usr/bin/env python
#-*- coding: utf-8 -*-

# 1. Copyright
# 2. Lisence
# 3. Author

"""
Documents
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sublime
import sublime_plugin
import threading
import subprocess
import time
import os.path

from . import base
from . import arduino_project
from . import arduino_compiler
from . import arduino_target_params


class Uploader(object):
    def __init__(self, sketch_path, console=None):
        self.message_queue = base.message_queue.MessageQueue(console)
        self.compiler = arduino_compiler.Compiler(sketch_path, console)
        self.project = arduino_project.Project(sketch_path)
        self.sketch_folder = os.path.dirname(sketch_path)
        self.error_occured = False
        self.params = {}
        self.do_touch = False
        self.wait_for_upload_port = False
    
    # compile and upload the sketch with platformio

    def upload(self, using_programmer=False):
        self.compiler.build()
        self.message_queue.start_print()
        upload_thread = threading.Thread(target=lambda: self.start_upload(using_programmer))
        upload_thread.start()
        
    # Upload the compiled sket into the selected board

    def start_upload(self, using_programmer):

        while not self.compiler.is_finished():
            time.sleep(1)
        if not self.compiler.has_error():
            self.error_occured = False
            settings = base.settings.get_arduino_settings()
            show_upload_output = settings.get('upload_verbose', False)
            self.prepare_upload_port()

            self.message_queue.put('[StinoIO - Start uploading...]\\n')
            cmd = 'platformio -f -c sublimetext run -t upload --upload-port %s' % (self.upload_port)

            self.compiler.excecute_command(cmd, show_upload_output)

        time.sleep(20)
        self.message_queue.stop_print()
    
    # @Return the serial port selected in the main menu

    def prepare_upload_port(self):
        settings = base.settings.get_arduino_settings()
        self.upload_port = settings.get('serial_port', 'no_serial')


def by_using_programmer(using_programmer, params):
    state = False
    upload_protocol = params.get('upload.protocol', '')
    upload_uploader = params.get('upload.uploader', '')
    if (using_programmer or upload_protocol is None) and \
            upload_uploader != 'dfu-util':
        state = True
    return state
