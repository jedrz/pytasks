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

    def add_task(self, text=None, date=None, interval=None, done=False):
        """arguments:
         date -- datetime.date object
         interval -- possible values: number of days, 'month' or 'year'
        """
        tasks = self.get_tasks()
        tasks.append({
            'text': text,
            'date': date,
            'interval': interval,
            'done': done
        })
        self.save_tasks(tasks)

    def delete_task(self, index):
        tasks = self.get_tasks()
        del tasks[index]
        self.save_tasks(tasks)

    def edit_task(self, index, text=None, date=None, interval=None,
                  done=None):
        tasks = self.get_tasks()
        t = tasks[index] # shortcut
        t['text'] = text or t['text']
        t['date'] = date or t['date']
        t['interval'] = interval or t['interval']
        if done in (True, False):
            t['done'] = done
        tasks[index] = t
        self.save_tasks(tasks)

    def swap_task(self, index_a, index_b):
        tasks = self.get_tasks()
        tasks[index_a], tasks[index_b] = tasks[index_b], tasks[index_a]
        self.save_tasks(tasks)

    def update(self):
        tasks = self.get_tasks()
        for i, task in enumerate(tasks):
            if not (task['date'] and task['interval']):
                continue
            date = task['date']
            interval = task['interval']
            while (datetime.date.today() - date).days > 0:
                if type(interval) == int:
                    date += datetime.timedelta(days=int(interval))
                elif interval == cons.MONTH:
                    if date.month == 12:
                        date = date.replace(year=date.year + 1, month=1)
                    else:
                        # fix for february and 30 days months
                        day = date.day
                        while True:
                            try:
                                date = date.replace(month=date.month + 1,
                                                    day=day)
                            except ValueError:
                                day -= 1
                            else:
                                break
                elif interval == cons.YEAR:
                    date = date.replace(year=date.year + 1)
                tasks[i]['date'] = date
        self.save_tasks(tasks)

    def get_tasks(self):
        try:
            with open(self.tasks_path) as f:
                tasks = json.load(f)
                for i, task in enumerate(tasks):
                    if not task['date']:
                        continue
                    date = datetime.datetime.strptime(task['date'],
                            cons.DATE_FORMAT)
                    date = datetime.date(date.year, date.month, date.day)
                    tasks[i]['date'] = date
                return tasks
        except ValueError:
            return []

    def save_tasks(self, tasks):
        with open(self.tasks_path, 'w') as f:
            for i, task in enumerate(tasks):
                if task['date']:
                    tasks[i]['date'] = task['date'].strftime(cons.DATE_FORMAT)
            json.dump(tasks, f)


if __name__ == '__main__':
    # test (sys.argv[1] -- todo file)
    import sys
    parser = TaskParser(sys.argv[1])
    parser.add_task('one')
    parser.add_task('two two')
    parser.add_task('three three three')
    parser.edit_task(2, text='four x 4',date=datetime.date.today(),
                     interval=cons.MONTH)
    parser.remove_task(0)
    print(parser.get_tasks())
