import sys

methods = ["bfs", "ucs", "greedy", "a*"]

defaultmethod = "a*"


def readstates(file):
    #parse file into states
    states = []
    with open(file, 'r') as file:
        for line in file:
            #skip end line
            line = line.strip()
            if line == "END OF FILE":
                break
            arr = line.split() 
            states.append([int(x) for x in arr])
    return states

#turn states into tuples for hashing
def statetotuple(state):
    return tuple(tuple(row) for row in state)

#turn tuples back into states for manipulation
def tupletostate(tuple):
    return [list(row) for row in tuple]

def find_blank(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

#get possible moves from current state
def get_successors(state):
    """Returns list of (new_state, moved_tile, cost, direction)
    Direction = the direction the TILE moves (opposite to blank)"""
    moves = []
    r, c = find_blank(state)
    # key = blank moves this way, value = tile moves opposite way
    directions = {
        'up':    (r - 1, c, 'Down'),
        'down':  (r + 1, c, 'Up'),
        'left':  (r, c - 1, 'Right'),
        'right': (r, c + 1, 'Left'),
    }
    for blank_dir, (nr, nc, tile_dir) in directions.items():
        if 0 <= nr < 3 and 0 <= nc < 3:
            new_state = [row[:] for row in state]
            tile = new_state[nr][nc]
            new_state[r][c], new_state[nr][nc] = new_state[nr][nc], new_state[r][c]
            moves.append((new_state, tile, tile, tile_dir))
    return moves

def print_state(state):
    for row in state:
        print(' '.join(str(x) for x in row))



#class for dump search results to file
class Dump:
    def __init__(self, flag, method):
        #flag to determine if dumping is enabled, list  to store lines from iterations
        self.flag = flag
        self.method = method 
        self.lines = []
        if flag:
            #if dumping is enabled create file with timestamp,method, and header info
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d-%H%M")
            self.filename = f"trace-{timestamp}.txt"
            self._header()
    
    #write header to dump file
    def _header(self):
        #add lines to list
        self.lines.append(f" {sys.argv[1]}, {sys.argv[2]}, {sys.argv[3]}, {sys.argv[4]} \n\n")
    
    def logiteration(self, iteration, fringe, closed, expandednodes, generatednodes):
        if not self.flag:
            return
        #log iteration details to list
        self.lines.append(f"Iteration: {iteration}")
        self.lines.append(f"Nodes Expanded: {expandednodes}")
        self.lines.append(f"Nodes Generated: {generatednodes}")   
        
        self.lines.append(f"Closed: ")
        for n in closed:
            self.lines.append(f"  {n}")
            
        self.lines.append(f"Fringe: ")
        for state in fringe:
            self.lines.append(f"  {state}")
            
    def writefile(self):
        if not self.flag:
            return
        with open(self.filename, 'w') as file:
            file.write('\n'.join(self.lines))
            
def printresult(path, totalcost, poppednodes, expandednodes, generatednodes, maxfringesize):
    print(f"Nodes Popped: {poppednodes}")
    print(f"Nodes Expanded: {expandednodes}")
    print(f"Nodes Generated: {generatednodes}")
    print(f"Maximum Fringe Size: {maxfringesize}")
    if path is None:
        print("No solution found.")
        return
    else:
        print(f"Solution Found at Depth {len(path)} with cost of {totalcost}")
        print(f"Total Cost: {totalcost}")
        print("Steps:")
        for state,action,cost in path[1:]: # skip initial state
            print(f"\tMove {action}")
            
def bfs(start, goal, dump):
    #save states into tuples hashing/closed set
    starttuple = statetotuple(start)
    goaltuple = statetotuple(goal) 
    
    from collections import deque
    fringe = deque([(starttuple, [], 0)]) # (state, path, cost)
    closed = set()
    poppednodes = expandednodes = iteration = 0
    generatednodes = maxfringesize = 1
    
    while fringe:
        maxfringesize = max(maxfringesize, len(fringe))
        iteration += 1
        
        #dump fringe and closed set info to file
        fringe_display = [(s, c) for s, _, c in fringe]
        dump.logiteration(iteration, fringe_display, closed, expandednodes, generatednodes) 
        
        
        statetuple, path, cost = fringe.popleft()
        poppednodes += 1
        
        #add start state to closed set and check if goal is reached
        if statetuple in closed:
            continue
        closed.add(statetuple)
        
        if statetuple == goaltuple:
            return path, cost, poppednodes, expandednodes, generatednodes, maxfringesize
        
        expandednodes += 1
        
        # return start back to list for manipulation and get successors
        state = tupletostate(statetuple)
        for newstate, tile, movecost, direction in get_successors(state):
            newtuple = statetotuple(newstate)
            if newtuple not in closed:
                generatednodes += 1
                newpath = path + [(newstate, f"{tile} {direction}", movecost)]
                fringe.append((newtuple, newpath, cost + movecost))
    
    return None, 0, poppednodes, expandednodes, generatednodes, maxfringesize      
        
    


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python expense_8_puzzle.py <start_file> <goal_file>")
        sys.exit(1)
    
    startfile = sys.argv[1]
    goalfile = sys.argv[2]
    method = sys.argv[3] if len(sys.argv) > 3 else 'a*'
    dumpflag = len(sys.argv) > 4 and sys.argv[4] in ['-d', '--dump']
    
    #check for valid method 
    if method not in methods:
        print(f"Invalid method. Choose from: {', '.join(methods)}")
        sys.exit(1)
    
    startstate = readstates(startfile)
    goalstate = readstates(goalfile)
    searchdump = Dump(dumpflag, method)
    
    print(f"\nStart State:")
    print_state(startstate)
    print(f"\nGoal State:")
    print_state(goalstate)
    print(f"\nRunning: {method.upper()}")
    print("-" * 40)
    
    path = None
    totalcost = 0
    nodespopped = nodesexpanded = nodesgenerated = maxfringesize = 0
    
    if method == "bfs":
        path, totalcost, nodespopped, nodesexpanded, nodesgenerated, maxfringesize = \
            bfs(startstate, goalstate, searchdump)
    
    printresult( path, totalcost, nodespopped, nodesexpanded, nodesgenerated, maxfringesize)
    
    searchdump.writefile()