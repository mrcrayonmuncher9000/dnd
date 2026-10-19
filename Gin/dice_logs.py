import datetime
import random
import tkinter as tk
from tkinter import messagebox


class InteractiveDiceLogsApp:
  BG = "#3a3a3a"
  FG = "#e0e0e0"
  DICE_TYPES = (2, 4, 6, 8, 10, 20, 100)

  def __init__(self, root):
    self.root = root
    self.root.title("Dice Roller")
    self.root.geometry("380x500")
    self.root.minsize(340, 440)
    self.root.configure(bg=self.BG)

    self.logs = [
        {
            "time": "12:00 pm",
            "details": (
                "Rolled 1 D6 (advantage) -1 +Dexterity: 4 | Rolls: 3, 5"
            ),
        },
        {
            "time": "2:30 pm",
            "details": (
                "Rolled 1 D20 (disadvantage) -1 +Intelligence: 15 | Rolls: 16"
            ),
        },
        {
            "time": "3:16 pm",
            "details": "Rolled 5 D20: 37 | Rolls: 9, 18, 7, 2, 1",
        },
    ]
    self.quick_actions = []
    self.selected_dice = 20
    self.is_expanded = True
    self.setup_ui()

  def setup_ui(self):
    self.container = tk.Frame(self.root, bg=self.BG, padx=14, pady=12)
    self.container.pack(fill=tk.BOTH, expand=True)

    dice_frame = tk.Frame(self.container, bg=self.BG)
    dice_frame.pack(fill=tk.X, pady=(0, 12))
    self.dice_buttons = {}
    for dice_type in self.DICE_TYPES:
      button = tk.Button(
          dice_frame,
          text=f"D{dice_type}",
          font=("Arial", 9, "bold"),
          fg="#1a1a1a",
          bg="#e0e0e0",
          activebackground="#cccccc",
          bd=0,
          padx=7,
          pady=4,
          relief=tk.FLAT,
          command=lambda sides=dice_type: self.select_dice(sides),
          cursor="hand2",
      )
      button.pack(side=tk.LEFT, padx=(0, 5))
      self.dice_buttons[dice_type] = button
    self.select_dice(self.selected_dice)

    options_frame = tk.Frame(self.container, bg=self.BG)
    options_frame.pack(fill=tk.X, pady=(0, 10))
    options_frame.grid_columnconfigure(1, weight=1)
    options_frame.grid_columnconfigure(3, weight=1)

    self.count_var = tk.StringVar(value="1")
    self.modifier_var = tk.StringVar(value="0")
    self.attribute_var = tk.StringVar(value="None")
    self.mode_var = tk.StringVar(value="None")

    self._add_option_label(options_frame, "Number of Dice:", 0, 0)
    self.count_entry = self._add_entry(
        options_frame, self.count_var, 0, 1
    )
    self._add_option_label(options_frame, "Attributes:", 0, 2)
    self._add_option_menu(
        options_frame,
        self.attribute_var,
        ("None", "Strength", "Dexterity", "Constitution", "Intelligence",
         "Wisdom", "Charisma"),
        0,
        3,
    )

    self._add_option_label(options_frame, "Ability Modifier:", 1, 0)
    self._add_entry(options_frame, self.modifier_var, 1, 1)
    self._add_option_label(options_frame, "Advantage:", 1, 2)
    self._add_option_menu(
        options_frame,
        self.mode_var,
        ("None", "Advantage", "Disadvantage"),
        1,
        3,
    )

    buttons_frame = tk.Frame(self.container, bg=self.BG)
    buttons_frame.pack(fill=tk.X, pady=(0, 8))
    self._make_button(
        buttons_frame, "Reset Dice  ⟳", self.reset_dice
    ).pack(side=tk.LEFT)
    self._make_button(
        buttons_frame, "Roll Dice  🎲", self.perform_roll
    ).pack(side=tk.RIGHT)

    quick_action_frame = tk.Frame(self.container, bg=self.BG)
    quick_action_frame.pack(fill=tk.X, pady=(0, 8))
    self._make_button(
        quick_action_frame,
        "Add to Quick Action  ⊞",
        self.add_quick_action,
        dark=True,
    ).pack(side=tk.LEFT)
    self.quick_action_status = tk.Label(
        quick_action_frame,
        text="",
        font=("Arial", 8),
        fg="#bdbdbd",
        bg=self.BG,
    )
    self.quick_action_status.pack(side=tk.RIGHT)

    divider = tk.Frame(self.container, bg="#555555", height=1)
    divider.pack(fill=tk.X, pady=(4, 8))

    self.toggle_btn = tk.Button(
        self.container,
        text="▼ Dice Logs",
        font=("Arial", 9),
        fg="#d0d0d0",
        bg=self.BG,
        activebackground=self.BG,
        activeforeground="#ffffff",
        bd=0,
        relief=tk.FLAT,
        command=self.toggle_logs,
        cursor="hand2",
    )
    self.toggle_btn.pack(anchor="w", pady=(0, 4))

    self.content_frame = tk.Frame(self.container, bg=self.BG)
    self.content_frame.pack(fill=tk.BOTH, expand=True)

    self.logs_view = tk.Frame(self.content_frame, bg=self.BG)
    self.logs_view.pack(fill=tk.BOTH, expand=True)
    self.logs_canvas = tk.Canvas(
        self.logs_view,
        bg=self.BG,
        highlightthickness=0,
        height=110,
    )
    self.logs_scrollbar = tk.Scrollbar(
        self.logs_view, orient=tk.VERTICAL, command=self.logs_canvas.yview
    )
    self.logs_canvas.configure(yscrollcommand=self.logs_scrollbar.set)
    self.logs_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    self.logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    self.logs_container = tk.Frame(self.logs_canvas, bg=self.BG)
    self.logs_window = self.logs_canvas.create_window(
        (0, 0), window=self.logs_container, anchor="nw"
    )
    self.logs_container.bind("<Configure>", self._update_scroll_region)
    self.logs_canvas.bind("<Configure>", self._resize_logs)

    self.clear_btn = self._make_button(
        self.content_frame, "Clear Logs  🗑", self.clear_logs
    )
    self.clear_btn.pack(anchor="w", pady=(6, 2))

    self.render_logs()

  def _add_option_label(self, parent, text, row, column):
    tk.Label(
        parent,
        text=text,
        font=("Arial", 8),
        fg="#cccccc",
        bg=self.BG,
    ).grid(row=row, column=column, sticky="w", padx=(0, 4), pady=5)

  def _add_entry(self, parent, variable, row, column):
    entry = tk.Entry(
        parent,
        textvariable=variable,
        width=5,
        bg="#555555",
        fg="#ffffff",
        insertbackground="#ffffff",
        bd=0,
        justify=tk.CENTER,
    )
    entry.grid(row=row, column=column, sticky="w", padx=(0, 8), pady=4)
    return entry

  def _add_option_menu(self, parent, variable, values, row, column):
    menu = tk.OptionMenu(parent, variable, *values)
    menu.config(
        bg="#555555",
        fg="#ffffff",
        activebackground="#666666",
        activeforeground="#ffffff",
        bd=0,
        highlightthickness=0,
        width=9,
    )
    menu["menu"].config(bg="#444444", fg="#ffffff")
    menu.grid(row=row, column=column, sticky="ew", padx=(0, 4), pady=2)

  def _make_button(self, parent, text, command, dark=False):
    return tk.Button(
        parent,
        text=text,
        font=("Arial", 8, "bold"),
        fg="#ffffff" if dark else "#1a1a1a",
        bg="#1a1a1a" if dark else "#e0e0e0",
        activebackground="#333333" if dark else "#cccccc",
        activeforeground="#ffffff" if dark else "#000000",
        bd=0,
        padx=10,
        pady=5,
        relief=tk.FLAT,
        command=command,
        cursor="hand2",
    )

  def select_dice(self, sides):
    self.selected_dice = sides
    for dice_type, button in self.dice_buttons.items():
      button.config(relief=tk.SUNKEN if dice_type == sides else tk.FLAT)

  def reset_dice(self):
    self.count_var.set("1")
    self.modifier_var.set("0")
    self.attribute_var.set("None")
    self.mode_var.set("None")
    self.select_dice(20)

  def render_logs(self):
    for widget in self.logs_container.winfo_children():
      widget.destroy()

    if not self.logs:
      tk.Label(
          self.logs_container,
          text="No dice logs available.",
          font=("Arial", 9),
          fg="#a0a0a0",
          bg=self.BG,
      ).pack(anchor="w", pady=5)
    else:
      for entry in self.logs:
        row = tk.Frame(self.logs_container, bg=self.BG, pady=3)
        row.pack(fill=tk.X, anchor="w")
        tk.Label(
            row,
            text=entry["time"],
            font=("Arial", 8, "underline"),
            fg="#cccccc",
            bg=self.BG,
        ).pack(side=tk.LEFT)
        tk.Label(
            row,
            text=f" — {entry['details']}",
            font=("Arial", 8),
            fg=self.FG,
            bg=self.BG,
            anchor="w",
            justify=tk.LEFT,
            wraplength=290,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

    self.logs_canvas.yview_moveto(0)
    self._update_scroll_region()
    if len(self.logs) > 4:
      self.logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    else:
      self.logs_scrollbar.pack_forget()

  def _update_scroll_region(self, _event=None):
    self.logs_canvas.configure(
        scrollregion=self.logs_canvas.bbox("all")
    )

  def _resize_logs(self, event):
    self.logs_canvas.itemconfigure(self.logs_window, width=event.width)

  def toggle_logs(self):
    self.is_expanded = not self.is_expanded
    if self.is_expanded:
      self.toggle_btn.config(text="▼ Dice Logs")
      self.content_frame.pack(fill=tk.BOTH, expand=True)
    else:
      self.toggle_btn.config(text="▶ Dice Logs")
      self.content_frame.pack_forget()

  def clear_logs(self):
    self.logs = []
    self.render_logs()

  def add_quick_action(self):
    self.quick_actions.append({
        "dice": self.selected_dice,
        "count": self.count_var.get(),
        "modifier": self.modifier_var.get(),
        "attribute": self.attribute_var.get(),
        "mode": self.mode_var.get(),
    })
    self.quick_action_status.config(text="Quick action added.")

  def perform_roll(self):
    try:
      count = int(self.count_var.get())
      modifier = int(self.modifier_var.get())
    except ValueError:
      messagebox.showerror(
          "Invalid dice settings",
          "Number of dice and ability modifier must be whole numbers.",
          parent=self.root,
      )
      return

    if count < 1:
      messagebox.showerror(
          "Invalid dice settings",
          "Number of dice must be at least 1.",
          parent=self.root,
      )
      return

    mode = self.mode_var.get()
    if mode in ("Advantage", "Disadvantage"):
      rolls = [
          random.randint(1, self.selected_dice),
          random.randint(1, self.selected_dice),
      ]
      chosen_roll = max(rolls) if mode == "Advantage" else min(rolls)
      total = chosen_roll + modifier
      roll_count = 1
      mode_text = f" ({mode.lower()})"
    else:
      rolls = [
          random.randint(1, self.selected_dice) for _ in range(count)
      ]
      total = sum(rolls) + modifier
      roll_count = count
      mode_text = ""

    modifier_text = f" {'+' if modifier >= 0 else ''}{modifier}"
    attribute = self.attribute_var.get()
    attribute_text = f" +{attribute}" if attribute != "None" else ""
    details = (
        f"Rolled {roll_count} D{self.selected_dice}{mode_text}"
        f"{modifier_text}{attribute_text}: {total} | Rolls: "
        f"{', '.join(map(str, rolls))}"
    )
    current_time = datetime.datetime.now().strftime("%I:%M %p").lower()
    self.logs.insert(0, {"time": current_time, "details": details})
    self.render_logs()


if __name__ == "__main__":
  root = tk.Tk()
  app = InteractiveDiceLogsApp(root)
  root.mainloop()
