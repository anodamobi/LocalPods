#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Injects local copies of CocoaPods in Podfile
# Version 1.2
# Homepage: https://github.com/anodamobi/Local-CocoaPods-auto-attacher
# Author: Alex Zavrazhniy <alex@anoda.mobi>
# Copyright 2014, ANODA Mobile Development Agency
# License: MIT

import argparse
import os
import logging
import re
import ConfigParser
import shutil


parser = argparse.ArgumentParser(description='Injects local copies of CocoaPods in Podfile')
parser.add_argument('--version', action='version', version='%(prog)s 1.2')
parser.add_argument('-v', dest='verbose', action='store_true', help='verbose output')
parser.add_argument('--pods', dest='pods', type=str, help='local Pods folder path (default is parent dir)')
parser.add_argument('--podfile', dest='podfile', type=str, help='Podfile path (default is ./Podfile)')
parser.add_argument('-d', '--dry-run', dest='dry', action='store_true', help='perform a trial run with no changes made')
parser.add_argument('-b', '--backup', dest='backup', action='store_true', help='backup Podfile before update')
parser.add_argument('-o', '--preserve-original', dest='preserve', action='store_true', help='preserve original lines with comments')
parser.add_argument('-g', '--group', dest='group', action='store_true', help='group local pods')
parser.add_argument('-r', '--runupdate', dest='runupdate', action='store_true', help='run `pod update` after saving')
parser.add_argument('-c', '--config', dest='config', default='~/.localpods', type=str, help='config file (default is ~/.localpods)')
parser.add_argument('--generate-config', dest='generateConfig', action='store_true', help='generate config file interactively and exit')

args = parser.parse_args()

args.config = os.path.expanduser(args.config)

optionsBoolean = ['preserve', 'group', 'runupdate', 'backup', 'dry']


# config generator
if args.generateConfig:
    config = ConfigParser.ConfigParser()
    config.add_section('localpods')
    print 'This will interactively generate your personal config file for localpods (~/.localpods)'
    print 'You can always override config parameters with command line options\n'

    pods = raw_input('Enter default local Pods folder path [..]:')
    if len(pods) is 0:
        pods = '..'
    config.set('localpods', 'pods', pods)
    config.set('localpods', 'group', raw_input('Group local pods [y/N]:') in ['Y', 'y'])
    config.set('localpods', 'preserve', raw_input('Preserve original lines with comments [y/N]:') in ['Y', 'y'])
    config.set('localpods', 'runupdate', raw_input('Run `pod update` after saving [y/N]:') in ['Y', 'y'])
    config.set('localpods', 'backup', raw_input('Backup Podfile before update [y/N]:') in ['Y', 'y'])

    with open(args.config, 'wb') as file:
        config.write(file)
    exit()
# / config generator


# Enable verbose if needed
if args.verbose:
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
else:
    logging.basicConfig(format='%(levelname)s: %(message)s')


# default options
options = {
    'pods': '..',
    'podfile': 'Podfile',
    'preserve': False,
    'group': False,
    'runupdate': False,
    'dry': False,
    'backup': False
}


# read config file
config = ConfigParser.ConfigParser()
config.read(args.config)

if config.has_option('localpods', 'pods'):
    options['pods'] = config.get('localpods', 'pods')

for option in optionsBoolean:
    if config.has_option('localpods', option):
        options[option] = config.getboolean('localpods', option)
# / read config file

argsDict = vars(args)

# override CLI options
for option in optionsBoolean + ['pods', 'podfile']:
    print option
    if argsDict[option]:
        options[option] = argsDict[option]
# / override CLI options


if options['dry']:
    print 'Performing a trial run with no changes made\n'


# expand ~ in pods path and make it absolute
if options['pods'][0] == '~':
    options['pods'] = os.path.expanduser(options['pods'])

options['pods'] = os.path.abspath(options['pods']) + '/'

# expand ~ in podfile path and make it absolute
if options['podfile'][0] == '~':
    options['podfile'] = os.path.expanduser(options['podfile'])

options['podfile'] = os.path.abspath(options['podfile'])


logging.debug('Using Local Pods folder: %s', options['pods'])
logging.debug('Using Podfile: %s\n', options['podfile'])


if not os.path.isfile(options['podfile']):
    logging.error('Podfile not found at %s', options['podfile'])
    exit(1)

try:
    podfileOld = open(options['podfile'])
except:
    logging.error('Unable to open Podfile at %s', options['podfile'])
    exit(1)


podfileNew = ''
podfileNewGroupOld = ''
podfileNewGroupNew = ''

for lineOld in podfileOld.readlines():
    lineOld = lineOld.strip()
    saveOldLine = True
    if lineOld[0:3] == 'pod':
        logging.debug('Found %s', lineOld)

        # extracting pod name
        try:
            podName = re.compile('pod\s([\'"]([A-z0-9+-_]*)[\'"])').match(lineOld).group(2)
            logging.debug('Pod name: %s\n', podName)
        except:
            logging.warning('Unable to parse Pod name, does it fit the [A-z0-9+-_] pattern?\n')

        if podName:
            # check for already patched
            isAlreadyLocal = re.compile(':path => [\'"](.*)[\'"]').search(lineOld)
            if isAlreadyLocal:
                # pod is already patched
                localPath = isAlreadyLocal.group(1)
                logging.warning('Pod %s already pointed at local path: %s\n', podName, localPath)
                if not os.path.isdir(localPath):
                    logging.warning('Local path %s for Pod %s does not exists!', localPath, podName)
            else:
                # pod isn't patched yet
                # checking local pod availability
                localPodPath = options['pods'] + podName
                if os.path.isdir(localPodPath):
                    print 'Found local Pod %s at: %s\n' % (podName, localPodPath)
                    lineNew = "pod '%s', :path => '%s'" % (podName, localPodPath)
                    if options['group']:
                        saveOldLine = False
                        podfileNewGroupOld += '#%s\n' % lineOld
                        podfileNewGroupNew += '%s\n' % lineNew
                    else:
                        if options['preserve']:
                            lineNew = "#%s\n%s" % (lineOld, lineNew)
                        lineOld = lineNew

    # remove 'end' keyword from podfile if --group option is enabled and groups isn't empty
    if lineOld[0:3] == 'end' and options['group'] and len(podfileNewGroupNew) > 0 :
        saveOldLine = False

    if saveOldLine:
        podfileNew += '%s\n' % lineOld

podfileOld.close()

# Append bottom part of new podfile
if len(podfileNewGroupOld) > 0:
    podfileNew += '\n# ADDED BY LOCALPODS:\n'
    podfileNew += '\n# ORIGINAL PODS:\n'
    podfileNew += podfileNewGroupOld
    podfileNew += '\n# LOCAL PODS:\n'
    podfileNew += podfileNewGroupNew + '\n'
    podfileNew += 'end'


if options['dry']:
    print 'The new Podfile:'
    print podfileNew
else:
    if options['backup']:
        shutil.copy2(options['podfile'], options['podfile'] + '.bak')

    podfileOld = open(options['podfile'], 'wb')
    podfileOld.write(podfileNew)
    print 'Saved new Podfile to: %s' % options['podfile']
    if options['runupdate']:
        print 'Running `pod update`'
        os.system('pod update')

# EOF
