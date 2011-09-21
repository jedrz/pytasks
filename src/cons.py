#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os
import os.path
import datetime


NAME = 'PyTasks'
DATA_FILENAME = 'todo.txt'
DATA_DIR = os.path.join(os.getenv('XDG_DATA_HOME'), NAME.lower())
DATA_FILE = os.path.join(DATA_DIR, DATA_FILENAME)

def create_conf():
    """Create an empty todo list file."""
    if not os.path.isdir(DATA_DIR):
        try:
            os.mkdir(DATA_DIR)
        except OSError:
            print('\'{}\' cannot be created, file or symlink exists'.format(
                DATA_DIR))
            sys.exit(1)
    if not os.path.isfile(DATA_FILE):
        try:
            with open(DATA_FILE, 'w') as f:
                pass
        except IOError:
            print('\'{}\' cannot be created, dir or symlink exists'.format(
                DATA_FILE))
            sys.exit(1)

create_conf()

DATE_FORMAT = '%d.%m.%y'

MONTH = 'month'
YEAR = 'year'
DAYS = int

TEXT_TYPES = (str, )
DATE_TYPES = (datetime.date, )
INTERVAL_VALUES = (MONTH, YEAR)
INTERVAL_TYPES = (int, )
DONE_TYPES = (True, False)

COLUMN_ID = 0
COLUMN_DONE = 1
COLUMN_DATE = 2
COLUMN_INTERVAL = 3
COLUMN_TEXT = 4

COMBOBOX_INTERVAL_NONE = 0
COMBOBOX_INTERVAL_MONTH = 1
COMBOBOX_INTERVAL_YEAR = 2
COMBOBOX_INTERVAL_DAYS = 3

WINDOW_SCHEMA = 'glade/window.glade'
DIALOG_ADD_SCHEMA = 'glade/dialog-add.glade'
DIALOG_DELETE_SCHEMA = 'glade/dialog-delete.glade'
DIALOG_CALENDAR_SCHEMA = 'glade/dialog-calendar.glade'
DIALOG_ABOUT_SCHEMA = 'glade/dialog-about.glade'
