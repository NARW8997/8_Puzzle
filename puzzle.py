from __future__ import division
from __future__ import print_function
from collections import deque

import resource
import heapq
import queue
import sys
import math
import time
import queue as Q


#### SKELETON CODE ####
## The Class that Represents the Puzzle
class PuzzleState(object):
    """
        The PuzzleState stores a board configuration and implements
        movement instructions to generate valid children.
    """

    def __init__(self, config, n, parent=None, action="Initial", cost=0):
        """
        :param config->List : Represents the n*n board, for e.g. [0,1,2,3,4,5,6,7,8] represents the goal state.
        :param n->int : Size of the board
        :param parent->PuzzleState
        :param action->string
        :param cost->int
        """
        if n * n != len(config) or n < 2:
            raise Exception("The length of config is not correct!")
        if set(config) != set(range(n * n)):
            raise Exception("Config contains invalid/duplicate entries : ", config)

        self.n = n
        self.cost = cost
        self.parent = parent
        self.action = action
        self.config = config
        self.children = []

        # Get the index and (row, col) of empty block
        self.blank_index = self.config.index(0)

    # def for heapq using
    def __lt__(self, other):
        self_cost = calculate_total_cost(self)
        other_cost = calculate_total_cost(other)
        if self_cost != other_cost:
            return self_cost < other_cost
        else:
            # if heuristic value is equal, we process as UDLR sequence
            action_map = {'Up': 0, 'Down': 1, 'Left': 2, 'Right': 3}
            return action_map[self.action] < action_map[other.action]

    def __key(self):
        return tuple(self.config)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, PuzzleState):
            return self.__key() == other.__key()
        return NotImplemented

    def display(self):
        """ Display this Puzzle state as a n*n board """
        for i in range(self.n):
            print(self.config[3 * i: 3 * (i + 1)])

    # swap the element in index i and j, return a new config
    def swap(self, i, j):
        new_config = list(self.config)
        temp = new_config[i]
        new_config[i] = new_config[j]
        new_config[j] = temp
        return new_config

    def move_up(self):
        """
        Moves the blank tile one row up.
        :return a PuzzleState with the new configuration
        """
        if self.blank_index > 2:
            return PuzzleState(self.swap(self.blank_index, self.blank_index - 3),
                                           self.n, self, "Up", self.cost + 1)
        else:
            return None

    def move_down(self):
        """
        Moves the blank tile one row down.
        :return a PuzzleState with the new configuration
        """
        if self.blank_index < 6:
            return PuzzleState(self.swap(self.blank_index, self.blank_index + 3),
                            self.n, self, "Down", self.cost + 1)
        else:
            return None

    def move_left(self):
        """
        Moves the blank tile one column to the left.
        :return a PuzzleState with the new configuration
        """
        if self.blank_index % 3 != 0:
            return PuzzleState(self.swap(self.blank_index, self.blank_index - 1),
                            self.n, self, "Left", self.cost + 1)
        else:
            return None

    def move_right(self):
        """
        Moves the blank tile one column to the right.
        :return a PuzzleState with the new configuration
        """
        if (self.blank_index + 1) % 3 != 0:
            return PuzzleState(self.swap(self.blank_index, self.blank_index + 1),
                            self.n, self, "Right", self.cost + 1)
        else:
            return None

    def expand(self):
        """ Generate the child nodes of this node """

        # Node has already been expanded
        if len(self.children) != 0:
            return self.children

        # Add child nodes in order of UDLR
        children = [
            self.move_up(),
            self.move_down(),
            self.move_left(),
            self.move_right()]

        # Compose self.children of all non-None children states
        self.children = [state for state in children if state is not None]
        return self.children

# Solver class to generate the final solution for output
# will be modified during the searching processs
class Solver():

    def __init__(self, frontier):
        #self.initial_state = initial_state
        self.frontier = frontier
        self.running_time = time.time()
        self.nodes_expanded = 0
        self.max_depth = 0
        self.explored = set()
        self.solution = None

    def puzzle_state_chain(self):
        current_state = self.solution
        result = [current_state]
        while not current_state.parent == None:
            result.append(current_state.parent)
            current_state = current_state.parent
        return result

    def build_path(self):
        paths = [node.action for node in self.puzzle_state_chain()[-2::-1]]
        return paths

    def solution_setter(self, state):
        self.solution = state
        self.nodes_expanded = len(self.explored) - len(self.frontier) - 1

# Function that Writes to output.txt

### Students need to change the method to have the corresponding parameters
def writeOutput(solverIns):
    ### Student Code Goes here
    file = open("output.txt", "w")

    file.write("path_to_goal: " + str(solverIns.build_path()) + "\n")
    file.write("cost_of_path: " + str(len(solverIns.build_path())) + "\n")
    file.write("nodes_expanded: " + str(solverIns.nodes_expanded) + "\n")
    file.write("search_depth: " + str(solverIns.solution.cost) + "\n")
    file.write("max_search_depth: " + str(solverIns.max_depth) + "\n")
    file.write("running_time: " + f'{(solverIns.running_time):.8f}' + "\n")
    file.write("max_ram_usage: " + f'{(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2 ** 20):.8f}')

    file.close()

def bfs_search(initial_state):
    """BFS search"""
    ### STUDENT CODE GOES HERE ###
    solverIns = Solver(deque())
    solverIns.frontier.append(initial_state)
    while not len(solverIns.frontier) == 0:
        # pop first
        # state is instaceOf PuzzleState
        state = solverIns.frontier.popleft()
        # add the node to the set of explored_tiles
        solverIns.explored.add(state)
        if test_goal(state):
            solverIns.solution_setter(state)
            break
        for neighbor in state.expand():
            if neighbor not in solverIns.explored:
                solverIns.frontier.append(neighbor)
                solverIns.explored.add(neighbor)
                solverIns.max_depth = max(solverIns.max_depth, neighbor.cost)
    solverIns.running_time = time.time() - solverIns.running_time
    return solverIns

def dfs_search(initial_state):
    """DFS search"""
    ### STUDENT CODE GOES HERE ###
    solverIns = Solver([])
    solverIns.frontier.append(initial_state)
    while not len(solverIns.frontier) == 0:
        state = solverIns.frontier.pop()
        solverIns.explored.add(state)
        if test_goal(state):
            solverIns.solution_setter(state)
            break
        for neighbor in state.expand()[::-1]:
            if neighbor not in solverIns.explored:
                solverIns.frontier.append(neighbor)
                solverIns.explored.add(neighbor)
                solverIns.max_depth = max(solverIns.max_depth, neighbor.cost)
    solverIns.running_time = time.time() - solverIns.running_time
    return solverIns

def A_star_search(initial_state):
    """A * search"""
    ### STUDENT CODE GOES HERE ###
    solverIns = Solver([])
    heapq.heappush(solverIns.frontier, initial_state)
    while not len(solverIns.frontier) == 0:
        state = heapq.heappop(solverIns.frontier)
        solverIns.explored.add(state)
        if test_goal(state):
            solverIns.solution_setter(state)
            break
        for neighbor in state.expand():
            if neighbor not in solverIns.explored:
                heapq.heappush(solverIns.frontier, neighbor)
                solverIns.explored.add(neighbor)
                solverIns.max_depth = max(solverIns.max_depth, neighbor.cost)
    solverIns.running_time = time.time() - solverIns.running_time
    return solverIns

def calculate_total_cost(state):
    """calculate the total estimated cost of a state"""
    ### STUDENT CODE GOES HERE ###
    # f(n) = g(n) + h(n) where g(n) is the current state's cost and
    # h(n) is the sum of manhattan distances heuristic.
    return state.cost + calculate_total_manhattan_dist(state)


def calculate_manhattan_dist(idx, value, n):
    """calculate the manhattan distance of a tile"""
    ### STUDENT CODE GOES HERE ###
    # value is at (idx // 3, idx % 3)
    # but it should be at (value // 3, value % 3)
    return abs(idx % 3 - value % 3) + abs(idx // 3 - value // 3)

# given a puzzle_state, calculate the total manhatten distance for it
def calculate_total_manhattan_dist(puzzle_state):
    total_manhatten = 0
    for i in range(9):
        if puzzle_state.config[i] == 0:
            continue
        total_manhatten += calculate_manhattan_dist(i, puzzle_state.config[i], puzzle_state.n)
    return total_manhatten

def test_goal(puzzle_state):
    """test the state is the goal state or not"""
    ### STUDENT CODE GOES HERE ###
    return puzzle_state.config == [0, 1, 2, 3, 4, 5, 6, 7, 8]


# Main Function that reads in Input and Runs corresponding Algorithm
def main():
    search_mode = sys.argv[1].lower()
    begin_state = sys.argv[2].split(",")
    begin_state = list(map(int, begin_state))
    board_size = int(math.sqrt(len(begin_state)))
    hard_state = PuzzleState(begin_state, board_size)
    start_time = time.time()

    if search_mode == "bfs":
        writeOutput(bfs_search(hard_state))
    elif search_mode == "dfs":
        writeOutput(dfs_search(hard_state))
    elif search_mode == "ast":
        writeOutput(A_star_search(hard_state))
    else:
        print("Enter valid command arguments !")

    end_time = time.time()
    print("Program completed in %.3f second(s)" % (end_time - start_time))


if __name__ == '__main__':
    main()