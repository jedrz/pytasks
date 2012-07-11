#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import operator

import parser
import cons


class InvalidIndexError(Exception):
    pass


class TaskListCLI(parser.TaskParser):

    def is_valid_index(self, index):
        return 0 < index <= len(self.get_tasks())

    def add(self, text):
        self.add_task(text)

    def delete(self, index):
        if not self.is_valid_index(index):
            raise InvalidIndexError('\'{}\' is not a valid index'.format(
                index))
        else:
            self.delete_task(index - 1)

    def mark(self, index):
        """Change the status of the task."""
        if not self.is_valid_index(index):
            raise InvalidIndexError('\'{}\' is not a valid index'.format(
                index))
        else:
            self.edit_task(index - 1, done=\
                    not self.get_tasks()[index - 1]['done'])

    def __str__(self):
        return self.list_tasks()

    def list_tasks(self, comp=True, incomp=True, status=True, number=True,
                   sort=False):
        """Return a formatted string with proper tasks.

        arguments:
        comp -- show completed tasks
        incomp -- show incompleted tasks
        status -- show status of tasks
        number -- show numbered tasks
        sort -- show sorted tasks by date

        By default the method returns formatted string with numbered all tasks
        and their status.
        """
        def filter_task(date, done):
            passed = False
            if comp and incomp:
                passed = True
            elif comp and done:
                passed = True
            elif incomp and not done:
                passed = True
            else:
                passed = False
            if passed and sort and not date:
                passed = False
            return passed
        tasks = [task for task in self.get_tasks() \
                if filter_task(task['date'], task['done'])]
        if sort:
            tasks = sorted(tasks, key=operator.itemgetter('date'))
        def format_task(text, date, done):
            if date:
                date = date.strftime(cons.DATE_FORMAT)
                s = '{} ({})'.format(text, date)
                if status:
                    if done:
                        return '[*] {}'.format(s)
                    else:
                        return '[ ] {}'.format(s)
                else:
                    return s
            else:
                if status:
                    if done:
                        return '[*] {}'.format(text)
                    else:
                        return '[ ] {}'.format(text)
                else:
                    return text
        if number:
            return '\n'.join('{}. {}'.format(n + 1, format_task(
                task['text'],
                task['date'],
                task['done']
                )) for n, task in enumerate(tasks))
        else:
            return '\n'.join(format_task(
                task['text'],
                task['date'],
                task['done']
                ) for task in tasks)


def main():
    ap = argparse.ArgumentParser(
            description='A todo list with interval option')
    ap.add_argument('-a', '--add', nargs='+', metavar='DESCRIPTION',
                    help='add a task')
    ap.add_argument('-d', '--delete', nargs=1, type=int, metavar='ID',
                    help='delete a task')
    ap.add_argument('-m', '--mark', nargs=1, type=int, metavar='ID',
                    help='mark a task')
    ap.add_argument('-l', '--list', action='store_true',
                    help='list all tasks')
    ap.add_argument('-c', '--comp', action='store_true',
                    help='list completed tasks')
    ap.add_argument('-i', '--incomp', action='store_true',
                    help='list incompleted tasks')
    ap.add_argument('--sorted', action='store_true',
                    help='tasks with date sorted by it')
    ap.add_argument('-s', '--status', action='store_false',
                    help='don\'t show status')
    ap.add_argument('-n', '--number', action='store_false',
                    help='tasks not numbered')
    ap.add_argument('--update', action='store_true', help='update all tasks')

    args = ap.parse_args()
    tl = TaskListCLI(cons.DATA_FILE)
    if args.add:
        tl.add(' '.join(args.add))
    elif args.delete:
        tl.delete(args.delete[0])
    elif args.mark:
        tl.mark(args.mark[0])
    elif args.list:
        print(tl.list_tasks(status=args.status, number=args.number,
                            sort=args.sorted))
    elif args.comp:
        print(tl.list_tasks(incomp=False, status=args.status,
                            number=args.number, sort=args.sorted))
    elif args.incomp:
        print(tl.list_tasks(comp=False, status=args.status,
                            number=args.number, sort=args.sorted))


if __name__ == '__main__':
    try:
        main()
    except InvalidIndexError as err:
        raise argparse.ArgumentParser.error(err)
