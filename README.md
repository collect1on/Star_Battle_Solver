# Star Battle Solver


![Configuration Loaded Successfully](https://raw.githubusercontent.com/collect1on/Star_Battle_Solver/main/folder_for_picture_in_readme/configuration%20loaded%20successfully.png)

A comprehensive GUI application for solving Star Battle puzzles using constraint propagation and backtracking algorithms.

## Overview

Star Battle is a logic puzzle where players place stars on a grid according to three simple rules:
1. Each row must contain exactly k stars
2. Each column must contain exactly k stars  
3. Each region (colored area) must contain exactly k stars
4. Stars cannot be adjacent to each other, even diagonally

This application provides both a puzzle creator and solver with an intuitive graphical interface.

## Features

- **Interactive Puzzle Creation**: Visually define regions using a color-coded system
- **Advanced Solving Algorithm**: Hybrid approach combining constraint propagation with snapshot-based backtracking
- **Configurable Parameters**: Adjust board size (n×n) and number of stars per region/row/column (k)
- **Save/Load Functionality**: Persist puzzle configurations in JSON format
- **Real-time Feedback**: Visual display of solving progress and results
- **Validation System**: Ensures solutions adhere to all Star Battle rules

## Technical Implementation

### Core Algorithm

The solver uses a sophisticated hybrid approach:

1. **Constraint Propagation**: 
   - Forced placements based on row, column, and region constraints
   - Continuous propagation until no more deterministic moves are available

2. **Backtracking with Snapshots**:
   - State preservation using comprehensive snapshots
   - Most-constrained variable selection heuristic
   - Chronological backtracking with intelligent branch pruning

3. **Validation**:
   - Adjacency checking (8-directional)
   - Complete solution verification

### Key Data Structures

- **Region Mapping**: Matrix tracking cell-to-region relationships
- **Constraint Tracking**: Arrays for row, column, and region star requirements
- **Forbidden Counts**: Tracking cells excluded due to adjacent stars
- **Neighborhood Mapping**: Precomputed 8-directional adjacency relationships

## Execution Flow

1. **Initialization**: Parse input parameters and initialize constraint arrays
2. **Constraint Propagation**: 
   - Identify forced star placements
   - Update forbidden cells based on adjacency
   - Repeat until no more deterministic moves
3. **Backtracking Search**:
   - Select most constrained cell
   - Take snapshot of current state
   - Try placing star and recursively search
   - If failed, restore snapshot and mark cell as forbidden
4. **Validation**: Verify solution meets all constraints
5. **Output**: Return solution or indicate impossibility

## Usage Instructions

### Installation

```bash
# Requires Python 3.6+ with tkinter
# Install dependencies
pip install numpy
```

### Running the Application

```bash
python star_battle_solver.py
```

### Creating a Puzzle

1. Set board size (n) using the spinbox
2. Set number of stars (k) per row/column/region
3. Select a color from the palette
4. Click cells to assign them to the selected region
5. Ensure all regions are contiguous and appropriately sized

### Solving a Puzzle

1. Click "Solve" to initiate the solving process
2. Monitor progress in the status area
3. View the solution with stars marked by ★ symbols

### Saving and Loading

- Use "Save Config" to store puzzle definitions
- Use "Load Config" to retrieve previously saved puzzles
- Configurations are stored in JSON format

## File Format

Configuration files use the following JSON structure:
```json
{
  "n": 8,
  "k": 1,
  "regions": [[1, 1, 2, 2, ...], ...]
}
```

Where regions is a 2D array with integers representing region IDs (-1 for unmarked cells).


