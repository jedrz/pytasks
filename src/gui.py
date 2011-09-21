#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import datetime

from gi.repository import Gtk, Gdk

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
    """Date chooser."""

    def __init__(self, date=datetime.date.today()):
        builder = Gtk.Builder()
        builder.add_from_file(cons.DIALOG_CALENDAR_SCHEMA)
        self.widgets = GtkBuilderProxy(builder)
        self.date = date

    def run(self):
        """Get chosen date and return status and datetime.date object."""
        # range of month in gtk calendar is 0..11
        self.widgets.calendar.select_month(self.date.month - 1,
                                           self.date.year)
        self.widgets.calendar.select_day(self.date.day)
        result = self.widgets.dialog.run()
        year, month, date = self.widgets.calendar.get_date()
        date_obj = datetime.date(year, month + 1, date)
        self.widgets.dialog.destroy()
        return result, date_obj


class DialogAdd:
    """A dialog which handle adding a task."""

    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file(cons.DIALOG_ADD_SCHEMA)
        builder.connect_signals(self)
        self.widgets = GtkBuilderProxy(builder)
        self.task = {'date': None, 'done': False}

    def run(self):
        """Return status and a task dictionary with user's description."""
        result = self.widgets.dialog.run()
        self.task['text'] = self.widgets.entry_text.get_text()
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
        """Show dialog with calendar and set date key of the task dict,
        when the icon in the entry is clicked.
        
        Also update some widgets' attributes.
        """
        if position == Gtk.EntryIconPosition.PRIMARY:
            # calendar icon clicked
            # define default date to show
            _date = self.task['date'] if self.task['date'] else \
                    datetime.date.today()
            dialog_calendar = DialogCalendar(_date)
            result_calendar, date = dialog_calendar.run()
            if result_calendar == Gtk.ResponseType.OK:
                self.task['date'] = date
                self.widgets.entry_date.set_text(date.strftime(cons.DATE_FORMAT))
                # set combobox sensitive
                self.widgets.combobox_interval.set_sensitive(True)
        else:
            # clear icon clicked
            self.task['date'] = None
            self.widgets.entry_date.set_text('')
            # set combobox not sensitive
            self.widgets.combobox_interval.set_active(
                    cons.COMBOBOX_INTERVAL_NONE)
            self.widgets.combobox_interval.set_sensitive(False)


class DialogDelete:
    """A simple dialog with two buttons handling deleting a task."""

    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file(cons.DIALOG_DELETE_SCHEMA)
        self.widgets = GtkBuilderProxy(builder)

    def run(self):
        result = self.widgets.dialog.run()
        self.widgets.dialog.destroy()
        return result


class DialogEdit(DialogAdd):
    """The same as DialogAdd but fills widgets."""
    
    def __init__(self, task):
        super(DialogEdit, self).__init__()
        self.task = task
        self.set_values()

    def set_values(self):
        """Fill proper widgets with task's values."""
        self.widgets.entry_text.set_text(self.task['text'])
        if self.task['date']:
            self.widgets.entry_date.set_text(self.task['date'].strftime(
                cons.DATE_FORMAT))
            # set combobox sensitive
            self.widgets.combobox_interval.set_sensitive(True)
        interval = self.task['interval']
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
    """Main class of the program."""

    def __init__(self):
        builder = Gtk.Builder()
        builder.add_from_file(cons.WINDOW_SCHEMA)
        builder.connect_signals(self)

        self.widgets = GtkBuilderProxy(builder)
        self.widgets.window.show_all()

        self.parser = parser.TaskParser(cons.DATA_FILE)

        # make done tasks strikethrough
        self.set_column_func()
        # add tasks to the liststore object
        self.liststore_update()

    def set_column_func(self):
        """Add a function to treeview columns controlling strikethrough
        property depending on status 'done' of the task.
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

    def liststore_update(self):
        """Clear and add tasks to the liststore object."""
        # count of tasks
        self._index = 0
        self.widgets.liststore.clear()
        tasks = self.parser.get_tasks()
        for task in tasks:
            self.liststore_add_task(task)

    def _get_date(self, date):
        if date:
            return date.strftime(cons.DATE_FORMAT)
        return ''

    def _get_interval(self, interval):
        # FIXME: needs translating
        if interval == cons.MONTH:
            return 'miesiąc'
        elif interval == cons.YEAR:
            return 'rok'
        elif isinstance(interval, cons.DAYS):
            return '{} dni'.format(interval)
        return ''

    def liststore_add_task(self, task):
        self.widgets.liststore.append([
            self._index,
            task['done'],
            self._get_date(task['date']),
            self._get_interval(task['interval']),
            task['text']
        ])
        self._index += 1

    def liststore_edit_task(self, it, task):
        self.widgets.liststore.set_value(it,
                cons.COLUMN_DATE, self._get_date(task['date']))
        self.widgets.liststore.set_value(it,
                cons.COLUMN_INTERVAL, self._get_interval(task['interval']))
        self.widgets.liststore.set_value(it, cons.COLUMN_TEXT, task['text'])

    def add_task(self):
        """Add a task to the liststore object and save to the file.
        
        The method is using a dialog to get some values.
        """
        dialog_add = DialogAdd()
        result, task = dialog_add.run()
        if result != Gtk.ResponseType.OK:
            return
        self.liststore_add_task(task)
        self.parser.add_task(**task)

    def edit_task(self):
        """Edit a selected task, similar to add_task."""
        model, it = self.widgets.treeview_selection.get_selected()
        if not it:
            return
        index = model.get_value(it, cons.COLUMN_ID)
        tasks = self.parser.get_tasks()
        dialog_edit = DialogEdit(tasks[index])
        result, task = dialog_edit.run()
        if result != Gtk.ResponseType.OK:
            return
        self.liststore_edit_task(it, task)
        self.parser.edit_task(index, **task)

    def delete_task(self):
        """Delete a selected task confirmed by user using dialog."""
        model, it = self.widgets.treeview_selection.get_selected()
        if not it:
            return
        dialog_delete = DialogDelete()
        result = dialog_delete.run()
        if result != Gtk.ResponseType.OK:
            return
        index = model.get_value(it, cons.COLUMN_ID)
        self.parser.delete_task(index)
        self.liststore_update()

    def toggle_task(self):
        """Make a task done or not done."""
        model, it = self.widgets.treeview_selection.get_selected()
        if not it:
            return
        index = model.get_value(it, cons.COLUMN_ID)
        value = model.get_value(it, cons.COLUMN_DONE)
        model.set_value(it, cons.COLUMN_DONE, not value)
        self.parser.edit_task(index, done=not value)

    def _menu_set_sensitive(self, sensitive):
        """Set sensitive menuitems."""
        prefix = 'context_menuitem_'
        names = ('edit', 'delete', 'done')
        for name in names:
            menuitem = getattr(self.widgets, prefix + name)
            menuitem.set_sensitive(sensitive)

    def menu_show_all(self, button, timestamp):
        self._menu_set_sensitive(True)
        self.widgets.context_menu.popup(None, None, None, None, button,
                                        timestamp)

    def menu_show_add(self, button, timestamp):
        self._menu_set_sensitive(False)
        self.widgets.context_menu.popup(None, None, None, None, button,
                                        timestamp)

    def on_window_destroy(self, window):
        Gtk.main_quit()

    def on_toolbutton_add_clicked(self, button):
        self.add_task()

    def on_toolbutton_edit_clicked(self, button):
        self.edit_task()

    def on_toolbutton_delete_clicked(self, button):
        self.delete_task()

    def on_toolbutton_done_clicked(self, button):
        self.toggle_task()

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
        # FIXME doesn't work
        return
        model, it = self.widgets.treeview_selection.get_selected()
        if not it:
            return
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

    def on_context_menuitem_add_activate(self, menuitem):
        self.add_task()

    def on_context_menuitem_edit_activate(self, menuitem):
        self.edit_task()

    def on_context_menuitem_delete_activate(self, menuitem):
        self.delete_task()

    def on_context_menuitem_done_activate(self, menuitem):
        self.toggle_task()

    def on_treeview_event(self, treeview, event):
        # button-press-event not working?
        if event.type == Gdk.EventType.BUTTON_PRESS:
            # right button clicked
            if event.button.button == 3:
                pthinfo = treeview.get_path_at_pos(event.x, event.y)
                # clicked on a row?
                if pthinfo:
                    self.menu_show_all(event.button.button, event.time)
                else:
                    self.menu_show_add(event.button.button, event.time)


def main():
    app = TaskListGUI()
    Gtk.main()


if __name__ == '__main__':
    main()
