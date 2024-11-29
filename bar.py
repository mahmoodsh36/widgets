import subprocess
import re

from gi.repository import Gtk, Gdk, GtkLayerShell, GLib

import hyprland

class SystemBar(Gtk.Window):
    def __init__(self):
        super().__init__()
        screen = Gdk.Screen.get_default()
        width = screen.get_width()  # Get the screen width
        self.set_default_size(width, 40)  # Full screen width, fixed height for the bar
        self.set_title("System Bar")

        # Initialize GTK Layer Shell
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.auto_exclusive_zone_enable(self)  # Correct method for auto exclusive zone
        # GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 0)
        # GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, 0)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)

        # Create a box to contain all widgets (using HORIZONTAL layout)
        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        # Set properties for the box to make sure widgets are distributed properly
        self.box.set_homogeneous(False)
        self.add(self.box)

        # Create a container for workspace buttons (left aligned)
        self.workspace_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.box.pack_start(self.workspace_box, False, False, 0)

        # Create a label for the current window title (centered)
        self.current_window_label = Gtk.Label(label="Window Title")
        self.box.pack_start(self.current_window_label, True, True, 0)

        # Create a label for the date (right aligned)
        self.date_label = Gtk.Label(label="Date")
        self.box.pack_end(self.date_label, False, False, 0)

        # Create buttons for workspaces
        self.workspace_buttons = []
        self.update_workspace_buttons()

        # Update current workspace and date
        GLib.timeout_add_seconds(1, self.update_date)
        GLib.timeout_add_seconds(1, self.update_current_workspace)

        def handler(event_line):
            if event_line.startswith('workspace>>'):
                # dont modify window from thread, use idle_add, otherwise we'll crash
                GLib.idle_add(
                    lambda: (self.update_workspace_buttons(), self.show_all()))
        hyprland.add_listener(handler)

    def update_workspace_buttons(self):
        """Fetch the current workspace information and create buttons for each workspace"""
        result = subprocess.run(["hyprctl", "workspaces"], capture_output=True, text=True)
        workspaces = self.parse_workspaces(result.stdout)
        print(workspaces)

        # Remove old buttons
        for button in self.workspace_buttons:
            self.workspace_box.remove(button)

        self.workspace_buttons.clear()

        # Add new buttons for each workspace
        for workspace in workspaces:
            button = Gtk.Button(label=str(workspace['id']))
            button.connect("clicked", self.on_workspace_button_clicked, workspace['id'])
            self.workspace_buttons.append(button)
            self.workspace_box.pack_start(button, False, False, 0)

    def parse_workspaces(self, output):
        """Parse workspace information from the hyprctl output"""
        workspaces = []
        for line in output.splitlines():
            match = re.match(r'workspace ID (\d+)', line)
            if match:
                workspaces.append({'id': int(match.group(1))})
        workspaces.sort(key=lambda x: x['id'])
        return workspaces

    def on_workspace_button_clicked(self, button, workspace_id):
        """Handle workspace button clicks and switch workspace"""
        print(f"Switching to workspace {workspace_id}")  # Debug print to verify
        subprocess.run(["hyprctl", 'dispatch', "workspace", str(workspace_id)])

    def update_current_workspace(self):
        """Update the current workspace label"""
        current_workspace = self.get_current_workspace_from_hyprland()
        if current_workspace:
            self.current_window_label.set_text(f"Workspace: {current_workspace}")
        GLib.timeout_add_seconds(1, self.update_current_workspace)

    def get_current_workspace_from_hyprland(self):
        """Get the current workspace using Hyprland IPC."""
        result = subprocess.run(["hyprctl", "activeworkspace"], capture_output=True, text=True)
        match = re.search(r'workspace ID (\d+)', result.stdout)
        if match:
            return int(match.group(1))
        else:
            print("Could not extract workspace ID from the output")
            return None

    def update_date(self):
        """Update the date label"""
        from datetime import datetime
        now = datetime.now()
        self.date_label.set_text(now.strftime("%Y-%m-%d %H:%M:%S"))
        return True  # Keep updating every second

if __name__ == "__main__":
    window = SystemBar()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()