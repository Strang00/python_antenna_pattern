__author__ = 'tchen'
__project__ = 'python-antenna-pattern'
__version__ = '1.0.4 Strang\'s edition'

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
        self.tilt_re_pattern = re.compile(r'''
            .*_([Tt](?P<value1>\d\d)|(?P<value2>\d\d)D?[Tt])[._].*
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
        self.tilt = 0
        self.merged_files = []

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
            self.frequency = int(float(m.group('value')))

        elif m.group('header').lower() == 'electrical_tilt':
            old_tilt = self.tilt
            self.tilt = int(m.group('value'))
            if (old_tilt != self.tilt and old_tilt != 0):
            #if config.VERBOSE is True:
                print("Updated tilt {tilt1} to electrical_tilt {tilt2} in {file}".format(tilt1 = old_tilt, tilt2 = self.tilt, file=self.file))

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
            m = self.tilt_re_pattern.match(file_name)
            if (m is not None):
                self.tilt = int((m.group("value1") if m.group("value1") else '') + (m.group("value2") if m.group("value2") else ''))
                if config.VERBOSE is True:
                    print("Parsed tilt {tilt} from {file}".format(tilt = self.tilt, file=self.file))
            for line in fp:
                self.parse_line(line) 

        return True

    # Simulate radiation pattern 59/7 with cardioida
    # TODO: extend pattern generation with passing target width
    # See Numerical modeling of antenna radiation patterns with a sin(x)/x function at
    # https://people.eecs.ku.edu/~callen58/725/Numerical_modeling_of_antenna_radiation_patterns.pdf
    def simulate_data(self, gain, band, tilt = 0):
        theta = np.arange(0, 360, 1)*np.pi/180.0
        self.name = 'Pattern simulation with beam width 59/7'
        self.frequency = band
        self.max_gain_db = gain
        self.tilt = tilt
        self.pattern_dict['horizontal'] = self.rho_h = np.round((-15*(1 - np.sin(theta-np.pi/2))+30)*1.5, 2)
        self.pattern_dict['vertical'] = self.rho_v = np.round((-15*(1-np.sin((theta+(-90-27-tilt)/180*np.pi)*10))+30)*1.0, 2)
        for l in range(int(360/10/2+tilt), 360-int(360/10/2-tilt)):
            self.pattern_dict['vertical'][l] = 50 if (90+tilt <= l < 270+tilt) else (self.pattern_dict['vertical'][l]+20)
        return True

    def offset_data(self, delta_hor, delta_ver):
        if (delta_hor != 0):
            print('Rotating horizontal pattern at {}'.format(delta_hor))
            buf_rho_h = list(self.rho_h)
        if (delta_ver != 0):
            print('Rotating vertical pattern at {}'.format(delta_ver))
            buf_rho_v = list(self.rho_v)
        for l in range(0, 360):
            if (delta_hor != 0):
                self.rho_h[(l + delta_hor + 360) % 360] = buf_rho_h[l]
            if (delta_ver != 0):
                self.rho_v[(l + delta_ver + 360) % 360] = buf_rho_v[l]

    def save_data(self, file_name):
        #if config.VERBOSE is True:
        print('saving file ', file_name)
    
        with open(file_name, 'w') as fp:
            self.file = file_name
            fp.write("NAME " + self.name + "\n")
            fp.write("FREQUENCY " + str(self.frequency) + "\n")
            fp.write("GAIN " + "{:.2f}".format(self.max_gain_db) + " dBi\n")
            fp.write("ELECTRICAL_TILT {:02d}\n".format(self.tilt))
            fp.write("COMMENT {:02d}T degree downtilt, generated by {} v{}\n".format(self.tilt, __project__, __version__))
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

    # Merge pointed antenna pattern to self using simple mininum for loss values (best signal)
    def merge_from(self, ant2):
        if (ant2 is None):
            return False
        if (self.frequency != ant2.frequency):
            print('Antenna merge skipped from {file2} to {file1}: different FREQUENCY'
                  .format(file1=self.file, file2=ant2.file))
            return False
        if (self.tilt != ant2.tilt):
            print('Antenna merge skipped from {file2} to {file1}: different TILT {tilt2} and {tilt1}'
                  .format(file1=self.file, file2=ant2.file, tilt2=ant2.tilt, tilt1=self.tilt))
        if (self.file == ant2.file):
            print('Antenna merge skipped from {file2} to {file1}: same file'
                  .format(file1=self.file, file2=ant2.file))
            return False
        if (ant2.file in self.merged_files):
            print('Antenna merge skipped from {file2} to {file1}: already merged'
                  .format(file1=self.file, file2=ant2.file))
            return False

        g_self = 0
        g_ant2 = 0
        if (self.max_gain_db != ant2.max_gain_db):
            if (self.max_gain_db < ant2.max_gain_db):
                g_self = ant2.max_gain_db - self.max_gain_db
                self.max_gain_db = ant2.max_gain_db
            else:
                g_ant2 = self.max_gain_db - ant2.max_gain_db
            
        for i in range(360):
            self.rho_h[i] = min(self.rho_h[i] + g_self, ant2.rho_h[i] + g_ant2)
            self.rho_v[i] = min(self.rho_v[i] + g_self, ant2.rho_v[i] + g_ant2)
        self.merged_files.append(ant2.file)
        
        if len(self.merged_files) == 1:
            self.name += ' MERGED'        
        return True
        
