import sys
from crossword import *


class CrosswordCreator:
    def __init__(self, crossword):
        """
        Create new CSP crossword generator.
        Initializes the domains for each variable to the full word list.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D list representing a given assignment.
        Each cell is a letter if assigned or None.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            for k in range(len(word)):
                i = variable.i + (k if variable.direction == Variable.DOWN else 0)
                j = variable.j + (k if variable.direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    # Print letter or blank space if no letter yet.
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create blank canvas.
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j],
                            fill="black",
                            font=font
                        )
        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, then solve the CSP.
        Returns a complete assignment if a solution exists, otherwise None.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update self.domains so that each variable is node-consistent.
        Remove from a variable's domain any words whose length does not match the variable's length.
        """
        for var in self.domains:
            self.domains[var] = {word for word in self.domains[var] if len(word) == var.length}

    def revise(self, x, y):
        """
        Make variable x arc-consistent with variable y.
        Remove values from domains[x] for which there is no possible corresponding value in domains[y]
        that satisfies the overlap constraint.
        Return True if a revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps.get((x, y))
        if overlap is None:
            return False
        i, j = overlap
        to_remove = set()
        for word in self.domains[x]:
            # For each word in x's domain, check if there is any word in y's domain 
            # where the letters at the overlapping indices match.
            if not any(word[i] == other[j] for other in self.domains[y]):
                to_remove.add(word)
        if to_remove:
            self.domains[x] -= to_remove
            revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Enforce arc consistency in the CSP.
        If arcs is None, begin with all arcs; otherwise, use the provided list.
        Return True if arc consistency was enforced without emptying any domain. 
        Return False if any domain becomes empty.
        """
        if arcs is None:
            arcs = [(x, y) for x in self.domains for y in self.crossword.neighbors(x)]
        queue = list(arcs)
        while queue:
            (x, y) = queue.pop(0)
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if assignment is complete (every variable is assigned a word).
        """
        return set(assignment.keys()) == self.crossword.variables

    def consistent(self, assignment):
        """
        Check if an assignment is consistent:
          - All words are distinct.
          - All words match the variable lengths.
          - Overlapping letters between variables are consistent.
        """
        # All assigned words should be distinct.
        if len(set(assignment.values())) < len(assignment):
            return False
        for var in assignment:
            word = assignment[var]
            if len(word) != var.length:
                return False
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps.get((var, neighbor))
                    if overlap:
                        i, j = overlap
                        if word[i] != assignment[neighbor][j]:
                            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return the list of domain values for var, ordered by the number of values they rule out for neighbor variables.
        The least constraining value is returned first.
        """
        def count_conflicts(value):
            count = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    overlap = self.crossword.overlaps.get((var, neighbor))
                    if overlap:
                        i, j = overlap
                        for neighbor_word in self.domains[neighbor]:
                            if value[i] != neighbor_word[j]:
                                count += 1
            return count

        return sorted(self.domains[var], key=count_conflicts)

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable using the Minimum Remaining Values (MRV) heuristic.
        If there is a tie, use the degree heuristic (variable with the most neighbors).
        """
        unassigned = [v for v in self.crossword.variables if v not in assignment]
        # Sort by domain size (MRV) then by negative degree (to maximize neighbor count)
        unassigned.sort(key=lambda var: (len(self.domains[var]), -len(self.crossword.neighbors(var))))
        return unassigned[0] if unassigned else None

    def backtrack(self, assignment):
        """
        Perform backtracking search to find a complete assignment.
        If successful, return the complete assignment; otherwise, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        return None


def main():
    # Check usage.
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Create the crossword puzzle from the structure and words files.
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print the result if a solution is found.
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
