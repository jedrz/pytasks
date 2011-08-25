#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os.path
import json
import datetime

import cons


class NoFileError(Exception):
    pass


class TaskParser:

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
            'interval': interval,
            'done': False
        })
        self.save_tasks(tasks)

    def remove_task(self, id):
        tasks = self.get_tasks()
        del tasks[id]
        self.save_tasks(tasks)

    def edit_task(self, id, text=None, date=None, interval=None, done=None):
        tasks = self.get_tasks()
        t = tasks[id]
        t['text'] = text or t['text']
        t['date'] = date or t['date']
        t['interval'] = interval or t['interval']
        t['done'] = done or t['done']
        tasks[id] = t
        self.save_tasks(tasks)


    def update(self):
        tasks = self.get_tasks()
        for i, task in enumerate(tasks):
            if not (task['date'] and task['interval']):
                continue
            date = datetime.datetime.strptime(task['date'], cons.DATE_FORMAT)
            interval = task['interval']
            while (datetime.datetime.now() - date).days > 0:
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
    # test (sys.argv[1] -- todo file)
    import sys
    parser = TaskParser(sys.argv[1])
    parser.add_task('one')
    parser.add_task('two two')
    parser.add_task('three three three')
    parser.edit_task(2, 'four x 4')
    parser.remove_task(0)
    print(parser.get_tasks())
