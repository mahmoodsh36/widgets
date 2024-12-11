#!/usr/bin/env python

import sys
import select
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio
from pathlib import Path

class DMenuPopup(Gtk.Window):
    def __init__(self, items=None):
        super().__init__()
        self.set_title("popup")
        self.set_default_size(400, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_decorated(False)
        self.set_type_hint(Gdk.WindowTypeHint.POPUP_MENU)

        self.entry = Gtk.Entry()
        self.entry.connect("changed", self.on_entry_changed)
        self.entry.set_placeholder_text("Search...")

        # use treeview instead of listbox
        self.liststore = Gtk.ListStore(str)
        self.treeview = Gtk.TreeView(model=self.liststore)

        self.treeview.set_headers_visible(False)
        self.treeview.connect("row-activated", self.on_item_selected)

        # add a single text column
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Item", renderer, text=0)
        self.treeview.append_column(column)

        self.scrollable = Gtk.ScrolledWindow()
        self.scrollable.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrollable.add(self.treeview)

        self.items = items if items else ["Option 1", "Option 2", "Option 3", "Option 4"]
        self.filtered_items = self.items[:]
        self.update_items(self.filtered_items)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(self.entry, False, False, 0)
        box.pack_start(self.scrollable, True, True, 0)
        self.add(box)

        self.connect("key-press-event", self.on_key_press)

    def update_items(self, items):
        """update the treeview with the filtered items."""
        self.liststore.clear()
        for item in items:
            self.liststore.append([item])

    def on_entry_changed(self, entry):
        """filter items based on the search text."""
        search_text = entry.get_text().lower()
        if search_text:
            self.filtered_items = [item for item in self.items if search_text in item.lower()]
        else:
            self.filtered_items = self.items[:]
        self.update_items(self.filtered_items)

    def on_item_selected(self, treeview, path, column):
        """handle the item selection."""
        model = treeview.get_model()
        item = model[path][0]
        print(item)
        self.destroy()

    def on_key_press(self, widget, event):
        """handle key press events."""
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
        if event.keyval == Gdk.KEY_Return:
            selection = self.treeview.get_selection()
            model, treeiter = selection.get_selected()
            if treeiter:
                print(model[treeiter][0])
            elif self.filtered_items:
                print(self.filtered_items[0])
            else:
                print("")
            self.destroy()

def read_stdin():
    """read items from stdin, one per line. returns an empty list if no input is available."""
    items = []
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        for line in sys.stdin:
            items.append(line.strip())
    return items

if __name__ == "__main__":
    items = read_stdin()
    if not items:
        items = ["Option 1", "Option 2", "Option 3", "Option 4"]

    # load main.css
    p = Path(__file__).with_name('main.css')
    css_filename = str(p.absolute())

    css_provider = Gtk.CssProvider()
    css_provider.load_from_file(Gio.File.new_for_path(css_filename))
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
    )

    win = DMenuPopup(items)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()

    Gtk.main()