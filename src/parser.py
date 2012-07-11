#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os.path
import json
import datetime
import operator

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

    def get_tasks(self):
        """Return a list with tasks.

        If file is empty return an empty list.
        """
        with open(self.tasks_path) as f:
            try:
                tasks = json.load(f)
            except ValueError:
                return []
            else:
                for i, task in enumerate(tasks):
                    if not task['date']:
                        continue
                    date = datetime.datetime.strptime(task['date'],
                            cons.DATE_FORMAT)
                    date = datetime.date(date.year, date.month, date.day)
                    tasks[i]['date'] = date
                return tasks

    def save_tasks(self, tasks):
        """Save tasks in the file.

        The file is being cleaned and written with the tasks list.
        """
        with open(self.tasks_path, 'w') as f:
            for i, task in enumerate(tasks):
                if task['date']:
                    # convert date from datetime.date object
                    # to a formatted string
                    tasks[i]['date'] = task['date'].strftime(cons.DATE_FORMAT)
            json.dump(tasks, f)

    def add_task(self, text=None, date=None, interval=None, done=False):
        """Add a task and save in the todo file.

        arguments:
        text -- description of the task
        date -- datetime.date object
        interval -- possible values: number of days, 'month' (cons.MONTH)
            or 'year' (cons.YEAR)
        done -- status of the task (by default False)
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
        """Delete a task pointed by the index."""
        tasks = self.get_tasks()
        del tasks[index]
        self.save_tasks(tasks)

    def edit_task(self, index, **task):
        """Edit a task pointed by the index.
        Similar to add_task method.
        """
        tasks = self.get_tasks()
        # dirty solution
        if task.get('text', -1) != -1:
            tasks[index]['text'] = task['text']
        if task.get('date', -1) != -1:
            tasks[index]['date'] = task['date']
        if task.get('interval', -1) != -1:
            tasks[index]['interval'] = task['interval']
        if task.get('done') in (False, True):
            tasks[index]['done'] = task['done']
        self.save_tasks(tasks)

    def swap_task(self, index_a, index_b):
        """Move a task from an index to another one."""
        tasks = self.get_tasks()
        tasks[index_a], tasks[index_b] = tasks[index_b], tasks[index_a]
        self.save_tasks(tasks)

    def update(self):
        """Update tasks with specified interval option.
        
        Basically this method updates date param when interval is set.
        """
        tasks = self.get_tasks()
        for i, task in enumerate(tasks):
            if not (task['date'] and task['interval']):
                continue
            date = task['date']
            interval = task['interval']
            while (datetime.date.today() - date).days > 0:
                if isinstance(interval, int):
                    date += datetime.timedelta(days=interval)
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


if __name__ == '__main__':
    # test (sys.argv[1] -- todo file)
    import sys
    parser = TaskParser(sys.argv[1])
    parser.add_task('one')
    parser.add_task('two two')
    parser.add_task('three three three')
    parser.edit_task(2, text='four x 4',date=datetime.date.today(),
                     interval='month')
    parser.delete_task(0)
    print(parser.get_tasks())
