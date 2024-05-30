__author__ = 'tchen'

'''
Description of the script:
0. used set_theta_offset() to rotate the polar axis so that 0 degree is on the top
1. Read the antenna gain vector in planet format
2. Parse the gain vector in polar coordinate for XY plan and vertical plane (not sure whether it's YZ or XZ plane yet)
3. Save a pdf or eps file with the same file name as the input file name but different extension, unless otherwise given
'''

import numpy as np
import matplotlib.pyplot as pyplot
import re
import sys
import glob
import os
try:
    import config
except ImportError:
    import python_antenna_pattern.config as config

def read_name_list(file_name):
    name_list = []
    try:
        with open(file_name, 'r') as fp:
            for line in fp:
                # strip the return character '\n'
                name_list.append(line.rstrip())
    #except FileNotFoundError:
    # to be python 2.7 compatible....
    except IOError:
        with open(file_name.replace('python_antenna_pattern/', ''), 'r') as fp:
            for line in fp:
                # strip the return character '\n'
                name_list.append(line.rstrip())
    return name_list




class AntennaPattern():
    def __init__(self, options=None):
        self.header_re_pattern = re.compile(r'''
            \s*                 # skip leading white spaces
            (?P<header>[\S]+)   # header name: everything other than white spaces
            \s*                 # white space
            (?P<value>[\S]+)    # value of the header entry
            (?P<rest>.*)        # rest of the line
        ''', re.VERBOSE)
        # should initialize whenever there's a call to parse_ant_by_*
        self.vertical_flag = False
        self.horizontal_flag = False
        self.counter = 0
        self.rho_v = [0.0]*360
        self.rho_h = [0.0]*360
        self.pattern_dict = {} 
        self.max_gain_db = 0
        self.max_gain_db_str = '0'
        self.frequency = 0
        self.name = 'Unknown' # Name added by Strang
        self.file = 'Unknown' # File added by Strang

    def parse_line(self, line):
        m = self.header_re_pattern.match(line)

        if m is None:
            if line == '':
                return
            else:
                print('no matching for line:\n', line)
            return

        # First horizontal then vertical
        if self.horizontal_flag and self.counter < 360:
            self.rho_h[self.counter] = float(m.group('value'))
            self.counter += 1

        if self.vertical_flag and self.counter < 360:
            self.rho_v[self.counter] = float(m.group('value'))
            self.counter += 1
        # TODO: need to make the labels for pattern general
        if m.group('header').lower() == 'horizontal':
            self.counter = 0
            self.pattern_dict['horizontal'] = self.rho_h
            self.horizontal_flag = True
            self.vertical_flag = False

        elif m.group('header').lower() == 'vertical':
            self.counter = 0
            self.pattern_dict['vertical'] = self.rho_v
            self.vertical_flag = True
            self.horizontal_flag = False

        elif m.group('header').lower() == 'frequency':
            self.frequency = int(m.group('value'))

        elif m.group('header').lower() == 'name': # Name added by Strang
            self.name = m.group('value') + m.group('rest')

        elif m.group('header').lower() == 'gain':
            self.max_gain_db = float(m.group('value'))
            if m.group('rest').lower() == ' dbd':
                if config.VERBOSE is True:
                    print('Converting to dBi (+2.14) from', m.group('value') + m.group('rest'))
                self.max_gain_db += 2.14 # 0 dBd = 2.14 dBi, added by Strang
            # Parse the max gain in string so that tht title can be set accordingly
            # m = header_re_pattern.match(line)
            self.max_gain_db_str = str(self.max_gain_db) #m.group('value') + m.group('rest'), added by Strang

    def parse_data(self, file_name):
        return self.parse_data_by_ant(file_name)

    def parse_data_by_ant(self, file_name):
        if config.VERBOSE is True:
            print('opening file ', file_name)
    
        with open(file_name, 'r') as fp:
            self.file = file_name
            for line in fp:
                self.parse_line(line) 

        return True

    def simulate_data(self, gain, band, tilt = 0):
        theta = np.arange(0, 360, 1)*np.pi/180.0
        self.name = 'Pattern simulation with beam width 59/7'
        self.frequency = band
        self.max_gain_db = gain
        self.tilt = tilt
        self.pattern_dict['horizontal'] = np.round((-15*(1 - np.sin(theta-np.pi/2))+30)*1.5, 2)
        self.pattern_dict['vertical'] = np.round((-15*(1-np.sin((theta+(-90-27-tilt)/180*np.pi)*10))+30)*1.0, 2)
        for l in range(int(360/10/2+tilt), 360-int(360/10/2-tilt)):
            self.pattern_dict['vertical'][l] = 50 if (90+tilt <= l < 270+tilt) else (self.pattern_dict['vertical'][l]+20)
        return True

    def save_data(self, file_name):
        #if config.VERBOSE is True:
        print('saving file ', file_name)
    
        with open(file_name, 'w') as fp:
            self.file = file_name
            fp.write("NAME " + self.name + "\n")
            fp.write("FREQUENCY " + str(self.frequency) + "\n")
            fp.write("GAIN " + str(self.max_gain_db) + " dBi\n")
            fp.write("COMMENT {:02d}T degree downtilt\n".format(self.tilt))
            counter = 0
            fp.write("HORIZONTAL 360\n")
            for val in self.pattern_dict['horizontal']:
                fp.write(str(counter) + " {:.2f}\n".format(val))
                counter += 1
            counter = 0
            fp.write("VERTICAL 360\n")
            for val in self.pattern_dict['vertical']:
                fp.write(str(counter) + " {:.2f}\n".format(val))
                counter += 1

        return True

