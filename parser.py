#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os.path
import json
import datetime

import cons

class NoFileError(Exception):
    pass


class TasksParser:

    def __init__(self, tasks_path):
        if os.path.isfile(tasks_path):
            self.tasks_path = tasks_path
        else:
            raise NoFileError('Given file \'{}\' does not exist'.format(
                os.path.split(tasks_path)[1]))
        # update tasks with defined interval
        self.update()

    def add_task(self, text, date=None, interval=None):
        """arguments:
         date -- datetime.date object
         interval -- possible values: number of days, 'month' or 'year'
        """
        tasks = self.get_tasks()
        tasks.append({
            'text': text,
            'date': date.strftime(cons.DATE_FORMAT) if date else date,
            'interval': interval
        })
        self.save_tasks(tasks)

    def remove_task(self, id):
        tasks = self.get_tasks()
        del tasks[id]
        self.save_tasks(tasks)

    def update(self):
        tasks = self.get_tasks()
        for i, task in enumerate(tasks):
            if task['date'] and task['interval']:
                date = datetime.datetime.strptime(task['date'],
                                                  cons.DATE_FORMAT)
                while (datetime.datetime.now() - date).days > 0:
                    interval = task['interval']
                    if type(interval) == int:
                        date += datetime.timedelta(days=int(interval))
                    elif interval == cons.MONTH:
                        if date.month == 12:
                            date = date.replace(year=date.year + 1, month=1)
                        else:
                            date = date.replace(month=date.month + 1)
                    elif interval == cons.YEAR:
                        date = date.replace(year=date.year + 1)
                    tasks[i]['date'] = date.strftime(cons.DATE_FORMAT)
        self.save_tasks(tasks)

    def get_tasks(self):
        try:
            with open(self.tasks_path) as f:
                return json.load(f)
        except ValueError:
            return []

    def save_tasks(self, tasks):
        with open(self.tasks_path, 'w') as f:
            json.dump(tasks, f)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage {} <todo list>'.format(sys.argv[0]))
        sys.exit(1)
    parser = TasksParser(sys.argv[1])
    print(parser)
