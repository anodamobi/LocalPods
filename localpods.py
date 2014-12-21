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
parser.add_argument('--version', action='version', version='%(prog)s 1.2')
parser.add_argument('-v', dest='verbose', action='store_true', help='verbose output')
parser.add_argument('--pods', dest='pods', type=str, help='local Pods folder path (default is parent dir)')
parser.add_argument('--podfile', dest='podfile', type=str, help='Podfile path (default is ./Podfile)')
parser.add_argument('-d', '--dry-run', dest='dry', action='store_true', help='perform a trial run with no changes made')
parser.add_argument('-o', '--preserve-original', dest='preserve', action='store_true', help='preserve original lines with comments')
parser.add_argument('-g', '--group', dest='group', action='store_true', help='group local pods')
parser.add_argument('-r', '--runupdate', dest='runupdate', action='store_true', help='run `pod update` after saving')
parser.add_argument('-c', '--config', dest='config', default='~/.localpods', type=str, help='config file (default is ~/.localpods)')
parser.add_argument('--generate-config', dest='generateConfig', action='store_true', help='generate config file interactively and exit')

args = parser.parse_args()

args.config = os.path.expanduser(args.config)


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

    with open(args.config, 'wb') as file:
        config.write(file)
    exit()
# / config generator


# Enable verbose or dry run if needed
if args.verbose:
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
else:
    logging.basicConfig(format='%(levelname)s: %(message)s')

if args.dry:
    print 'Performing a trial run with no changes made\n'

# read config file
config = ConfigParser.ConfigParser()
config.read(args.config)

options = {
    'pods': '..',
    'podfile': 'Podfile',
    'preserve': parser.get_default('preserve'),
    'group': parser.get_default('group'),
    'runupdate': parser.get_default('runupdate')
}

if config.has_option('localpods', 'pods'):
    options['pods'] = config.get('localpods', 'pods')

if config.has_option('localpods', 'preserve'):
    options['preserve'] = config.getboolean('localpods', 'preserve')

if config.has_option('localpods', 'group'):
    options['group'] = config.getboolean('localpods', 'group')

if config.has_option('localpods', 'runupdate'):
    options['runupdate'] = config.getboolean('localpods', 'runupdate')
# / read config file


# expand ~ in pods path and make it absolute
if args.pods[0] == '~':
    args.pods = os.path.expanduser(args.pods)
args.pods = os.path.abspath(args.pods) + '/'

# expand ~ in podfile path and make it absolute
if args.podfile[0] == '~':
    args.podfile= os.path.expanduser(args.podfile)
args.podfile = os.path.abspath(args.podfile)


logging.debug('Using Local Pods folder: %s', args.pods)
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
podfileNewGroupOld = ''
podfileNewGroupNew = ''

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
                podPath = args.pods + pod
                if os.path.isdir(podPath):
                    print 'Found local Pod %s at: %s\n' % (pod, podPath)
                    if args.group:
                        line
                    else:
                        lineNew = "pod '%s', :path => '%s'" % (pod, podPath)
                        if args.preserve:
                            lineNew = "#%s\n%s" % (line, lineNew)
                        line = lineNew

    podfileNew += '%s\n' % line

podfile.close()

# Append bottom part of new podfile
if len(podfileNewGroupOld) > 0:
    podfileNew += '\n# ORIGINAL LOCAL PODS\n'
    podfileNew += podfileNewGroupOld + '\n'
    podfileNew += '\n# LOCAL PODS\n'
    podfileNew += podfileNewGroupNew


if args.dry:
    print 'The new Podfile:'
    print podfileNew
else:
    podfile = open(args.podfile, 'wb')
    podfile.write(podfileNew)
    print 'Saved new Podfile to: %s' % args.podfile
    if args.runupdate:
        print 'Running `pod update`'
        os.system('pod update')

# EOF
