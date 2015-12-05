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

import os
import glob
import inspect
import threading
import subprocess
import re
import time
import shutil

from . import base
from . import arduino_info
from . import arduino_project
from . import arduino_src


class Compiler(object):
    def __init__(self, path, console=None):
        os.environ['CYGWIN'] = 'nodosfilewarning'

        self.need_to_build = True
        self.message_queue = base.message_queue.MessageQueue(console)
        self.arduino_info   = arduino_info.get_arduino_info()
        self.project        = arduino_project.Project(path)
        self.project_name   = self.project.get_name()
        self.build_path     = os.path.dirname(get_build_path(self))
        self.done_build     = False
        self.error_occured  = False
        self.settings       = base.settings.get_arduino_settings()
        self.bare_gcc       = self.settings.get('bare_gcc', False)
        self.is_big_project = self.settings.get('big_project', False)


    # Initialize the proyect with plarformio

    def initialize_io(self):
        target_board_id = self.settings.get('target_board_id', '')

        self.clean_ini()

        cmd = 'platformio -f -c sublimetext init -b %s' % target_board_id
        show_compilation_output = self.settings.get('build_verbose', False)

        self.message_queue.put('[StinoIO - Initializing project: "{0}"...]\\n', self.project_name)
        self.excecute_command(cmd,show_compilation_output)

        # Copy file to the src folder
        if(not self.error_occured):
            try:
                shutil.copy(self.project.get_path(), self.build_path + '\\src')
                self.message_queue.put('[StinoIO - Initializing finished correctly]\\n')
            except:
                self.error_occured = True

    # delete ini file in the project directory

    def clean_ini(self):
        os.chdir(self.build_path)
        for file in glob.glob("*.ini"):
            os.remove(file)

    # Prepare the files to compile with platformio
    # Call to the start_build function
    
    def build(self):
        self.message_queue.start_print()      
        self.initialize_io()
        
        if(self.error_occured):
            self.message_queue.put('[StinoIO - Error initializing the project]\\n')
            return
        
        build_thread = threading.Thread(target=self.start_build)
        build_thread.start() 

    # Compile the project of the initialization was successful

    def start_build(self):       
        
        if(not self.error_occured or not self.done_build or not self.project_src_changed):
            self.message_queue.put('[StinoIO - Start building project]\\n')

            cmd = 'platformio -f -c sublimetext run'
            show_compilation_output = self.settings.get('build_verbose', False)          
            
            self.excecute_command(cmd,show_compilation_output)

            if(not self.error_occured):
                self.done_build = True

            time.sleep(10)
            self.message_queue.stop_print()

    # Excecute every command required with platformio
    # string cmd: comand to send (http://docs.platformio.org/en/latest/userguide/index.html#commands)

    def excecute_command(self, cmd, is_verbose=False):
        start_time = time.time()

        compile_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=self.build_path, stderr=subprocess.PIPE, shell=True)
        result = compile_proc.communicate()
        return_code = compile_proc.returncode
        
        stdout = result[0].decode(base.sys_info.get_sys_encoding())
        stderr = result[1].decode(base.sys_info.get_sys_encoding())

        if(is_verbose):
            if(stdout):
                self.message_queue.put(stdout + '\n')
            if(stderr):
                self.message_queue.put(stderr + '\n')

        if return_code != 0:
            self.message_queue.put('[StinoIO - Exit with error code {0}.]\\n', return_code)
            self.error_occured = True

        if(not self.error_occured):
            end_time = time.time()
            diff_time = end_time - start_time
            diff_time = '%.1f' % diff_time
            self.message_queue.put('[StinoIO - Finished in {0}s.]\\n', diff_time)      
    
    # @Return the state of the compilation

    def is_finished(self):
        return self.done_build

    # @Return a bolean with the state of the error
    # in the different process

    def has_error(self):
        return self.error_occured

# @Return the path of the proyect to compile it
# if it's not changed, it will use the same path
# of the sketch.

def get_build_path(self):    
    project_path = self.project.get_path()
    settings = base.settings.get_arduino_settings()
    setting_build_path = settings.get('build_path', '')
    
    if(setting_build_path != '' and setting_build_path != project_path):
        return setting_build_path
    else:
        return project_path
