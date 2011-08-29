#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import os.path


NAME = 'PyTasks'
DATA_FILENAME = 'todo.txt'
DATA_DIR = os.path.join(os.getenv('XDG_DATA_HOME'), NAME.lower())
DATA_FILE = os.path.join(DATA_DIR, DATA_FILENAME)

def create_conf():
    if not os.path.isdir(DATA_DIR):
        try:
            os.mkdir(DATA_DIR)
        except OSError:
            print('{} cannot be created, dir exists'.format(DATA_DIR))
    if not os.path.isfile(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            pass

create_conf()

DATE_FORMAT = '%d.%m.%y'
MONTH = 'month'
YEAR = 'year'
DAYS = int

COLUMN_ID = 0
COLUMN_DONE = 1
COLUMN_DATE = 2
COLUMN_INTERVAL = 3
COLUMN_TEXT = 4

COMBOBOX_INTERVAL_NONE = 0
COMBOBOX_INTERVAL_MONTH = 1
COMBOBOX_INTERVAL_YEAR = 2
COMBOBOX_INTERVAL_DAYS = 3

RESPONSE_CLEAR = -13

WINDOW_SCHEMA = 'glade/window.glade'
DIALOG_ADD_SCHEMA = 'glade/dialog-add.glade'
DIALOG_DELETE_SCHEMA = 'glade/dialog-delete.glade'
DIALOG_CALENDAR_SCHEMA = 'glade/dialog-calendar.glade'