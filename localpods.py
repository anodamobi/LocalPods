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

parser = argparse.ArgumentParser(description='Injects local copies of CocoaPods in Podfile')
parser.add_argument('--version', action='version', version='%(prog)s version 1.2')
parser.add_argument('-v', dest='verbose', action='store_true', help='verbose output')
parser.add_argument('--pods', dest='pods', default='..', type=str, help='local Pods folder path (default is parent dir)')
parser.add_argument('--podfile', dest='podfile', default='Podfile', type=str, help='Podfile path (default is ./Podfile)')
parser.add_argument('-d --dry-run', dest='dry', action='store_true', help='perform a trial run with no changes made')
parser.add_argument('-o --preserve-original', dest='preserve', action='store_true', help='preserve original lines with comments')
parser.add_argument('-g --group', dest='group', action='store_true', help='group local pods')
parser.add_argument('-r --runupdate', dest='runupdate', action='store_true', help='run `pod update` after saving')
parser.add_argument('-c --config', dest='config', default='~/.localpods', type=str, help='config file (default is ~/.localpods)')
parser.add_argument('--generate-config', dest='generateConfig', action='store_true', help='generate config file interactively and exit')

args = parser.parse_args()

# config generator
if args.generateConfig:
    config = ConfigParser.ConfigParser()
    config.add_section('localpods')
    print 'This will interactively generate your personal config file for localpods'

    pods = raw_input('Enter default local Pods folder path [..]:')
    if len(pods) is 0:
        pods = '..'
    config.set('localpods', 'pods', pods)
    config.set('localpods', 'preverse', raw_input('Group local pods [y/N]:') in ['Y', 'y,' ''])
    config.set('localpods', 'group', raw_input('Preserve original lines with comments [y/N]:') in ['Y', 'y,' ''])
    config.set('localpods', 'runupdate', raw_input('Run `pod update` after saving [y/N]:') in ['Y', 'y,' ''])

    with open(os.path.expanduser(args.config), 'wb') as file:
        config.write(file)
    exit()
# / config generator

logging.basicConfig(format='%(levelname)s: %(message)s')

# Enable verbose if needed
if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

# read config file
config = ConfigParser.ConfigParser()

config.read(os.path.expanduser(args.config))

if config.has_option('localpods', 'foo'):
    foo = config.get('localpods', 'foo')

if config.has_option('localpods', 'pods'):
    args.path = config.get('localpods', 'pods')
# / read config file

# expand all relative paths
args.path = os.path.abspath(args.path) + '/'
args.podfile = os.path.abspath(args.podfile)

# expand ~ in pods path
if '~' in args.path:
    args.path = os.path.expanduser(args.path)

# expand ~ in podfile path
if '~' in args.podfile:
    args.podfile= os.path.expanduser(args.podfile)

if args.dry:
    print 'Performing a trial run with no changes made\n'

logging.debug('Using Local Pods folder: %s', args.path)
logging.debug('Using Podfile: %s\n', args.podfile)

if not os.path.isfile(args.podfile):
    logging.error('Podfile not found at %s', args.podfile)
    exit(1)

try:
    podfile = open(args.podfile)
except:
    logging.error('Unable to open Podfile at %s', args.podfile)
    exit(1)

podfileNew = ''

for line in podfile.readlines():
    line = line.strip()
    if line[0:3] == 'pod':
        logging.debug('Found %s', line)
        try:
            pod = re.compile('pod\s([\'"]([A-z0-9+-_]*)[\'"])').match(line).group(2)
            logging.debug('Pod name: %s\n', pod)
        except:
            logging.warning('Unable to parse Pod name, is it fits the [A-z0-9+-_] pattern?\n')

        if pod:
            isLocal = re.compile(':path => [\'"](.*)[\'"]').search(line)
            if isLocal:
                localPath = isLocal.group(1)
                logging.warning('Pod %s already pointed at local path: %s\n', pod, localPath)
                if not os.path.isdir(localPath):
                    logging.warning('Local path %s for Pod %s does not exists!', localPath, pod)
            else:
                podPath = args.path + pod
                if os.path.isdir(podPath):
                    print 'Found local Pod %s at: %s\n' % (pod, podPath)
                    lineNew = "pod '%s', :path => '%s'" % (pod, podPath)
                    if args.preserve:
                        lineNew = "#%s\n%s" % (line, lineNew)
                    line = lineNew

    podfileNew += '%s\n' % line

podfile.close()

if args.dry:
    print 'The new Podfile:'
    print podfileNew
else:
    podfile = open(args.podfile, 'wb')
    podfile.write(podfileNew)
    print 'Saved new Podfile to: %s' % args.podfile

# EOF
