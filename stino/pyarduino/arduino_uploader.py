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
    
    def upload(self, using_programmer=False):

        self.compiler.build()
        self.message_queue.start_print()
        upload_thread = threading.Thread(target=lambda: self.start_upload(using_programmer))
        upload_thread.start()

    """
    def upload(self, using_programmer=False):

        #prefix_env = "[env:uno]\n" # name of the enviroment
        #PathIO = self.sketch_folder + "/platformio.ini"
        
        #FileIO = open(PathIO,'wb')
        #FileIO.write(bytes(prefix_env, 'UTF-8'))
        #FileIO.close()

        print("estoy aqui")
        project_name = self.project.get_name()
        self.message_queue.put('[Stino - Start building "{0}"...]\\n', project_name)

        os.environ['CYGWIN'] = 'nodosfilewarning'
        error_occured = False

        cmd = "platformio init -d C:/Users/guill/Desktop/blink_example"

        #cmd = "platformio run -d C:/Users/guill/Desktop/blink_example --target upload"
        compile_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        result = compile_proc.communicate()
        return_code = compile_proc.returncode
        
        stdout = result[0].decode(base.sys_info.get_sys_encoding())
        stderr = result[1].decode(base.sys_info.get_sys_encoding())

        if(stdout):
            self.message_queue.put(stdout + '\n')
        if(stderr):
            self.message_queue.put(stderr + '\n')

        if return_code != 0:
            self.message_queue.put('[Stino - Exit with error code {0}.]\\n', return_code)
            self.error_occured = True

       
        #self.compiler.build()
        #self.message_queue.start_print()
        #upload_thread = threading.Thread(
        #    target=lambda: self.start_upload(using_programmer))
        #upload_thread.start()
        """
        

    def start_upload(self, using_programmer):

        while not self.compiler.is_finished():
            time.sleep(1)
        if not self.compiler.has_error():
            self.message_queue.put('[StinoIO - Start uploading...]\\n')

            #self.params = self.compiler.get_params()
            self.prepare_upload_port(using_programmer)
            #self.prepare_cmds(using_programmer)
            #self.exec_cmds()
            self.error_occured = False
            cmd = 'platformio -f -c sublimetext run -t upload --upload-port %s' % (self.upload_port)

            compile_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=self.sketch_folder, stderr=subprocess.PIPE, shell=True)
            result = compile_proc.communicate()
            return_code = compile_proc.returncode
            
            stdout = result[0].decode(base.sys_info.get_sys_encoding())
            stderr = result[1].decode(base.sys_info.get_sys_encoding())

            """
            if(stdout):
                self.message_queue.put('stdout\n')
                self.message_queue.put(stdout + '\n')
            if(stderr):
                self.message_queue.put('stderr\n')
                self.message_queue.put(stderr + '\n')
            """

            if return_code != 0:
                self.message_queue.put('[StinoIO - Exit with error code {0}.]\\n', return_code)
                self.error_occured = True

            if not self.error_occured:
                self.retouch_serial_port()
                self.message_queue.put('[StinoIO - Done uploading.]\\n')
        time.sleep(20)
        self.message_queue.stop_print()
    

    def prepare_upload_port(self, using_programmer):
        settings = base.settings.get_arduino_settings()
        self.upload_port = settings.get('serial_port', 'no_serial')
        return
        """
        self.params['serial.port'] = self.upload_port
        if self.upload_port.startswith('/dev/'):
            self.upload_port_file = self.upload_port[5:]
        else:
            self.upload_port_file = self.upload_port
        self.params['serial.port.file'] = self.upload_port_file

        if self.upload_port in base.serial_monitor.serials_in_use:
            serial_monitor = base.serial_monitor.serial_monitor_dict.get(self.upload_port, None)
            if serial_monitor:
                serial_monitor.stop()

        if not by_using_programmer(using_programmer, self.params):
            bootloader_file = self.params.get('bootloader.file', '')
            if 'caterina' in bootloader_file.lower():
                self.do_touch = True
                self.wait_for_upload_port = True
            elif self.params.get('upload.use_1200bps_touch') == 'true':
                self.do_touch = True

            if self.params.get('upload.wait_for_upload_port') == 'true':
                self.wait_for_upload_port = True

            if self.do_touch:
                before_ports = base.serial_port.list_serial_ports()
                if self.upload_port in before_ports:
                    text = 'Forcing reset using 1200bps open/close '
                    text += 'on port {0}.\\n'
                    self.message_queue.put(text, self.upload_port)
                    base.serial_port.touch_port(self.upload_port, 1200)
                if self.wait_for_upload_port:
                    if base.sys_info.get_os_name() != 'osx':
                        time.sleep(0.4)
                    self.upload_port = base.serial_port.wait_for_port(
                        self.upload_port, before_ports, self.message_queue)
                else:
                    time.sleep(4)
                self.params['serial.port'] = self.upload_port

                if self.upload_port.startswith('/dev/'):
                    self.upload_port_file = self.upload_port[5:]
                else:
                    self.upload_port_file = self.upload_port
                self.params['serial.port.file'] = self.upload_port_file

            if self.params.get('upload.auto_reset', '') == 'true':
                text = 'Resetting to bootloader via DTR pulse\\n'
                self.message_queue.put(text)
                base.serial_port.auto_reset(self.upload_port)
        self.params = arduino_target_params.replace_param_values(self.params)
        """

    def prepare_cmds(self, using_programmer):
        self.cmds = []
        if not by_using_programmer(using_programmer, self.params):
            if 'post_compile.pattern' in self.params:
                self.cmds.append(self.params.get('post_compile.pattern', ''))
            self.cmds.append(self.params.get('upload.pattern'))
        else:
            self.cmds.append(self.params.get('program.pattern', ''))

        settings = base.settings.get_arduino_settings()
        verify_code = settings.get('verify_code', False)
        if verify_code:
            self.cmds[-1] = self.cmds[-1] + ' -V'

    def exec_cmds(self):
        settings = base.settings.get_arduino_settings()
        show_upload_output = settings.get('upload_verbose', False)
        working_dir = self.compiler.get_ide_path()
        self.error_occured = arduino_compiler.exec_cmds(
            working_dir, self.cmds, self.message_queue, show_upload_output)

    def retouch_serial_port(self):
        if self.do_touch:
            if self.wait_for_upload_port:
                time.sleep(0.1)
                timeout = time.time() + 2
                while timeout > time.time():
                    ports = base.serial_port.list_serial_ports()
                    if self.upload_port in ports:
                        base.serial_port.touch_port(self.upload_port, 9600)
                        break
                    time.sleep(0.25)
            else:
                base.serial_port.touch_port(self.upload_port, 9600)


def by_using_programmer(using_programmer, params):
    state = False
    upload_protocol = params.get('upload.protocol', '')
    upload_uploader = params.get('upload.uploader', '')
    if (using_programmer or upload_protocol is None) and \
            upload_uploader != 'dfu-util':
        state = True
    return state
