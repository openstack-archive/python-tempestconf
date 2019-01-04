# Copyright 2018 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# This script is able to compare two ini files specified by arguments, f.e.:
#   $ ./compare-ini.py ./file1.ini ./file2.ini

# If some of the values are actually lists divided by commas, f.e.:
#
# [section]
# key = value1,value2,value3
#
# then this script compares these values regardless their order.

import six
from six.moves import configparser
import sys


def compare_ini_files(conf1, path1, conf2, path2):
    failed = 0
    for section in conf1.sections():
        if not conf2.has_section(section):
            sys.stderr.write("%s doesn't have %s section.\n" %
                             (path2, section))
            failed = 1
            continue
        for (key, value) in conf1.items(section):
            values1 = value.split(',')
            if len(values1) > 1:
                # the value contains a list of strings divided by commas,
                # e.g. api_extensions
                values2 = conf2.get(section, key).split(',')
                for i in values1:
                    if i not in values2:
                        sys.stderr.write("%s value not in %s.%s of %s\n" %
                                         (i, section, key, path2))
                        failed = 1
            else:
                val1 = conf1.get(section, key)
                if not conf2.has_option(section, key):
                    sys.stderr.write("%s doesn't have %s option in %s "
                                     "section.\n" % (path2, key, section))
                    failed = 1
                else:
                    val2 = conf2.get(section, key)
                    if not val1 == val2:
                        sys.stderr.write("%s in %s != %s in %s under %s.%s\n" %
                                         (val1, path1, val2,
                                          path2, section, key))
                        failed = 1
    return failed


if __name__ == '__main__':
    if six.PY3:
        conf1 = configparser.ConfigParser()
        conf2 = configparser.ConfigParser()
    else:
        conf1 = configparser.SafeConfigParser()
        conf2 = configparser.SafeConfigParser()

    conf1.read(sys.argv[1])
    conf2.read(sys.argv[2])

    # compare first file to the other one
    ret = compare_ini_files(conf1, sys.argv[1], conf2, sys.argv[2])

    # compare the other file to the first one
    ret2 = compare_ini_files(conf2, sys.argv[2], conf1, sys.argv[1])

    sys.exit(ret or ret2)
