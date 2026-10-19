import math
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox


@dataclass
class CharacterToken:
  name: str
  color: str
  column: int
  row: int
  start_column: int
  start_row: int
  movement_limit: int | None = None
  has_moved: bool = False

  @property
  def distance_moved(self):
    return math.hypot(
        self.column - self.start_column,
        self.row - self.start_row,
    )


class CharacterProximityApp:
  CELL_SIZE = 22
  COLUMNS = 36
  ROWS = 24
  TOKEN_RADIUS = 10
  MAX_MOVEMENT = 35
  ZOOM_MIN = 0.3
  ZOOM_MAX = 1.5
  VIEW_MARGIN = MAX_MOVEMENT
  COLORS = ("#ffaaaa", "#b5ffa9", "#aaa1ff", "#fff49a", "#ffc891")
  BG = "#303b36"

  def __init__(self, root):
    self.root = root
    self.root.title("Character Movement & Proximity")
    self.root.geometry("900x680")
    self.root.minsize(720, 560)
    self.root.configure(bg="#292929")
    self.characters = [
        CharacterToken("A", self.COLORS[0], 10, 14, 10, 14),
        CharacterToken("B", self.COLORS[1], 16, 11, 16, 11),
        CharacterToken("C", self.COLORS[2], 24, 8, 24, 8),
        CharacterToken("D", self.COLORS[3], 21, 19, 21, 19),
        CharacterToken("E", self.COLORS[4], 28, 15, 28, 15),
    ]
    self.selected_character = self.characters[0]
    self.dragged_character = None
    self.preview_position = None
    self.next_character_number = 6
    self.zoom = 1.0
    self.character_var = tk.StringVar(value="")
    self.movement_var = tk.StringVar(value="")
    self.status_var = tk.StringVar(value="")
    self.zoom_var = tk.DoubleVar(value=self.zoom)
    self.setup_ui()

  def setup_ui(self):
    controls = tk.Frame(self.root, bg="#292929", padx=12, pady=10)
    controls.pack(fill=tk.X)
    tk.Label(
        controls,
        text="Move character:",
        fg="#eeeeee",
        bg="#292929",
        font=("Arial", 10, "bold"),
    ).pack(side=tk.LEFT, padx=(0, 6))
    self.character_menu = tk.OptionMenu(
        controls,
        self.character_var,
        "",
        command=self.select_character,
    )
    self.character_menu.config(
        bg="#555555",
        fg="#ffffff",
        activebackground="#666666",
        activeforeground="#ffffff",
        bd=0,
        highlightthickness=0,
        width=7,
    )
    self.character_menu["menu"].config(bg="#444444", fg="#ffffff")
    self.character_menu.pack(side=tk.LEFT, padx=(0, 14))
    tk.Label(
        controls,
        text="Move (feet, max 35):",
        fg="#dddddd",
        bg="#292929",
        font=("Arial", 9),
    ).pack(side=tk.LEFT, padx=(0, 5))
    tk.Entry(
        controls, textvariable=self.movement_var, width=5, justify=tk.CENTER
    ).pack(side=tk.LEFT, padx=(0, 6))
    tk.Button(
        controls, text="Set Range", command=self.set_movement_limit,
        cursor="hand2",
    ).pack(side=tk.LEFT, padx=(0, 12))
    tk.Button(
        controls, text="Add Character", command=self.add_character,
        cursor="hand2",
    ).pack(side=tk.LEFT, padx=(0, 6))
    tk.Button(
        controls, text="Next Turn", command=self.reset_turn,
        cursor="hand2",
    ).pack(side=tk.LEFT)
    self.confirm_button = tk.Button(
        controls,
        text="Confirm Move",
        command=self.confirm_move,
        state=tk.DISABLED,
        cursor="hand2",
    )
    self.confirm_button.pack(side=tk.LEFT, padx=(8, 0))

    zoom_controls = tk.Frame(self.root, bg="#292929", padx=12)
    zoom_controls.pack(fill=tk.X)
    tk.Label(
        zoom_controls,
        text="Zoom:",
        fg="#dddddd",
        bg="#292929",
        font=("Arial", 9),
    ).pack(side=tk.LEFT, padx=(0, 6))
    tk.Button(
        zoom_controls,
        text="−",
        width=2,
        command=lambda: self.adjust_zoom(-0.1),
        cursor="hand2",
    ).pack(side=tk.LEFT)
    self.zoom_slider = tk.Scale(
        zoom_controls,
        variable=self.zoom_var,
        from_=self.ZOOM_MIN,
        to=self.ZOOM_MAX,
        resolution=0.1,
        orient=tk.HORIZONTAL,
        showvalue=False,
        length=180,
        command=self.set_zoom,
        bg="#292929",
        fg="#dddddd",
        highlightthickness=0,
        troughcolor="#555555",
        activebackground="#cccccc",
    )
    self.zoom_slider.pack(side=tk.LEFT, padx=4)
    tk.Button(
        zoom_controls,
        text="+",
        width=2,
        command=lambda: self.adjust_zoom(0.1),
        cursor="hand2",
    ).pack(side=tk.LEFT)
    self.zoom_label = tk.Label(
        zoom_controls,
        text="100%",
        fg="#dddddd",
        bg="#292929",
        font=("Arial", 9),
    )
    self.zoom_label.pack(side=tk.LEFT, padx=8)

    canvas_frame = tk.Frame(self.root, bg="#292929")
    canvas_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(2, 6))
    self.canvas = tk.Canvas(
        canvas_frame,
        bg=self.BG,
        highlightthickness=0,
        xscrollincrement=1,
        yscrollincrement=1,
    )
    horizontal_scrollbar = tk.Scrollbar(
        canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview
    )
    vertical_scrollbar = tk.Scrollbar(
        canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview
    )
    self.canvas.configure(
        xscrollcommand=horizontal_scrollbar.set,
        yscrollcommand=vertical_scrollbar.set,
    )
    self.canvas.grid(row=0, column=0, sticky="nsew")
    vertical_scrollbar.grid(row=0, column=1, sticky="ns")
    horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
    canvas_frame.grid_rowconfigure(0, weight=1)
    canvas_frame.grid_columnconfigure(0, weight=1)
    self.canvas.bind("<Button-1>", self.on_press)
    self.canvas.bind("<B1-Motion>", self.on_drag)
    self.canvas.bind("<ButtonRelease-1>", self.on_release)
    tk.Label(
        self.root,
        textvariable=self.status_var,
        fg="#dddddd",
        bg="#292929",
        anchor="w",
        padx=14,
        pady=6,
        font=("Arial", 9),
    ).pack(fill=tk.X)
    self.redraw()

  def redraw(self):
    self.canvas.delete("all")
    cell_size = self.cell_size
    self.canvas.configure(
        scrollregion=(
            0,
            0,
            (self.COLUMNS + 2 * self.VIEW_MARGIN) * cell_size,
            (self.ROWS + 2 * self.VIEW_MARGIN) * cell_size,
        )
    )
    self.draw_map_grid()
    if (
        not self.selected_character.has_moved
        and self.selected_character.movement_limit is not None
    ):
      self.draw_movement_circle(self.selected_character)
    if self.preview_position is not None:
      self.draw_move_preview()
    for character in self.characters:
      self.draw_character(character)

    self.refresh_character_menu()
    self.confirm_button.config(
        state=tk.NORMAL if self.preview_position is not None else tk.DISABLED
    )
    limit = self.selected_character.movement_limit
    if self.selected_character.has_moved:
      self.movement_var.set("")
      if all(character.has_moved for character in self.characters):
        self.status_var.set("All characters have finished moving. Reset Turn to start again.")
      else:
        self.status_var.set(
            f"{self.selected_character.name} has already moved this turn."
        )
    elif limit is None:
      self.movement_var.set("")
      self.status_var.set(
          f"{self.selected_character.name}: enter up to 35 feet to show "
          "a movement circle, then drag the token within it."
      )
    else:
      moved = self.selected_character.distance_moved
      self.movement_var.set(str(limit))
      if self.preview_position is not None:
        preview_column, preview_row = self.preview_position
        preview_distance = math.hypot(
            preview_column - self.selected_character.start_column,
            preview_row - self.selected_character.start_row,
        )
        self.status_var.set(
            f"{self.selected_character.name}: preview destination "
            f"({preview_column + 1}, {preview_row + 1}) — "
            f"{preview_distance:g} / {limit} ft. "
            "Select Confirm Move to place the token."
        )
        return
      self.status_var.set(
          f"{self.selected_character.name}: {moved:g} / {limit} ft moved "
          f"({self.MAX_MOVEMENT} ft maximum). "
          "Movement is measured from the turn-start square."
      )

  def draw_map_grid(self):
    cell_size = self.cell_size
    padding = self.VIEW_MARGIN * cell_size
    for column in range(self.COLUMNS):
      for row in range(self.ROWS):
        x = padding + column * cell_size
        y = padding + row * cell_size
        fill = "#3a4740" if (column + row) % 2 == 0 else "#37433d"
        self.canvas.create_rectangle(
            x, y, x + cell_size, y + cell_size,
            fill=fill, outline="#4b5850",
        )
    self.canvas.create_text(
        padding + 8,
        padding + self.ROWS * cell_size - 8,
        text="1 grid square = 1 foot",
        anchor="sw",
        fill="#c4cec7",
        font=("Arial", 9),
    )

  def draw_movement_circle(self, character):
    x, y = self.grid_to_canvas(
        character.start_column, character.start_row
    )
    radius = character.movement_limit * self.cell_size
    self.canvas.create_oval(
        x - radius, y - radius, x + radius, y + radius,
        fill=character.color,
        stipple="gray25",
        outline=character.color,
        width=2,
    )

  def draw_character(self, character):
    x, y = self.grid_to_canvas(character.column, character.row)
    radius = self.token_radius
    selected = character is self.selected_character
    self.canvas.create_oval(
        x - radius,
        y - radius,
        x + radius,
        y + radius,
        fill=character.color,
        outline="#ffffff" if selected else "#343434",
        width=3 if selected else 2,
    )
    self.canvas.create_text(
        x, y, text=character.name, fill="#222222",
        font=("Arial", 9, "bold"),
    )

  def draw_move_preview(self):
    column, row = self.preview_position
    target_x, target_y = self.grid_to_canvas(column, row)
    radius = self.token_radius
    current_x, current_y = self.grid_to_canvas(
        self.selected_character.column, self.selected_character.row
    )
    self.canvas.create_line(
        current_x,
        current_y,
        target_x,
        target_y,
        fill="#ffffff",
        dash=(5, 3),
        width=2,
    )
    self.canvas.create_oval(
        target_x - radius,
        target_y - radius,
        target_x + radius,
        target_y + radius,
        fill=self.selected_character.color,
        stipple="gray50",
        outline="#ffffff",
        dash=(3, 2),
        width=2,
    )
    self.canvas.create_text(
        target_x,
        target_y,
        text=self.selected_character.name,
        fill="#222222",
        font=("Arial", 9, "bold"),
    )

  def grid_to_canvas(self, column, row):
    padding = self.VIEW_MARGIN * self.cell_size
    return (
        padding + (column + 0.5) * self.cell_size,
        padding + (row + 0.5) * self.cell_size,
    )

  def canvas_to_grid(self, x, y):
    padding = self.VIEW_MARGIN * self.cell_size
    column = round((x - padding) / self.cell_size - 0.5)
    row = round((y - padding) / self.cell_size - 0.5)
    return (
        min(max(column, 0), self.COLUMNS - 1),
        min(max(row, 0), self.ROWS - 1),
    )

  def position_is_occupied(self, character, column, row):
    x, y = self.grid_to_canvas(column, row)
    candidate_radius = self.token_radius
    for other in self.characters:
      if other is character:
        continue
      other_x, other_y = self.grid_to_canvas(other.column, other.row)
      minimum_distance = candidate_radius + self.token_radius
      if math.hypot(x - other_x, y - other_y) < minimum_distance:
        return True
    return False

  def on_press(self, event):
    pointer_x = self.canvas.canvasx(event.x)
    pointer_y = self.canvas.canvasy(event.y)
    column, row = self.canvas_to_grid(pointer_x, pointer_y)
    candidate = min(
        self.characters,
        key=lambda character: math.hypot(
            self.grid_to_canvas(character.column, character.row)[0]
            - pointer_x,
            self.grid_to_canvas(character.column, character.row)[1]
            - pointer_y,
        ),
    )
    center_x, center_y = self.grid_to_canvas(
        candidate.column, candidate.row
    )
    if math.hypot(center_x - pointer_x, center_y - pointer_y) > self.token_radius:
      self.dragged_character = None
      return
    if candidate.has_moved:
      self.status_var.set(f"{candidate.name} has already moved this turn.")
      return
    if candidate is not self.selected_character:
      self.preview_position = None
    self.selected_character = candidate
    self.dragged_character = candidate
    self.redraw()

  def on_drag(self, event):
    character = self.dragged_character
    if (
        character is None
        or character.has_moved
        or character.movement_limit is None
    ):
      return
    column, row = self.canvas_to_grid(
        self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
    )
    distance = math.hypot(
        column - character.start_column,
        row - character.start_row,
    )
    if distance <= character.movement_limit:
      if self.position_is_occupied(character, column, row):
        self.preview_position = None
        self.redraw()
        self.status_var.set("That square is occupied. Choose an empty square.")
        return
      self.preview_position = (column, row)
      self.redraw()

  def on_release(self, _event):
    self.dragged_character = None

  def refresh_character_menu(self):
    available = [
        character.name
        for character in self.characters
        if not character.has_moved
    ]
    menu = self.character_menu["menu"]
    menu.delete(0, tk.END)
    if available:
      for name in available:
        menu.add_command(
            label=name,
            command=lambda selected=name: self.select_character(selected),
        )
      self.character_var.set(self.selected_character.name)
    else:
      menu.add_command(label="No characters available", state=tk.DISABLED)
      self.character_var.set("None")

  def select_character(self, name):
    character = next(
        (item for item in self.characters if item.name == name),
        None,
    )
    if character is None or character.has_moved:
      self.refresh_character_menu()
      return
    if character is not self.selected_character:
      self.preview_position = None
      self.dragged_character = None
      self.selected_character = character
    self.redraw()
    self.root.update_idletasks()
    self.center_view_on_selected_character()

  def set_movement_limit(self):
    try:
      limit = int(self.movement_var.get())
    except ValueError:
      messagebox.showerror(
          "Invalid movement",
          "Enter a whole number of feet from 1 to 35.",
          parent=self.root,
      )
      return
    if not 1 <= limit <= self.MAX_MOVEMENT:
      messagebox.showerror(
          "Invalid movement",
          "Movement must be between 1 and 35 feet.",
          parent=self.root,
      )
      return
    character = self.selected_character
    if character.has_moved:
      return
    if character.distance_moved > limit:
      messagebox.showerror(
          "Movement is already spent",
          "The new range cannot be less than the distance this character "
          "has already moved this turn.",
          parent=self.root,
      )
      return
    character.movement_limit = limit
    self.preview_position = None
    self.redraw()
    self.root.update_idletasks()
    self.center_view_on_selected_character()

  def confirm_move(self):
    if self.preview_position is None:
      return
    character = self.selected_character
    if character.has_moved:
      self.preview_position = None
      self.redraw()
      return
    column, row = self.preview_position
    distance = math.hypot(
        column - character.start_column,
        row - character.start_row,
    )
    if character.movement_limit is None or distance > character.movement_limit:
      self.preview_position = None
      self.redraw()
      return
    if self.position_is_occupied(character, column, row):
      self.preview_position = None
      self.redraw()
      self.status_var.set("That square is occupied. Choose an empty square.")
      return
    character.column = column
    character.row = row
    character.has_moved = True
    character.movement_limit = None
    self.preview_position = None

    current_index = self.characters.index(character)
    for offset in range(1, len(self.characters) + 1):
      next_character = self.characters[
          (current_index + offset) % len(self.characters)
      ]
      if not next_character.has_moved:
        self.selected_character = next_character
        break

    self.movement_var.set("")
    self.redraw()

  def add_character(self):
    column, row = self.find_open_square()
    if column is None:
      messagebox.showerror(
          "No room for character",
          "There are no unoccupied grid squares available.",
          parent=self.root,
      )
      return
    color = self.COLORS[(self.next_character_number - 1) % len(self.COLORS)]
    character = CharacterToken(
        str(self.next_character_number), color, column, row, column, row
    )
    self.next_character_number += 1
    self.characters.append(character)
    self.selected_character = character
    self.preview_position = None
    self.redraw()

  def find_open_square(self):
    for row in range(self.ROWS):
      for column in range(self.COLUMNS):
        if not self.position_is_occupied(None, column, row):
          return column, row
    return None, None

  def reset_turn(self):
    self.preview_position = None
    for character in self.characters:
      character.start_column = character.column
      character.start_row = character.row
      character.movement_limit = None
      character.has_moved = False
    self.redraw()

  @property
  def cell_size(self):
    return self.CELL_SIZE * self.zoom

  @property
  def token_radius(self):
    return max(4, self.cell_size * self.TOKEN_RADIUS / self.CELL_SIZE)

  def adjust_zoom(self, amount):
    self.zoom_var.set(
        min(self.ZOOM_MAX, max(self.ZOOM_MIN, self.zoom + amount))
    )
    self.set_zoom(self.zoom_var.get())

  def set_zoom(self, value):
    self.zoom = min(self.ZOOM_MAX, max(self.ZOOM_MIN, float(value)))
    self.zoom_label.config(text=f"{round(self.zoom * 100)}%")
    self.redraw()
    self.root.update_idletasks()
    self.center_view_on_selected_character()

  def center_view_on_selected_character(self):
    x, y = self.grid_to_canvas(
        self.selected_character.start_column,
        self.selected_character.start_row,
    )
    region_width = (self.COLUMNS + 2 * self.VIEW_MARGIN) * self.cell_size
    region_height = (self.ROWS + 2 * self.VIEW_MARGIN) * self.cell_size
    self.canvas.xview_moveto(
        max(0, (x - self.canvas.winfo_width() / 2) / region_width)
    )
    self.canvas.yview_moveto(
        max(0, (y - self.canvas.winfo_height() / 2) / region_height)
    )


if __name__ == "__main__":
  root = tk.Tk()
  app = CharacterProximityApp(root)
  root.mainloop()