import tkinter as tk
from tkinter import ttk, messagebox
import math

def is_valid(region, color, assignment, adjacency):
    for neighbor in adjacency.get(region, []):
        if assignment.get(neighbor) == color:
            return False
    return True

def backtrack(regions, adjacency, colors, assignment):
    if len(assignment) == len(regions):
        return assignment
    unassigned = [r for r in regions if r not in assignment]
    region = unassigned[0]
    for color in colors:
        if is_valid(region, color, assignment, adjacency):
            assignment[region] = color
            result = backtrack(regions, adjacency, colors, assignment)
            if result:
                return result
            del assignment[region]
    return None

class MapColoringApp:
    COLORS = ["Red", "Green", "Blue", "Yellow"]
    COLOR_HEX = {
        "Red":    "#ef4444",
        "Green":  "#22c55e",
        "Blue":   "#3b82f6",
        "Yellow": "#eab308",
        "White":  "#e5e7eb",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Map Coloring – CSP Solver")
        self.root.geometry("900x620")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(True, True)

        self.regions = []          
        self.adjacency = {}        
        self.node_positions = {}   
        self.assignment = {}       
        self.dragging = None

        self._build_ui()
        self._load_sample()

    def _build_ui(self):
        left = tk.Frame(self.root, bg="#2a2a3e", width=260)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(12,0), pady=12)
        left.pack_propagate(False)

        tk.Label(left, text="MAP COLORING", bg="#2a2a3e", fg="#a78bfa",
                 font=("Courier", 11, "bold")).pack(pady=(16,2))
        tk.Label(left, text="CSP Solver", bg="#2a2a3e", fg="#6b7280",
                 font=("Courier", 9)).pack(pady=(0,14))

        self._section(left, "ADD REGION")
        self.region_entry = self._entry(left, "Region name (e.g. A)")
        tk.Button(left, text="+ Add Region", command=self._add_region,
                  bg="#7c3aed", fg="white", font=("Courier", 9, "bold"),
                  relief=tk.FLAT, padx=8, pady=5, cursor="hand2").pack(fill=tk.X, padx=12, pady=(0,12))

        self._section(left, "ADD ADJACENCY")
        self.adj_from = self._dropdown(left, "From:")
        self.adj_to   = self._dropdown(left, "To:")
        tk.Button(left, text="+ Add Edge", command=self._add_edge,
                  bg="#7c3aed", fg="white", font=("Courier", 9, "bold"),
                  relief=tk.FLAT, padx=8, pady=5, cursor="hand2").pack(fill=tk.X, padx=12, pady=(0,12))

        self._section(left, "COLORS AVAILABLE")
        self.color_vars = {}
        for c in self.COLORS:
            var = tk.BooleanVar(value=True)
            self.color_vars[c] = var
            f = tk.Frame(left, bg="#2a2a3e")
            f.pack(anchor=tk.W, padx=16, pady=1)
            tk.Checkbutton(f, text=c, variable=var, bg="#2a2a3e",
                           fg=self.COLOR_HEX[c], selectcolor="#1e1e2e",
                           activebackground="#2a2a3e",
                           font=("Courier", 9)).pack(side=tk.LEFT)

        
        tk.Frame(left, bg="#2a2a3e", height=1).pack(fill=tk.X, padx=12, pady=10,)

        tk.Button(left, text="▶  SOLVE", command=self._solve,
                  bg="#059669", fg="white", font=("Courier", 10, "bold"),
                  relief=tk.FLAT, padx=8, pady=7, cursor="hand2").pack(fill=tk.X, padx=12, pady=3)

        tk.Button(left, text="↺  Reset Colors", command=self._reset_colors,
                  bg="#374151", fg="#d1d5db", font=("Courier", 9),
                  relief=tk.FLAT, padx=8, pady=5, cursor="hand2").pack(fill=tk.X, padx=12, pady=3)

        tk.Button(left, text="✕  Clear All", command=self._clear_all,
                  bg="#374151", fg="#d1d5db", font=("Courier", 9),
                  relief=tk.FLAT, padx=8, pady=5, cursor="hand2").pack(fill=tk.X, padx=12, pady=3)

        tk.Button(left, text="★  Load Sample", command=self._load_sample,
                  bg="#374151", fg="#d1d5db", font=("Courier", 9),
                  relief=tk.FLAT, padx=8, pady=5, cursor="hand2").pack(fill=tk.X, padx=12, pady=3)
        right = tk.Frame(self.root, bg="#1e1e2e")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=12)

        tk.Label(right, text="Graph Visualization  (drag nodes to reposition)",
                 bg="#1e1e2e", fg="#6b7280", font=("Courier", 8)).pack(anchor=tk.W)

        self.canvas = tk.Canvas(right, bg="#12121f", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<ButtonPress-1>",   self._on_press)
        self.canvas.bind("<B1-Motion>",       self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        self.result_frame = tk.Frame(right, bg="#1e1e2e")
        self.result_frame.pack(fill=tk.X, pady=(8,0))

        self.result_label = tk.Label(self.result_frame, text="", bg="#1e1e2e",
                                     fg="#a78bfa", font=("Courier", 9),
                                     justify=tk.LEFT, wraplength=580)
        self.result_label.pack(anchor=tk.W)

    def _section(self, parent, title):
        tk.Label(parent, text=title, bg="#2a2a3e", fg="#6b7280",
                 font=("Courier", 8, "bold")).pack(anchor=tk.W, padx=12, pady=(8,2))

    def _entry(self, parent, placeholder):
        e = tk.Entry(parent, bg="#1e1e2e", fg="#e5e7eb", insertbackground="white",
                     font=("Courier", 10), relief=tk.FLAT, bd=0)
        e.pack(fill=tk.X, padx=12, pady=(0,6), ipady=5)
        e.insert(0, placeholder)
        e.bind("<FocusIn>",  lambda ev: e.delete(0, tk.END) if e.get()==placeholder else None)
        e.bind("<FocusOut>", lambda ev: e.insert(0, placeholder) if e.get()=='' else None)
        return e

    def _dropdown(self, parent, label):
        tk.Label(parent, text=label, bg="#2a2a3e", fg="#9ca3af",
                 font=("Courier", 8)).pack(anchor=tk.W, padx=16)
        cb = ttk.Combobox(parent, values=[], state="readonly", font=("Courier", 9))
        cb.pack(fill=tk.X, padx=12, pady=(0,6))
        return cb

    def _refresh_dropdowns(self):
        vals = self.regions[:]
        self.adj_from["values"] = vals
        self.adj_to["values"]   = vals

    def _add_region(self):
        name = self.region_entry.get().strip()
        if not name or name == "Region name (e.g. A)":
            messagebox.showwarning("Input", "Enter a region name.")
            return
        if name in self.regions:
            messagebox.showwarning("Duplicate", f"'{name}' already exists.")
            return
        self.regions.append(name)
        self.adjacency[name] = []
        n = len(self.regions)
        cx, cy, r = 300, 230, 160
        angle = 2 * math.pi * (n - 1) / max(n, 1)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        self.node_positions[name] = (x, y)
        self.region_entry.delete(0, tk.END)
        self._refresh_dropdowns()
        self._reposition_nodes()
        self._draw()

    def _add_edge(self):
        a = self.adj_from.get()
        b = self.adj_to.get()
        if not a or not b:
            messagebox.showwarning("Input", "Select both regions.")
            return
        if a == b:
            messagebox.showwarning("Input", "A region can't be adjacent to itself.")
            return
        if b not in self.adjacency[a]:
            self.adjacency[a].append(b)
        if a not in self.adjacency[b]:
            self.adjacency[b].append(a)
        self._draw()

    def _reposition_nodes(self):
        n = len(self.regions)
        if n == 0:
            return
        cx, cy, r = 300, 230, 160
        for i, reg in enumerate(self.regions):
            angle = 2 * math.pi * i / n - math.pi / 2
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            self.node_positions[reg] = (x, y)

    def _draw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 600
        h = self.canvas.winfo_height() or 420

        for reg, neighbors in self.adjacency.items():
            x1, y1 = self.node_positions.get(reg, (0,0))
            for nb in neighbors:
                x2, y2 = self.node_positions.get(nb, (0,0))
                self.canvas.create_line(x1, y1, x2, y2,
                                        fill="#374151", width=2, smooth=True)

        R = 28
        for reg in self.regions:
            x, y = self.node_positions.get(reg, (0,0))
            color_name = self.assignment.get(reg, None)
            fill = self.COLOR_HEX.get(color_name, "#374151") if color_name else "#374151"
            outline = "#a78bfa" if color_name else "#6b7280"

            self.canvas.create_oval(x-R, y-R, x+R, y+R,
                                    fill=fill, outline=outline, width=2,
                                    tags=("node", reg))
            self.canvas.create_text(x, y, text=reg, fill="white",
                                    font=("Courier", 11, "bold"), tags=("node", reg))
            if color_name:
                self.canvas.create_text(x, y+R+12, text=color_name,
                                        fill=self.COLOR_HEX[color_name],
                                        font=("Courier", 8))

        if not self.regions:
            self.canvas.create_text(w//2, h//2,
                                    text="Add regions and adjacencies\nthen click SOLVE",
                                    fill="#374151", font=("Courier", 11), justify=tk.CENTER)

    def _on_press(self, event):
        for reg in self.regions:
            x, y = self.node_positions[reg]
            if abs(event.x - x) < 30 and abs(event.y - y) < 30:
                self.dragging = reg
                return

    def _on_drag(self, event):
        if self.dragging:
            self.node_positions[self.dragging] = (event.x, event.y)
            self._draw()

    def _on_release(self, event):
        self.dragging = None

    def _solve(self):
        if not self.regions:
            messagebox.showwarning("Empty", "Add at least one region.")
            return
        selected_colors = [c for c, v in self.color_vars.items() if v.get()]
        if not selected_colors:
            messagebox.showwarning("Colors", "Select at least one color.")
            return

        result = backtrack(self.regions, self.adjacency, selected_colors, {})

        if result:
            self.assignment = result
            self._draw()
            lines = [f"  {r}  →  {c}" for r, c in result.items()]
            self.result_label.config(
                text="✔  Solution Found:\n" + "\n".join(lines),
                fg="#22c55e"
            )
        else:
            self.assignment = {}
            self._draw()
            self.result_label.config(
                text="✘  No solution found with the selected colors. Try adding more colors.",
                fg="#ef4444"
            )

    def _reset_colors(self):
        self.assignment = {}
        self.result_label.config(text="")
        self._draw()

    def _clear_all(self):
        self.regions.clear()
        self.adjacency.clear()
        self.node_positions.clear()
        self.assignment.clear()
        self._refresh_dropdowns()
        self.result_label.config(text="")
        self._draw()

    def _load_sample(self):
        self._clear_all()
        for r in ["A", "B", "C", "D"]:
            self.regions.append(r)
            self.adjacency[r] = []

        edges = [("A","B"),("A","C"),("B","C"),("B","D"),("C","D")]
        for a, b in edges:
            self.adjacency[a].append(b)
            self.adjacency[b].append(a)

        self._refresh_dropdowns()
        self._reposition_nodes()
        self._draw()
        self.result_label.config(text="Sample loaded! Click SOLVE to color the map.", fg="#a78bfa")



if __name__ == "__main__":
    root = tk.Tk()
    app = MapColoringApp(root)
    root.after(100, app._draw)   
    root.mainloop()
