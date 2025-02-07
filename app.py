"""UI for 3D Print Dose Customization.

TODO:
- Make selection box respect canvas panning
- Parameterize height,width
- Maybe use component selection for this?
- Add absolute vs. scale option for exposure scaling

"""

from __future__ import annotations

import logging
import tkinter as tk
from typing import TYPE_CHECKING

from menus.arrange_menu import align_bottom, align_left, align_right, align_top, set_x, set_y
from menus.file_menu import load_json, save_json
from menus.group_menu import change_group, delete_group, new_group, rename_group, set_group_color
from menus.object_menu import add_component, delete_component, tile

if TYPE_CHECKING:
    from component import Component

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CANVAS_X = 2560
CANVAS_Y = 1600


class App:
    """A class used to represent the Application with a Tkinter GUI.

    Attributes
    ----------
    root : tk.Tk
        The root window of the Tkinter application.
    button_bar : tk.Frame
        The frame containing the buttons.
    dimensions_label : tk.Label
        The label displaying the dimensions and coordinates of the selected component.
    canvas : tk.Canvas
        The canvas on which components are drawn.
    selection : list[Component]
        The list of selected components.
    groups : dict[str, list[Component]]
        The dictionary of groups and their components.
    colors : dict[str, str]
        The dictionary of groups and their colors.
    color_boxes : dict[str, tk.PhotoImage]
        The dictionary of color box images.
    selection_rect : int | None
        The ID of the selection component on the canvas.

    """

    def __init__(self, root: tk.Tk) -> None:
        """Initialize the App.

        Parameters
        ----------
        root : tk.Tk
            The root window of the Tkinter application.

        """
        self.root = root
        self.root.title("3D Print Dose Customization")
        self.comp_width = 100
        self.comp_height = 100
        self.selection = []
        self.groups = {}
        self.colors = {}
        self.color_boxes = {}
        self.selection_rect = None
        self.selection_start_x = None
        self.selection_start_y = None
        self.create_ui()

    def create_ui(self) -> None:
        """Create the base UI."""
        self.create_menu_bar()
        self.create_label()
        self.create_canvas()
        self.bind_shortcuts()

    def create_menu_bar(self) -> None:
        """Create the menu bar."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=lambda: load_json(self), accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=lambda: save_json(self), accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        self.group_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Group", menu=self.group_menu)

        self.group_var = tk.StringVar()
        self.update_group_dropdown()

        component_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Component", menu=component_menu)
        component_menu.add_command(label="Add", command=lambda: add_component(self), accelerator="Insert")
        component_menu.add_command(label="Delete", command=lambda: delete_component(self), accelerator="Delete")
        component_menu.add_separator()
        component_menu.add_command(label="Tile Create", command=lambda: tile(self))

        arrange_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Arrange", menu=arrange_menu)
        arrange_menu.add_command(label="Set X", command=lambda: set_x(self), accelerator="Ctrl+X")
        arrange_menu.add_command(label="Set Y", command=lambda: set_y(self), accelerator="Ctrl+Y")
        arrange_menu.add_separator()
        arrange_menu.add_command(label="Align Left", command=lambda: align_left(self), accelerator="Ctrl+L")
        arrange_menu.add_command(label="Align Right", command=lambda: align_right(self), accelerator="Ctrl+R")
        arrange_menu.add_command(label="Align Top", command=lambda: align_top(self), accelerator="Ctrl+T")
        arrange_menu.add_command(label="Align Bottom", command=lambda: align_bottom(self), accelerator="Ctrl+B")

    def update_group_dropdown(self) -> None:
        """Update the group dropdown menu."""
        self.group_menu.delete(0, "end")
        self.group_menu.add_command(label="New Group", command=lambda: new_group(self), accelerator="Ctrl+G")
        self.group_menu.add_command(label="Delete Group", command=lambda: delete_group(self))
        self.group_menu.add_separator()
        self.group_menu.add_command(label="- Groups -", state=tk.DISABLED)

        self.color_boxes.clear()
        for group in self.groups:
            color = self.colors[group]
            label = f"  {group}"
            color_box = self.create_color_box(color)
            self.color_boxes[group] = color_box
            self.group_menu.add_radiobutton(
                label=label,
                variable=self.group_var,
                value=group,
                indicatoron=1,
                compound=tk.LEFT,
                image=color_box,
            )

        self.group_menu.add_command(label="Rename Group", command=lambda: rename_group(self))
        self.group_menu.add_command(label="Change Group Color", command=lambda: set_group_color(self))
        self.group_menu.add_command(label="Change Selection to Current Group", command=lambda: change_group(self))
        if self.groups:
            self.group_var.set(list(self.groups.keys())[-1])

    def create_color_box(self, color: str) -> tk.PhotoImage:
        """Create a small colored box for the group label.

        Parameters
        ----------
        color : str
            The color of the box.

        Returns
        -------
        tk.PhotoImage
            The image of the colored box.

        """
        size = 10
        image = tk.PhotoImage(width=size, height=size)
        image.put(color, to=(0, 0, size, size))
        return image

    def bind_shortcuts(self) -> None:
        """Bind keyboard shortcuts."""
        self.root.bind_all("<Insert>", lambda _: add_component(self))
        self.root.bind_all("<Delete>", lambda _: delete_component(self))
        self.root.bind_all("<Control-g>", lambda _: new_group(self))
        self.root.bind_all("<Control-o>", lambda _: load_json(self))
        self.root.bind_all("<Control-s>", lambda _: save_json(self))
        self.root.bind_all("<Control-x>", lambda _: set_x(self))
        self.root.bind_all("<Control-y>", lambda _: set_y(self))
        self.root.bind_all("<Control-l>", lambda _: align_left(self))
        self.root.bind_all("<Control-r>", lambda _: align_right(self))
        self.root.bind_all("<Control-t>", lambda _: align_top(self))
        self.root.bind_all("<Control-b>", lambda _: align_bottom(self))

    def create_label(self) -> None:
        """Create the dimensions label."""
        self.dimensions_label = tk.Label(self.root, text="", bg="lightgray")
        self.dimensions_label.pack(side=tk.TOP, fill=tk.X)

    def update_label(self, comp: Component | None) -> None:
        """Update the label with the dimensions and coordinates of the component.

        Parameters
        ----------
        comp : Component | None
            The component whose information is to be displayed or None if no component is selected.

        """
        if comp is None:
            self.dimensions_label.config(text="")
            return
        text = f"X: {comp.x}, Y: {comp.y}, Width: {comp.width}, Height: {comp.height}, Group: {comp.group}"
        self.dimensions_label.config(text=text)

    def create_canvas(self) -> None:
        """Create the canvas with scrollbars."""
        # Set the main window to start maximized
        self.root.state("zoomed")

        # Create a main frame to hold the canvas and the vertical scrollbar
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a frame for the canvas and vertical scrollbar
        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create the canvas with a fixed size and scroll region
        self.canvas = tk.Canvas(self.canvas_frame, width=CANVAS_X, height=CANVAS_Y, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.NONE, expand=False)

        # Create scrollbars and attach them to the canvas
        self.v_scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.config(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        self.canvas.config(scrollregion=(0, 0, CANVAS_X, CANVAS_Y))

        # Bind events to the canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        # Prevent the canvas from resizing when the window is resized
        self.canvas_frame.pack_propagate(flag=False)
        self.canvas.pack_propagate(flag=False)

    def clear_canvas(self) -> None:
        """Clear all components from the canvas."""
        self.canvas.delete("all")

    def on_canvas_click(self, event: tk.Event) -> None:
        """Handle the click event on the canvas."""
        logger.debug("Click at (%d, %d)", event.x, event.y)
        self.selection_start_x = event.x
        self.selection_start_y = event.y
        if not self.canvas.find_withtag("current"):  # nothing was under cursor when clicked
            self.deselect_all()
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
                self.selection_rect = None
        else:
            self.selection_start_x = None
            self.selection_start_y = None

    def on_canvas_drag(self, event: tk.Event) -> None:
        """Handle the drag event on the canvas."""
        if self.selection_start_x is not None and self.selection_start_y is not None:
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
            self.selection_rect = self.canvas.create_rectangle(
                self.selection_start_x,
                self.selection_start_y,
                event.x,
                event.y,
                outline="blue",
                dash=(2, 2),
            )

    def on_canvas_release(self, event: tk.Event) -> None:
        """Handle the release event on the canvas."""
        logger.debug("Release at (%d, %d)", event.x, event.y)
        if self.selection_rect:
            x1, y1, x2, y2 = self.canvas.coords(self.selection_rect)
            self.select_components_in_area(x1, y1, x2, y2)
            self.canvas.delete(self.selection_rect)
            self.selection_rect = None

    def select_components_in_area(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Select all components within the specified area."""
        for group in self.groups.values():
            for comp in group:
                if (
                    comp.x >= min(x1, x2)
                    and comp.x + comp.width <= max(x1, x2)
                    and comp.y >= min(y1, y2)
                    and comp.y + comp.height <= max(y1, y2)
                ):
                    comp.select()
        if self.selection:
            self.update_label(self.selection[0])

    def deselect_all(self) -> None:
        """Deselect all components."""
        for comp in self.selection[:]:  # operate on a copy of the list since it will be modified
            comp.deselect()
        self.update_label(None)


def main() -> None:
    """Run the Tkinter application."""
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
