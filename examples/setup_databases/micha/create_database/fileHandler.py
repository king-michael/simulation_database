"""
_info_ fileHandler
"""

import logging
logger = logging.getLogger('SetupDatabase')
logger.info("fileHandler: imported from: %s",__file__)

import os

class FileHandler():
    def __init__(self):
        self.list_comments = ['#']

    def get_data_from_file(self,fname,path=None):
        """reads the file
        :returns: dict of file context"""
        if path is not None: # in case we provide a path
            fname = os.path.join(path, fname)
        # Create a dict to store data in
        data={}

        with open(fname, 'r') as fp:
            for line in fp:
                line_strip = line.strip()
                if len(line_strip) == 0: continue  # empty lines
                if line_strip[0] in self.list_comments: continue  # comments
                line_split = line_strip.split(":", 1)  # max split 1
                if len(line_split) == 2:
                    data[line_split[0].strip()] = line_split[1].strip()
        return data
