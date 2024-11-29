import sys
import select
from gi.repository import Gtk, Gdk, GLib

class DMenuPopup(Gtk.Window):
    def __init__(self, items=None):
        super().__init__()
        self.set_title("Dmenu-like Popup")
        self.set_default_size(400, 300)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Set the window to be a floating popup
        self.set_decorated(False)  # Remove window decorations (like title bar)
        self.set_keep_above(True)  # Keep the window above other windows
        self.set_type_hint(Gdk.WindowTypeHint.POPUP_MENU)  # Hint for floating window
        self.set_transient_for(None)  # Not tied to any specific window

        # Set up entry box to type search query
        self.entry = Gtk.Entry()
        self.entry.connect("changed", self.on_entry_changed)
        self.entry.set_placeholder_text("Search...")

        # Set up a list box to show search results
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.set_activate_on_single_click(True)
        self.listbox.connect("row-activated", self.on_item_selected)

        # Add key press event to handle enter key
        self.connect("key-press-event", self.on_key_press)

        # Populate with items passed via stdin or fallback to default list
        if items:
            self.items = items
        else:
            self.items = ["Option 1", "Option 2", "Option 3", "Option 4"]

        self.update_items(self.items)

        # Main layout
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(self.entry, False, False, 0)
        box.pack_start(self.listbox, True, True, 0)
        self.add(box)

    def update_items(self, items):
        """Update the listbox with filtered items."""
        self.listbox.foreach(lambda widget: self.listbox.remove(widget))  # Clear previous items
        for item in items:
            label = Gtk.Label(label=item)
            row = Gtk.ListBoxRow()
            row.add(label)
            self.listbox.add(row)
        self.listbox.show_all()

    def on_entry_changed(self, entry):
        """Filter the list of items based on the entered text."""
        search_text = entry.get_text().lower()
        filtered_items = [item for item in self.items if search_text in item.lower()]
        self.update_items(filtered_items)

    def on_item_selected(self, listbox, row):
        """Handle the item selection."""
        label = row.get_child()
        print(f"Selected: {label.get_text()}")  # Handle the selection action
        self.destroy()  # Close the popup after selection

    def on_key_press(self, widget, event):
        """Handle key press events."""
        if event.keyval == Gdk.KEY_Return:  # Enter key pressed
            selected_row = self.listbox.get_selected_row()
            if selected_row:
                label = selected_row.get_child()
                print(f"Selected: {label.get_text()}")  # Handle the selection action
            else:
                # If no row is selected, return the first item by default
                print(f"Selected: {self.items[0]}")
            self.destroy()  # Close the popup after selection


def read_stdin():
    """Read items from stdin, one per line. Returns empty list if no input is available."""
    items = []
    # Use select to check if there's data available in stdin
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        for line in sys.stdin:
            items.append(line.strip())  # Add item to the list (strip to remove newline)
    return items


if __name__ == "__main__":
    items = read_stdin()  # Get items from stdin (if provided)
    if not items:  # If stdin is empty, use a default list
        items = ["Option 1", "Option 2", "Option 3", "Option 4"]
    win = DMenuPopup(items)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()