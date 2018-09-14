# Copyright (c) 2015 Michel Oosterhof <michel@oosterhof.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The names of the author(s) may not be used to endorse or promote
#    products derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHORS ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

from __future__ import absolute_import, division

import json
import os
import sys

import cowrie.core.output
import cowrie.python.logfile
from cowrie.core.config import CONFIG
from twisted.python import log


class Output(cowrie.core.output.Output):

    time_fields_to_remove = {'time', 'time_msec', 'timestamp'}
    config_mapping = {'unix_nsec_time': 'time', 'unix_msec_time': 'time_msec', 'iso_time': 'timestamp'}

    def __init__(self):
        cowrie.core.output.Output.__init__(self)
        fn = CONFIG.get('output_jsonlog', 'logfile')
        time_output = False
        for config_option in self.config_mapping.keys():
            if CONFIG.has_option('output_jsonlog', config_option) and CONFIG.getboolean('output_jsonlog', config_option):
                time_output = True
                self.time_fields_to_remove.remove(self.config_mapping[config_option])
        if not time_output:
            print("ERROR: You must enable at least one time output format in the cowrie.cfg under the 'output_jsonlog' section. Possible options are: {}", str(self.config_mapping.keys())[1:-1])
            sys.exit(1)
        dirs = os.path.dirname(fn)
        base = os.path.basename(fn)
        self.outfile = cowrie.python.logfile.CowrieDailyLogFile(base, dirs, defaultMode=0o664)

    def start(self):
        pass

    def stop(self):
        self.outfile.flush()

    def write(self, logentry):
        if 'time' not in self.time_fields_to_remove:
            logentry['time'] = logentry['time']
        if 'time_msec' not in self.time_fields_to_remove:
            logentry['time_msec'] = int(logentry['time'] * 1000000 / 1000)
        for i in list(logentry.keys()):
            # Remove twisted 15 legacy keys
            if i.startswith('log_') or i in self.time_fields_to_remove or i == 'system':
                del logentry[i]
        json.dump(logentry, self.outfile)
        self.outfile.write('\n')
        self.outfile.flush()