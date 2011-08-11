#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os.path
import json
import datetime


class NoFileError(Exception):
    pass


class TasksParser:

    DATE_FORMAT = '%d.%m.%y'
    MONTH = 'month'
    YEAR = 'year'
    
    def __init__(self, tasks_path):
        if os.path.isfile(tasks_path):
            self.tasks_path = tasks_path
        else:
            raise NoFileError('Given file {} does not exist'.format(
                os.path.split(tasks_path)[1]))
        # update tasks with defined interval
        self.update()

    def add_task(self, text, date=None, interval=None):
        """bla bla
        arguments:
         date -- datetime.date object
         interval -- possible values: number of days, 'month' or 'year'
        """
        tasks = []
        try:
            with open(self.tasks_path) as f:
                tasks = json.load(f)
        except ValueError:
            pass
        tasks.append({
            'text': text,
            'date': date.strftime(self.DATE_FORMAT) if date else date,
            'interval': interval
        })
        with open(self.tasks_path, 'w') as f:
            json.dump(tasks, f)

    def remove_task(self, id):
        tasks = []
        with open(self.tasks_path) as f:
            tasks = json.load(f)
        del tasks[id]
        with open(self.tasks_path, 'w') as f:
            json.dump(tasks, f)

    def update(self):
        tasks = []
        try:
            with open(self.tasks_path) as f:
                tasks = json.load(f)
        except ValueError:
            return
        for i, task in enumerate(tasks):
            if task['date']:
                date = datetime.datetime.strptime(task['date'],
                                                  self.DATE_FORMAT)
                if (datetime.datetime.now() - date).days <= 0:
                    continue
                interval = task['interval']
                if type(interval) == int:
                    new_date = date + datetime.timedelta(days=int(interval))
                elif interval == self.MONTH:
                    if date.month == 12:
                        new_date = date.replace(year=date.year + 1, month=1)
                    else:
                        new_date = date.replace(month=date.month + 1)
                elif interval == self.YEAR:
                    new_date = date.replace(year=date.year + 1)
                tasks[i]['date'] = new_date.strftime(self.DATE_FORMAT)
        with open(self.tasks_path, 'w') as f:
            json.dump(tasks, f)


    def __str__(self):
        tasks = []
        try:
            with open(self.tasks_path) as f:
                tasks = json.load(f)
        except ValueError:
            pass
        def print_task(task):
            if task['date']:
                date_obj = datetime.datetime.strptime(task['date'],
                                                      self.DATE_FORMAT)
                date = date_obj.strftime(self.DATE_FORMAT)
                return '{} [{}]'.format(task['text'], date)
            else:
                return task['text']
        output = '\n'.join('{}. {}'.format(n + 1, print_task(task)) \
                for n, task in enumerate(tasks))
        return output


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage {} <todo list>'.format(sys.argv[0]))
        sys.exit(1)
    parser = TasksParser(sys.argv[1])
    print(parser)
