#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse

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
        if not self.is_valid_index(index):
            raise InvalidIndexError('\'{}\' is not a valid index'.format(
                index))
        else:
            self.edit_task(index - 1, done=\
                    not self.get_tasks()[index - 1]['done'])

    def __str__(self):
        return self.list_tasks()

    def list_tasks(self, comp=True, incomp=True, status=True):
        def filter_task(done):
            if comp and incomp:
                return True
            elif comp and done:
                return True
            elif incomp and not done:
                return True
            else:
                return False
        tasks = [task for task in self.get_tasks() \
                if filter_task(task['done'])]

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
        output = '\n'.join('{}. {}'.format(n + 1, format_task(task['text'], \
                task['date'], task['done'])) for n, task in enumerate(tasks))
        return output


def main():
    ap = argparse.ArgumentParser(
            description='A todo list with interval option')
    group = ap.add_mutually_exclusive_group()
    group.add_argument('-a', '--add', nargs='+', metavar='DESCRIPTION',
                       help='add a task')
    group.add_argument('-d', '--delete', nargs=1, type=int, metavar='ID',
                       help='delete a task')
    group.add_argument('-m', '--mark', nargs=1, type=int, metavar='ID',
                       help='mark a task')
    group2 = ap.add_mutually_exclusive_group()
    group2.add_argument('-l', '--list', action='store_true',
                        help='list all tasks')
    group2.add_argument('-c', '--comp', action='store_true',
                        help='list completed tasks')
    group2.add_argument('-i', '--incomp', action='store_true',
                        help='list incompleted tasks')
    ap.add_argument('-s', '--status', action='store_false',
                    help='don\'t show status')
    ap.add_argument('--update', action='store_true', help='update all tasks')

    args = ap.parse_args()
    tl = TaskListCLI(cons.DATA_FILE)
    if args.add:
        tl.add(' '.join(args.add))
    elif args.delete:
        tl.delete(args.delete[0])
    elif args.mark:
        tl.mark(args.mark[0])
    if args.list:
        print(tl.list_tasks(status=args.status))
    elif args.comp:
        print(tl.list_tasks(incomp=False, status=args.status))
    elif args.incomp:
        print(tl.list_tasks(comp=False, status=args.status))


if __name__ == '__main__':
    try:
        main()
    except InvalidIndexError as err:
        raise argparse.ArgumentParser.error(err)
