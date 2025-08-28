import tkinter as tk
from tkinter import messagebox, filedialog
import numpy as np
from collections import defaultdict
import json
import time
from copy import deepcopy

# --------------------------------------
# StarBattleApp: GUI for Star Battle Solver
# --------------------------------------
class StarBattleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Star Battle Solver (Hybrid Snapshot Backtracking)")

        # Initialize variables
        self.n = tk.IntVar(value=8)  # Board size (n x n)
        self.k = tk.IntVar(value=1)  # Number of stars per row/column/region
        self.selected_color_idx = tk.IntVar(value=1)  # Default color index (avoid 0 for unmarked)
        self.colors = [
            "#FFFFFF",  # index 0 reserved for blank/unmarked
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",
            "#800000", "#008000", "#000080", "#808000", "#800080", "#008080",
            "#C0C0C0", "#808080", "#FFA500", "#A52A2A", "#FFC0CB", "#FFD700"
        ]

        # Track color selection changes
        try:
            self.selected_color_idx.trace_add('write', lambda *args: self.update_color_preview())
        except AttributeError:
            self.selected_color_idx.trace('w', lambda *args: self.update_color_preview())

        # Use -1 to represent unmarked cells
        self.regions = np.full((self.n.get(), self.n.get()), -1, dtype=int)
        self.solution = None

        # Build the interface
        self.create_widgets()

    def create_widgets(self):
        # Control panel on the left
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(control_frame, text="Board Settings", font=('Arial', 12, 'bold')).pack(pady=5)

        tk.Label(control_frame, text="Board size n (n x n):").pack()
        tk.Spinbox(control_frame, from_=4, to=20, textvariable=self.n,
                   command=self.reset_board).pack()

        tk.Label(control_frame, text="Stars per row/column (k):").pack()
        tk.Spinbox(control_frame, from_=1, to=5, textvariable=self.k).pack()

        tk.Label(control_frame, text="Color Selection", font=('Arial', 12, 'bold')).pack(pady=5)

        tk.Label(control_frame, text="Color index (0 = blank):").pack()
        tk.Spinbox(control_frame, from_=0, to=len(self.colors) - 1,
                   textvariable=self.selected_color_idx,
                   command=self.update_color_preview).pack()

        # Color preview label
        self.color_preview = tk.Label(control_frame, text="Current color",
                                      width=15, height=2, relief=tk.SUNKEN)
        self.color_preview.pack(pady=5)
        self.update_color_preview()

        # Control buttons
        tk.Button(control_frame, text="Reset Board", command=self.reset_board).pack(pady=5)
        tk.Button(control_frame, text="Solve", command=self.solve).pack(pady=5)
        tk.Button(control_frame, text="Save Config", command=self.save_config).pack(pady=5)
        tk.Button(control_frame, text="Load Config", command=self.load_config).pack(pady=5)

        # Status label
        self.status_label = tk.Label(control_frame, text="Waiting to solve...",
                                     wraplength=150, justify=tk.LEFT)
        self.status_label.pack(pady=5)

        # Board frame on the right
        self.board_frame = tk.Frame(self.root, padx=10, pady=10)
        self.board_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.create_board()

    def create_board(self):
        # Clear existing board widgets
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        n = self.n.get()
        # Initialize regions with -1 (unmarked)
        self.regions = np.full((n, n), -1, dtype=int)
        self.cells = []

        # Create grid of buttons for the board
        for r in range(n):
            row = []
            for c in range(n):
                cell = tk.Button(self.board_frame, width=3, height=1, bg="white",
                                 command=lambda r=r, c=c: self.mark_cell(r, c))
                cell.grid(row=r, column=c, padx=1, pady=1)
                row.append(cell)
            self.cells.append(row)

    def mark_cell(self, r, c):
        # Mark a cell with the selected color
        color_idx = self.selected_color_idx.get()
        self.regions[r][c] = color_idx
        if 0 <= color_idx < len(self.colors):
            self.cells[r][c].config(bg=self.colors[color_idx])
        else:
            self.cells[r][c].config(bg="white")

    def update_color_preview(self):
        # Update the color preview label
        try:
            color_idx = int(self.selected_color_idx.get())
        except (tk.TclError, ValueError):
            color_idx = 0

        if 0 <= color_idx < len(self.colors):
            color = self.colors[color_idx]
        else:
            color = "white"

        self.color_preview.config(bg=color, text=f"Color {color_idx}")

    def reset_board(self):
        # Reset the board to initial state
        self.n.set(self.n.get())  # Trigger update
        self.create_board()
        self.solution = None
        self.status_label.config(text="Waiting to solve...")

    def solve(self):
        # Solve the Star Battle puzzle
        n = self.n.get()
        k = self.k.get()
        regions = self.regions.tolist()

        # Check if any regions are marked (all -1 means no markings)
        if np.max(self.regions) == -1:
            messagebox.showerror("Error", "Please mark at least one region!")
            return

        # Simple check for region sizes (skip -1)
        region_sizes = defaultdict(int)
        for r in range(n):
            for c in range(n):
                rid = self.regions[r][c]
                if rid == -1:
                    continue
                region_sizes[rid] += 1

        for rid, size in region_sizes.items():
            if size < k:
                messagebox.showerror("Error", f"Region {rid} is too small ({size} cells), cannot place {k} stars!")
                return

        self.status_label.config(text="Solving...")
        self.root.update()

        start_time = time.time()
        solver = ImprovedStarBattleSolver(n, self.regions.tolist(), k, unlabeled=-1)
        solution = solver.solve(timeout=600)

        if not solution:
            self.status_label.config(text="No solution")
            messagebox.showinfo("Result", "No feasible solution found!")
        else:
            self.display_solution(solution)
            solve_time = time.time() - start_time
            self.status_label.config(text=f"Solved ({solve_time:.2f}s)")
            messagebox.showinfo("Result", f"Solution found! Time: {solve_time:.2f} seconds")

    def display_solution(self, solution):
        # Display the solution on the board
        n = self.n.get()

        # Reset board colors (unmarked cells show white)
        for r in range(n):
            for c in range(n):
                rid = self.regions[r][c]
                if rid == -1:
                    bg = "white"
                elif 0 <= rid < len(self.colors):
                    bg = self.colors[rid]
                else:
                    bg = "white"
                self.cells[r][c].config(bg=bg, text="")

        # Mark star positions
        for (r, c) in solution:
            self.cells[r][c].config(text="★", fg="black", font=('Arial', 12, 'bold'))

    def save_config(self):
        # Save current configuration to file
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filepath:
            data = {
                "n": self.n.get(),
                "k": self.k.get(),
                "regions": self.regions.tolist()
            }

            with open(filepath, 'w') as f:
                json.dump(data, f)

    def load_config(self):
        # Load configuration from file
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filepath:
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)

                # Validate configuration format
                if not all(key in data for key in ["n", "k", "regions"]):
                    messagebox.showerror("Error", "Invalid configuration file format")
                    return

                self.n.set(data["n"])
                self.k.set(data["k"])

                loaded_regions = np.array(data["regions"])
                if loaded_regions.shape != (data["n"], data["n"]):
                    messagebox.showerror("Error", "Region data size mismatch")
                    return

                self.create_board()
                self.regions = loaded_regions

                # Update board display
                n = self.n.get()
                for r in range(n):
                    for c in range(n):
                        rid = int(self.regions[r][c])
                        if rid == -1:
                            bg = "white"
                        elif 0 <= rid < len(self.colors):
                            bg = self.colors[rid]
                        else:
                            bg = "white"
                        self.cells[r][c].config(bg=bg, text="")

                self.solution = None
                self.status_label.config(text="Configuration loaded")
                messagebox.showinfo("Success", "Configuration loaded successfully")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")


# --------------------------------------
# ImprovedStarBattleSolver: Enhanced solver
#   - Supports unlabeled = -1 (skipped)
#   - Includes defensive checks and final validation
# --------------------------------------
class ImprovedStarBattleSolver:
    def __init__(self, n, regions, k, unlabeled=-1):
        self.n = n  # Board size
        self.k = k  # Stars per row/column/region
        self.regions = regions  # Region matrix
        self.unlabeled = unlabeled  # Value for unmarked cells
        self.solution = set()  # Set of star positions

        # Counters for remaining stars needed
        self.rows_needed = [k] * n
        self.cols_needed = [k] * n
        self.regs_needed = defaultdict(int)  # Default 0 for unmarked regions

        # Forbidden counts for cells (due to adjacent stars)
        self.forbidden_counts = defaultdict(int)

        # Precompute neighbors (8-direction)
        self.neighbors = {}
        for r in range(n):
            for c in range(n):
                neigh = []
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < n and 0 <= nc < n:
                            neigh.append((nr, nc))
                self.neighbors[(r, c)] = neigh

        # Group cells by region (skip unlabeled)
        self.region_cells = defaultdict(list)
        for r in range(n):
            for c in range(n):
                rid = self.regions[r][c]
                if rid == unlabeled:
                    continue
                self.region_cells[rid].append((r, c))

        # Initialize stars needed for each marked region
        for rid in self.region_cells:
            self.regs_needed[rid] = k

        # Statistics
        self.nodes_visited = 0
        self.propagations = 0

    def can_place_star(self, r, c):
        # Check if a star can be placed at (r, c)
        if (r, c) in self.solution:
            return False
        if self.forbidden_counts.get((r, c), 0) > 0:
            return False
        if self.rows_needed[r] <= 0 or self.cols_needed[c] <= 0:
            return False
        rid = self.regions[r][c]
        if rid != self.unlabeled and self.regs_needed.get(rid, 0) <= 0:
            return False
        # Check if any neighbor already has a star
        for nr, nc in self.neighbors[(r, c)]:
            if (nr, nc) in self.solution:
                return False
        return True

    def place_star_forced(self, r, c):
        # Place a star with defensive checks (for constraint propagation)
        for nr, nc in self.neighbors[(r, c)]:
            if (nr, nc) in self.solution:
                return False

        self.solution.add((r, c))
        self.rows_needed[r] -= 1
        self.cols_needed[c] -= 1
        rid = self.regions[r][c]
        if rid != self.unlabeled:
            self.regs_needed[rid] -= 1

        # Update forbidden counts for neighbors
        for nr, nc in self.neighbors[(r, c)]:
            self.forbidden_counts[(nr, nc)] += 1

        return True

    def place_star(self, r, c):
        # Place a star and return affected forbidden cells
        # Defensive check for adjacent stars
        for nr, nc in self.neighbors[(r, c)]:
            if (nr, nc) in self.solution:
                raise RuntimeError("Attempting to place star adjacent to existing star")

        self.solution.add((r, c))
        self.rows_needed[r] -= 1
        self.cols_needed[c] -= 1
        rid = self.regions[r][c]
        if rid != self.unlabeled:
            self.regs_needed[rid] -= 1

        new_forbidden = []
        for nr, nc in self.neighbors[(r, c)]:
            self.forbidden_counts[(nr, nc)] += 1
            if self.forbidden_counts[(nr, nc)] == 1:
                new_forbidden.append((nr, nc))

        return new_forbidden

    def remove_star(self, r, c, new_forbidden):
        # Remove a star and restore state
        self.solution.remove((r, c))
        self.rows_needed[r] += 1
        self.cols_needed[c] += 1
        rid = self.regions[r][c]
        if rid != self.unlabeled:
            self.regs_needed[rid] += 1

        # Restore forbidden counts
        for nr, nc in new_forbidden:
            self.forbidden_counts[(nr, nc)] -= 1
            if self.forbidden_counts[(nr, nc)] == 0:
                del self.forbidden_counts[(nr, nc)]

    def propagate_constraints(self):
        # Propagate constraints until no more changes
        changed = True
        while changed:
            changed = False
            self.propagations += 1

            # Check rows
            for r in range(self.n):
                if self.rows_needed[r] > 0:
                    valid_positions = [c for c in range(self.n) if self.can_place_star(r, c)]
                    if len(valid_positions) == self.rows_needed[r]:
                        for c in valid_positions:
                            if self.place_star_forced(r, c):
                                changed = True
                    elif len(valid_positions) < self.rows_needed[r]:
                        return False

            # Check columns
            for c in range(self.n):
                if self.cols_needed[c] > 0:
                    valid_positions = [r for r in range(self.n) if self.can_place_star(r, c)]
                    if len(valid_positions) == self.cols_needed[c]:
                        for r in valid_positions:
                            if self.place_star_forced(r, c):
                                changed = True
                    elif len(valid_positions) < self.cols_needed[c]:
                        return False

            # Check regions
            for region_id, cells in self.region_cells.items():
                if self.regs_needed[region_id] > 0:
                    valid_positions = [(r, c) for (r, c) in cells if self.can_place_star(r, c)]
                    if len(valid_positions) == self.regs_needed[region_id]:
                        for r, c in valid_positions:
                            if self.place_star_forced(r, c):
                                changed = True
                    elif len(valid_positions) < self.regs_needed[region_id]:
                        return False

        return True

    def select_next_cell(self):
        # Select the next cell to try (most constrained)
        best_cell = None
        min_choices = float('inf')
        max_constraints = -1

        for r in range(self.n):
            for c in range(self.n):
                if self.can_place_star(r, c):
                    # Calculate available choices in row, column, and region
                    available_in_row = sum(1 for cc in range(self.n) if self.can_place_star(r, cc))
                    available_in_col = sum(1 for rr in range(self.n) if self.can_place_star(rr, c))
                    rid = self.regions[r][c]
                    available_in_region = 0
                    if rid != self.unlabeled:
                        available_in_region = sum(1 for (rr, cc) in self.region_cells[rid] if self.can_place_star(rr, cc))

                    choices = available_in_row + available_in_col + available_in_region
                    constraints = len([1 for nr, nc in self.neighbors[(r, c)] if self.can_place_star(nr, nc)])

                    # Select cell with fewest choices and most constraints
                    if (choices < min_choices or
                            (choices == min_choices and constraints > max_constraints)):
                        min_choices = choices
                        max_constraints = constraints
                        best_cell = (r, c)

        return best_cell

    def is_complete(self):
        # Check if solution is complete
        return (all(x == 0 for x in self.rows_needed) and
                all(x == 0 for x in self.cols_needed) and
                all(x == 0 for x in self.regs_needed.values()))

    def is_impossible(self):
        # Check if current state is impossible
        for r in range(self.n):
            available = sum(1 for c in range(self.n) if self.can_place_star(r, c))
            if available < self.rows_needed[r]:
                return True

        for c in range(self.n):
            available = sum(1 for r in range(self.n) if self.can_place_star(r, c))
            if available < self.cols_needed[c]:
                return True

        for region_id, cells in self.region_cells.items():
            available = sum(1 for r, c in cells if self.can_place_star(r, c))
            if available < self.regs_needed[region_id]:
                return True

        return False

    def _restore_from_snapshot(self, snapshot):
        # Restore state from snapshot
        self.rows_needed = list(snapshot['rows_needed'])
        self.cols_needed = list(snapshot['cols_needed'])
        self.regs_needed = defaultdict(lambda: 0)
        self.regs_needed.update(snapshot['regs_needed'])
        self.forbidden_counts = defaultdict(int, snapshot['forbidden_counts'])
        self.solution = set(snapshot['solution'])

    def validate_no_adjacent(self):
        # Validate that no stars are adjacent
        for (r, c) in list(self.solution):
            for nr, nc in self.neighbors[(r, c)]:
                if (nr, nc) in self.solution:
                    return False, (r, c), (nr, nc)
        return True, None, None

    def backtrack(self, start_time, timeout):
        # Backtracking search with snapshot restoration
        self.nodes_visited += 1

        # Check timeout
        if time.time() - start_time > timeout:
            return False

        # Propagate constraints
        if not self.propagate_constraints():
            return False

        # Check if solution is complete
        if self.is_complete():
            return True

        # Check if current state is impossible
        if self.is_impossible():
            return False

        # Select next cell to try
        cell = self.select_next_cell()
        if not cell:
            return False

        r, c = cell

        # Take snapshot of current state
        snapshot = {
            'rows_needed': list(self.rows_needed),
            'cols_needed': list(self.cols_needed),
            'regs_needed': dict(self.regs_needed),
            'forbidden_counts': dict(self.forbidden_counts),
            'solution': set(self.solution)
        }

        # Try placing a star
        new_forbidden = self.place_star(r, c)
        if self.backtrack(start_time, timeout):
            return True
        self._restore_from_snapshot(snapshot)

        # Try not placing a star (mark as forbidden)
        self.forbidden_counts[(r, c)] += 1
        if self.backtrack(start_time, timeout):
            return True
        self.forbidden_counts[(r, c)] -= 1
        if self.forbidden_counts.get((r, c), 0) == 0:
            self.forbidden_counts.pop((r, c), None)

        self._restore_from_snapshot(snapshot)
        return False

    def solve(self, timeout=600):
        # Main solving method
        start_time = time.time()

        # Initial constraint propagation
        if not self.propagate_constraints():
            return None

        # Check if already solved
        if self.is_complete():
            ok, a, b = self.validate_no_adjacent()
            if not ok:
                print("Validation failed: adjacent stars", a, b)
                return None
            return self.solution

        # Check if impossible
        if self.is_impossible():
            return None

        # Start backtracking search
        if self.backtrack(start_time, timeout):
            ok, a, b = self.validate_no_adjacent()
            if not ok:
                print("Validation failed: adjacent stars", a, b)
                return None
            return self.solution

        return None


# Entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = StarBattleApp(root)
    root.mainloop()