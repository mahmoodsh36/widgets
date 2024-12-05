#!/usr/bin/env python

import sys
import select
import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject, Gio
import difflib

class Item(GObject.GObject):
    text = GObject.Property(type=str)
    def __init__(self):
        GObject.GObject.__init__(self)

class DMenuPopup(Gtk.Window):
    def __init__(self, items=None):
        super().__init__()
        self.parent = Gtk.Window()
        self.set_title("popup")
        self.set_default_size(400, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_decorated(False)
        # self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.POPUP_MENU)
        self.set_transient_for(self.parent)

        self.entry = Gtk.Entry()
        self.entry.connect("changed", self.on_entry_changed)
        self.entry.set_placeholder_text("Search...")

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.set_activate_on_single_click(True)
        self.listbox.connect("row-activated", self.on_item_selected)

        self.scrollable = Gtk.ScrolledWindow()
        self.scrollable.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrollable.add(self.listbox)

        self.connect("key-press-event", self.on_key_press)

        if items:
            self.items = items
        else:
            self.items = ["Option 1", "Option 2", "Option 3", "Option 4"]

        self.liststore = Gio.ListStore()
        item1 = Item()
        item2 = Item()
        item1.text = "hello"
        item2.text = "hey"
        self.liststore.append(item1)
        self.liststore.append(item2)
        # self.listbox.bind_model(self.liststore)
        self.listbox.bind_model(self.liststore, self.create_widget_func)

        self.filtered_items = self.items
        self.update_items(self.filtered_items)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(self.entry, False, False, 0)
        box.pack_start(self.scrollable, True, True, 0)
        self.add(box)

        # Debouncing timer
        self.last_change_time = 0
        self.debounce_timeout = 0  # Time in seconds (300 ms)

    def create_widget_func(self, item):
        label = Gtk.Label(label=item.text)
        label.set_markup(self.highlight_matches(item.text))
        return label

    def update_items(self, items):
        """update the listbox with filtered items."""
        # children = self.listbox.get_children()

        self.liststore.remove_all()

        mylist = []
        for i in range(len(items)):
            x = Item()
            x.text = items[i]
            mylist.append(x)
        self.liststore.splice(0, 0, mylist)

        # self.listbox.show_all()

    def highlight_matches(self, item):
        """highlight the matching substring in the item using Pango markup."""
        search_text = self.entry.get_text().lower()
        if search_text:
            start_idx = item.lower().find(search_text)
            if start_idx != -1:
                # Highlight the matched part of the string
                before_match = item[:start_idx]
                match = item[start_idx:start_idx + len(search_text)]
                after_match = item[start_idx + len(search_text):]

                # Return Pango markup for highlighting
                return f'<span foreground="yellow">{before_match}</span>' \
                       f'<span foreground="blue">{match}</span>' \
                       f'<span foreground="yellow">{after_match}</span>'
        return item  # Return item without highlighting if no match

    def on_entry_changed(self, entry):
        """trigger filtering with debounce."""
        current_time = time.time()
        if current_time - self.last_change_time > self.debounce_timeout:
            self.last_change_time = current_time
            search_text = entry.get_text().lower()
            if search_text:
                self.filtered_items = self.get_fuzzy_matches(search_text)
                GLib.idle_add(
                    lambda: self.update_items(self.filtered_items))
                # self.update_items(self.filtered_items)
            else:
                self.filtered_items = self.items
                GLib.idle_add(
                    lambda: self.update_items(self.filtered_items))

    def get_fuzzy_matches(self, search_text):
        """return the closest matches using difflib."""
        # matches = difflib.get_close_matches(search_text, self.items, n=10, cutoff=0.1)
        # return matches
        parts = search_text.split(' ')
        matches = []
        for item in self.items:
            match = True
            for part in parts:
                if not part in item:
                    match = False
            if match:
                matches.append(item)
        return matches

    def on_item_selected(self, listbox, row):
        """handle the item selection."""
        label = row.get_child()
        print(label.get_text())  # Handle the selection action
        self.destroy()

    def on_key_press(self, widget, event):
        """handle key press events."""
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
        if event.keyval == Gdk.KEY_Return:
            selected_row = self.listbox.get_selected_row()
            if selected_row:
                label = selected_row.get_child()
                print(label.get_text())
            elif self.filtered_items:
                print(self.filtered_items[0])
            else:
                print("")
            self.destroy()

def read_stdin():
    """read items from stdin, one per line. returns empty list if no input is available."""
    items = []
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        for line in sys.stdin:
            items.append(line.strip())
    return items

if __name__ == "__main__":
    items = read_stdin()
    if not items:
        items = ["Option 1", "Option 2", "Option 3", "Option 4"]

    win = DMenuPopup(items)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()

    # Load the CSS styling using inline CSS
    style_provider = Gtk.CssProvider()
    style_provider.load_from_data(b"""
        /* Window Style */
        window {
            background-color: #2e2e2e;
            border-radius: 10px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.6);
        }

        /* Style the listbox (the container) */
        list {
            background-color: #1f1f1f;
            border-radius: 5px;
            padding: 10px;
            margin-top: 10px;
        }

        /* Style the individual rows in the listbox */
        row {
            background-color: #333;
            color: #fff;
            padding: 12px 15px;
            border-bottom: 1px solid #444;
            transition: background-color 0.3s ease;
        }

        /* On hover, change the background color of the row */
        row:hover {
            background-color: #0066cc;
        }

        /* Style for activatable rows (when selected or clickable) */
        row.activatable:selected {
            background-color: #00cc77;
        }

        /* Remove the bottom border from the last row */
        row:last-child {
            border-bottom: none;
        }

        /* Style the entry field */
        entry {
            background-color: #111;
            color: #fff;
            border: none;
            padding: 10px;
            border-radius: 5px;
        }

        /* Focus state for the entry field */
        entry:focus {
            border: 2px solid #0077cc;
        }

        /* Label styling inside listbox rows */
        row label {
            font-family: 'Arial', sans-serif;
            font-size: 16px;
        }
    """)

    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
    )

    Gtk.main()