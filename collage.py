import gi
from gi.repository import Gtk, GdkPixbuf
from gi.repository import Pango

class ImageGridWidget(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Search bar
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search by title...")
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.pack_start(self.search_entry, False, False, 0)

        # Scrolled window
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(self.scrolled_window, True, True, 0)

        # Grid to hold images and titles
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(10)
        self.grid.set_column_spacing(10)
        self.scrolled_window.add(self.grid)

        # Internal data structure to keep track of items
        self.items = []  # Each item is a tuple (widget, title)

    def add_image(self, image_path, title):
        # Create image widget
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(image_path, 100, 100, preserve_aspect_ratio=True)
        image = Gtk.Image.new_from_pixbuf(pixbuf)

        # Create label
        label = Gtk.Label(label=title)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_max_width_chars(15)
        label.set_xalign(0.5)

        # Create a container for image and label
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        container.pack_start(image, False, False, 0)
        container.pack_start(label, False, False, 0)

        # Add event box for handling mouse events
        event_box = Gtk.EventBox()
        event_box.add(container)
        event_box.connect("enter-notify-event", self.on_mouse_hover, title)
        event_box.connect("button-press-event", self.on_mouse_click, title)

        # Add to grid
        self.items.append((event_box, title))
        self.update_grid()

    def update_grid(self):
        # Clear the grid
        for child in self.grid.get_children():
            self.grid.remove(child)

        # Add filtered items back to the grid
        for i, (widget, _) in enumerate(self.items):
            self.grid.attach(widget, i % 4, i // 4, 1, 1)  # 4 items per row

        self.grid.show_all()

    def on_search_changed(self, search_entry):
        search_text = search_entry.get_text().lower()

        # Filter items based on the search query
        for widget, title in self.items:
            if search_text in title.lower():
                widget.show()
            else:
                widget.hide()

    def on_mouse_hover(self, widget, event, title):
        print(f"Hovered over: {title}")

    def on_mouse_click(self, widget, event, title):
        print(f"Clicked on: {title}")

# Example usage
if __name__ == "__main__":
    import os
    import sys

    # Create a GTK application
    app = Gtk.Application()

    def on_activate(app):
        # Create a window
        window = Gtk.ApplicationWindow(application=app)
        window.set_default_size(600, 400)
        window.set_title("Image Grid")

        # Create and populate the ImageGridWidget
        image_grid = ImageGridWidget()

        # Example images (replace with your own paths)
        images = [
            ("/home/mahmooz/dl/garden-rose-red-pink-56866.jpeg", "Title 1"),
            ("/home/mahmooz/dl/premium_photo-1676478746990-4ef5c8ef234a.jpg", "Title 2"),
            # ("/path/to/image3.jpg", "Title 3"),
            # ("/path/to/image4.jpg", "Title 4"),
        ]

        for image_path, title in images:
            if os.path.exists(image_path):
                image_grid.add_image(image_path, title)
            else:
                print(f"Image not found: {image_path}", file=sys.stderr)

        window.add(image_grid)
        window.show_all()

    app.connect("activate", on_activate)
    app.run([])
