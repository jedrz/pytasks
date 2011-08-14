#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import datetime
import argparse

import parser
import cons


class InvalidIndexError(Exception):
    pass


class TasksList(parser.TasksParser):

    def is_valid_index(self, id):
        return 0 < id <= len(self.get_tasks())

    def add(self, text):
        self.add_task(text)

    def edit(self, id, text):
        tasks = self.get_tasks()
        if not self.is_valid_index(id):
            raise InvalidIndexError('\'{}\' is not a valid index'.format(id))
        else:
            tasks[id - 1]['text'] = text
            self.save_tasks(tasks)

    def remove(self, id):
        if not self.is_valid_index(id):
            raise InvalidIndexError('\'{}\' is not a valid index'.format(id))
        else:
            self.remove_task(id - 1)

    def __str__(self):
        tasks = self.get_tasks()
        def print_task(task):
            if task['date']:
                date_obj = datetime.datetime.strptime(task['date'],
                                                      cons.DATE_FORMAT)
                date = date_obj.strftime(cons.DATE_FORMAT)
                return '{} [{}]'.format(task['text'], date)
            else:
                return task['text']
        output = '\n'.join('{}. {}'.format(n + 1, print_task(task)) \
                for n, task in enumerate(tasks))
        return output


def main():
    ap = argparse.ArgumentParser(
            description='A todo list with interval option')
    ap.add_argument('path', help='a path to the todo list')
    ap.add_argument('-l', '--list', action='store_true',
                    help='list all tasks') # means do nothing
    ap.add_argument('--update', action='store_true', help='update all tasks')
    group = ap.add_mutually_exclusive_group()
    group.add_argument('-a', '--add', nargs='+', metavar='DESCRIPTION',
                       help='add a task')
    group.add_argument('-e', '--edit', nargs='+',
                       metavar=('ID', 'DESCRIPTION'), help='edit a task')
    group.add_argument('-r', '--remove', nargs=1, type=int, metavar='ID',
                       help='remove a task')
    args = ap.parse_args()

    try:
        tl = TasksList(args.path)
    except parser.NoFileError as err:
        print(err)
        sys.exit(1)
    if args.add:
        tl.add(' '.join(args.add))
    elif args.edit:
        id = int(args.edit[0])
        text = ' '.join(args.edit[1:])
        tl.edit(id, text)
    elif args.remove:
        tl.remove(args.remove[0])
    if args.list:
        print(tl)


if __name__ == '__main__':
    main()
