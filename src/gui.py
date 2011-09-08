#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import datetime

from gi.repository import Gtk

import parser
import cons


class GtkBuilderProxy:
    """A simple proxy for Gtk.Builder.

    Give possibility to get a object by accessing its as an attribute.
    """

    def __init__(self, builder):
        self._builder = builder

    def __getattr__(self, name):
        return self._builder.get_object(name)


class DialogCalendar:

    def __init__(self, date=datetime.date.today()):
        builder = Gtk.Builder()
        builder.add_from_file(cons.DIALOG_CALENDAR_SCHEMA)
        self.widgets = GtkBuilderProxy(builder)
        self.date = date

    def run(self):
        # range of month in gtk calendar is 0..11
        self.widgets.calendar.select_month(self.date.month - 1, self.date.year)
        self.widgets.calendar.select_day(self.date.day)
        result = self.widgets.dialog.run()
        year, month, date = self.widgets.calendar.get_date()
        date_obj = datetime.date(year, month + 1, date)
        self.widgets.dialog.destroy()
        return result, date_obj


class DialogAdd:

    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file(cons.DIALOG_ADD_SCHEMA)
        builder.connect_signals(self)
        self.widgets = GtkBuilderProxy(builder)
        self.task = {'done': False, 'date': None}

    def run(self):
        result = self.widgets.dialog.run()
        self.task['text'] = self.widgets.entry_text.get_text() or None
        active = self.widgets.combobox_interval.get_active()
        if active == cons.COMBOBOX_INTERVAL_MONTH:
            self.task['interval'] = cons.MONTH
        elif active == cons.COMBOBOX_INTERVAL_YEAR:
            self.task['interval'] = cons.YEAR
        elif active == cons.COMBOBOX_INTERVAL_DAYS:
            self.task['interval'] = \
                    self.widgets.spinbutton_days.get_value_as_int()
        elif active == cons.COMBOBOX_INTERVAL_NONE:
            self.task['interval'] = None
        self.widgets.dialog.destroy()
        return result, self.task

    def on_combobox_interval_changed(self, combobox):
        """Set sensitive attribute of spinbutton depending on combobox 
        value.
        """
        if combobox.get_active() == cons.COMBOBOX_INTERVAL_DAYS:
            self.widgets.spinbutton_days.set_sensitive(True)
        else:
            self.widgets.spinbutton_days.set_sensitive(False)

    def on_entry_date_icon_press(self, entry, position, event):
        dialog_calendar = DialogCalendar()
        result_calendar, date = dialog_calendar.run()
        if result_calendar == Gtk.ResponseType.OK:
            self.task['date'] = date
            self.widgets.entry_date.set_text(date.strftime(cons.DATE_FORMAT))
        elif result_calendar == cons.RESPONSE_CLEAR:
            self.task['date'] = None
            self.widgets.entry_date.set_text('')


class DialogDelete:

    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file(cons.DIALOG_DELETE_SCHEMA)
        self.widgets = GtkBuilderProxy(builder)

    def run(self):
        result = self.widgets.dialog.run()
        self.widgets.dialog.destroy()
        return result


class DialogEdit(DialogAdd):
    
    def __init__(self, task):
        super(DialogEdit, self).__init__()
        self.set_values(task)

    def set_values(self, task):
        self.widgets.entry_text.set_text(task['text'])
        self.widgets.entry_date.set_text(task['date'].strftime(
            cons.DATE_FORMAT))
        interval = task['interval']
        if interval == cons.MONTH:
            self.widgets.combobox_interval.set_active(
                    cons.COMBOBOX_INTERVAL_MONTH)
        elif interval == cons.YEAR:
            self.widgets.combobox_interval.set_active(
                    cons.COMBOBOX_INTERVAL_YEAR)
        elif isinstance(interval, cons.DAYS):
            self.widgets.combobox_interval.set_active(
                    cons.COMBOBOX_INTERVAL_DAYS)
            self.widgets.spinbutton_days.set_value(interval)
        else:
            self.widgets.combobox_interval.set_active(
                    cons.COMBOBOX_INTERVAL_NONE)


class TaskListGUI:

    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file(cons.WINDOW_SCHEMA)
        builder.connect_signals(self)

        self.widgets = GtkBuilderProxy(builder)
        self.widgets.window.show_all()

        self.parser = parser.TaskParser(cons.DATA_FILE)

        self.set_column_func()
        self.update_liststore()

    def set_column_func(self):
        """Add a function to treeview columns controlling strikethrough
        property depending on status of the task.
        """
        def make_strikethrough(column, cell, model, it, data):
            if model.get_value(it, cons.COLUMN_DONE):
                cell.set_property('strikethrough', True)
            else:
                cell.set_property('strikethrough', False)
        self.widgets.treeviewcolumn_date.set_cell_data_func(
                self.widgets.cellrenderertext_date,
                make_strikethrough
        )
        self.widgets.treeviewcolumn_interval.set_cell_data_func(
                self.widgets.cellrenderertext_interval,
                make_strikethrough
        )
        self.widgets.treeviewcolumn_text.set_cell_data_func(
                self.widgets.cellrenderertext_text,
                make_strikethrough
        )

    def update_liststore(self):
        """Clear and add tasks to liststore object."""
        # count of tasks
        self._index = 0
        self.widgets.liststore.clear()
        tasks = self.parser.get_tasks()
        for task in tasks:
            self.add_task_liststore(task)

    def _get_date(self, date):
        if date:
            return date.strftime(cons.DATE_FORMAT)
        return ''

    def _get_interval(self, interval):
        if interval == cons.MONTH:
            return 'miesiąc'
        elif interval == cons.YEAR:
            return 'rok'
        elif isinstance(interval, cons.DAYS):
            return '{} dni'.format(interval)
        return ''

    def add_task_liststore(self, task):
        self.widgets.liststore.append([
            self._index,
            task['done'],
            self._get_date(task['date']),
            self._get_interval(task['interval']),
            task['text']
        ])
        self._index += 1

    def edit_task_liststore(self, it, task):
        self.widgets.liststore.set_value(it,
                cons.COLUMN_DATE, self._get_date(task['date']))
        self.widgets.liststore.set_value(it,
                cons.COLUMN_INTERVAL, self._get_interval(task['interval']))
        self.widgets.liststore.set_value(it, cons.COLUMN_TEXT, task['text'])

    def on_window_destroy(self, window):
        Gtk.main_quit()

    def on_toolbutton_add_clicked(self, button):
        dialog_add = DialogAdd()
        result, task = dialog_add.run()
        if result != Gtk.ResponseType.OK:
            return
        self.add_task_liststore(task)
        self.parser.add_task(**task)

    def on_toolbutton_delete_clicked(self, button):
        model, it = self.widgets.treeview_selection.get_selected()
        if not it:
            return
        dialog_delete = DialogDelete()
        result = dialog_delete.run()
        if result != Gtk.ResponseType.OK:
            return
        index = model.get_value(it, cons.COLUMN_ID)
        self.parser.delete_task(index)
        self.update_liststore()

    def on_toolbutton_edit_clicked(self, button):
        model, it = self.widgets.treeview_selection.get_selected()
        if not it:
            return
        index = model.get_value(it, cons.COLUMN_ID)
        tasks = self.parser.get_tasks()
        dialog_edit = DialogEdit(tasks[index])
        result, task = dialog_edit.run()
        if result != Gtk.ResponseType.OK:
            return
        self.edit_task_liststore(it, task)
        self.parser.edit_task(index, **task)

    def on_toolbutton_done_clicked(self, button):
        model, it = self.widgets.treeview_selection.get_selected()
        if not it:
            return
        index = model.get_value(it, cons.COLUMN_ID)
        value = model.get_value(it, cons.COLUMN_DONE)
        model.set_value(it, cons.COLUMN_DONE, not value)
        self.parser.edit_task(index, done=not value)

    def on_toolbutton_down_clicked(self, button):
        model, it = self.widgets.treeview_selection.get_selected()
        if not it:
            return
        next_it = model.iter_next(it)
        if not next_it:
            next_it = model.get_iter_first()
        model.swap(it, next_it)
        index_a = model.get_value(it, cons.COLUMN_ID)
        index_b = model.get_value(next_it, cons.COLUMN_ID)
        model.set_value(it, cons.COLUMN_ID, index_b)
        model.set_value(next_it, cons.COLUMN_ID, index_a)
        self.parser.swap_task(index_a, index_b)

    def on_toolbutton_up_clicked(self, button):
        return
        model, it = self.widgets.treeview_selection.get_selected()
        if not it:
            return
        # FIXME doesn't work
        index_a = model.get_value(it, cons.COLUMN_ID)
        index_b = -1
        if index_a == 0:
            index_b = len(model) - 1
        else:
            index_b = index_a - 1
        model[index_a], model[index_b] = model[index_b], model[index_a]
        model[index_a][cons.COLUMN_ID] = index_b
        model[index_b][cons.COLUMN_ID] = index_a
        self.parser.swap_task(index_a, index_b)


def main():
    app = TaskListGUI()
    Gtk.main()


if __name__ == '__main__':
    main()
