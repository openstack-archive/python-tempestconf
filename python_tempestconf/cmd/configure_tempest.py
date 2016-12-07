# Copyright 2016 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import traceback

from cliff import command
from oslo_log import log as logging


LOG = logging.getLogger(__name__)


class TempestConf(command.Command):

    def get_parser(self, prog_name):
        parser = super(TempestConf, self).get_parser(prog_name)
        parser = self._add_args(parser)
        return parser

    def get_description(self):
        return 'Configure Tempest'

    def _add_args(self, parser):
        parser.add_argument('--dummy', default=None,
                            help='Dummy tempest config description')
        return parser

    def take_action(self, parsed_args):
        pass
