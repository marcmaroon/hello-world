import sys
import heapq
from datetime import datetime
from collections import deque

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

#get possible successors from current state
def get_successors(state):
    successors = []
    row, col = find_blank(state)
    directions = {
        'up':    (row - 1, col, 'Down'),
        'down':  (row + 1, col, 'Up'),
        'left':  (row, col - 1, 'Right'),
        'right': (row, col + 1, 'Left'),
    }
    for blank_dir, (newrow, newcol, tile_dir) in directions.items():
        if 0 <= newrow < 3 and 0 <= newcol < 3:
            new_state = [row[:] for row in state]
            tile = new_state[newrow][newcol]
            new_state[row][col], new_state[newrow][newcol] = new_state[newrow][newcol], new_state[row][col]
            successors.append((new_state, tile, tile, tile_dir))
    return successors

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
        print(f"Solution Found at Depth {len(path) - 1} with cost of {totalcost}")
        print(f"Total Cost: {totalcost}")
        print("Steps:")
        for state,action,cost in path[1:]: # skip initial state
            print(f"\tMove {action}")
            
#summation of tile * manhattan distance
def heuristic(state, goal):
    #get end positions of each tile in goal state
    goalpos = {}
    for i in range(3):
        for j in range(3):
            goalpos[goal[i][j]] = (i, j)
            
    total = 0
    for i in range(3):
        for j in range(3):
            tile = state[i][j]
            #blanks are skipped
            if tile != 0:
                gi, gj = goalpos[tile]
                dist = abs(i - gi) + abs(j - gj)
                #tile x manhattan dist
                total += tile * dist
    return total
            
def bfs(start, goal, dump):
    #save states into tuples hashing/closed set
    starttuple = statetotuple(start)
    goaltuple = statetotuple(goal) 
    
    fringe = deque([(starttuple, [], 0)]) # (state, path, cost)
    closed = set()
    poppednodes = expandednodes = iteration = 0
    generatednodes = maxfringesize = 1
    
    while fringe:
        maxfringesize = max(maxfringesize, len(fringe))
        iteration += 1
        
        #dump fringe and closed set info to file
        fringedisplay = [(s, col) for s, _, col in fringe]
        dump.logiteration(iteration, fringedisplay, closed, expandednodes, generatednodes) 
        
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

def ucs(start, goal, dump):
    starttuple = statetotuple(start)
    goaltuple = statetotuple(goal)  
        
    #tie breaker
    counter = 0 
    fringe = [(0, counter, starttuple, [])] # (cost, counter, state, path)
    closed = {}
    poppednodes = expandednodes = iteration = 0
    generatednodes = maxfringesize = 1
    
    while fringe:
        maxfringesize = max(maxfringesize, len(fringe))
        iteration += 1
        
        #dump fringe and closed set info to file
        fringedisplay = [(s, col) for col, _, s, _ in fringe]
        dump.logiteration(iteration, fringedisplay, closed, expandednodes, generatednodes) 
        
        cost, _, statetuple, path = heapq.heappop(fringe)
        poppednodes += 1
        
        #skkip visited lower cost
        if statetuple in closed and closed[statetuple] <= cost:
            continue
        closed[statetuple] = cost
        
        if statetuple == goaltuple:
            return path, cost, poppednodes, expandednodes, generatednodes, maxfringesize
        
        expandednodes += 1
        
        #switch back to list for manipulation and get successors
        state = tupletostate(statetuple)
        for newstate, tile, movecost, direction in get_successors(state):
            newtuple = statetotuple(newstate)
            newcost = cost + movecost
            if newtuple not in closed or closed[newtuple] > newcost:
                generatednodes += 1
                counter += 1
                newpath = path + [(newstate, f"{tile} {direction}", movecost)]
                heapq.heappush(fringe, (newcost, counter, newtuple, newpath))
                            
    return None, 0, poppednodes, expandednodes, generatednodes, maxfringesize

def greedy(start, goal, dump):
    starttuple = statetotuple(start)
    goaltuple = statetotuple(goal)  
        
    #tie breaker
    counter = 0 
    fringe = [(heuristic(start, goal), counter, starttuple, [], 0)] # (heuristic, counter, state, path, cost)
    closed = set()
    poppednodes = expandednodes = iteration = 0
    generatednodes = maxfringesize = 1
    
    while fringe:
        maxfringesize = max(maxfringesize, len(fringe))
        iteration += 1
        
        #dump fringe and closed set info to file
        fringedisplay = [(s, f"h={h}") for h, _, s, _, _ in fringe]
        dump.logiteration(iteration, fringedisplay, closed, expandednodes, generatednodes) 
        
        hval, _, statetuple, path, cost = heapq.heappop(fringe)
        poppednodes += 1
        
        if statetuple in closed:
            continue
        closed.add(statetuple)
        
        if statetuple == goaltuple:
            return path, cost, poppednodes, expandednodes, generatednodes, maxfringesize
        
        expandednodes += 1
        
        state = tupletostate(statetuple)
        for newstate, tile, movecost, direction in get_successors(state):
            newtuple = statetotuple(newstate)
            if newtuple not in closed:
                generatednodes += 1
                counter += 1
                newpath = path + [(newstate, f"{tile} {direction}", movecost)]
                heapq.heappush(fringe, (heuristic(newstate, goal), counter, newtuple, newpath, cost + movecost))
                            
    return None, 0, poppednodes, expandednodes, generatednodes, maxfringesize

def astar(start, goal, dump):
    starttuple = statetotuple(start)
    goaltuple = statetotuple(goal)
    
    counter = 0
    fringe = [(heuristic(start, goal), counter, starttuple, [], 0)]
    closed = {}
    poppednodes = expandednodes = iteration = 0
    generatednodes = maxfringesize = 1
    
    while fringe:
        maxfringesize = max(maxfringesize, len(fringe))
        iteration += 1
        
        #dump fringe and closed set info to file
        fringedisplay = [(s, col) for _, col, s, _, _ in fringe]
        dump.logiteration(iteration, fringedisplay, closed, expandednodes, generatednodes) 
        
        _, _, statetuple, path, cost = heapq.heappop(fringe)
        poppednodes += 1
        
        if statetuple in closed and closed[statetuple] <= cost:
            continue
        closed[statetuple] = cost
        
        if statetuple == goaltuple:
            return path, cost, poppednodes, expandednodes, generatednodes, maxfringesize
        
        expandednodes += 1
        
        state = tupletostate(statetuple)
        for newstate, tile, movecost, direction in get_successors(state):
            newtuple = statetotuple(newstate)
            newcost = cost + movecost
            if newtuple not in closed or closed[newtuple] > newcost:
                generatednodes += 1
                counter += 1
                newpath = path + [(newstate, f"{tile} {direction}", movecost)]
                heapq.heappush(fringe, (newcost + heuristic(newstate, goal), counter, newtuple, newpath, newcost))
    
    return None, 0, poppednodes, expandednodes, generatednodes, maxfringesize
    


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python expense_8_puzzle.py <start_file> <goal_file>")
        sys.exit(1)
    
    startfile = sys.argv[1]
    goalfile = sys.argv[2]
    method = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] in methods else defaultmethod
    dumpflag = len(sys.argv) > 4 and sys.argv[4] in ['-d', '--dump']
    
    #check for valid method 
    if method not in methods:
        print(f"Invalid method. Choose from: {', '.join(methods)}")
        sys.exit(1)
    
    startstate = readstates(startfile)
    goalstate = readstates(goalfile)
    searchdump = Dump(dumpflag, method)
    
    print(f"Running: {method}")
    
    path = None
    totalcost = 0
    nodespopped = nodesexpanded = nodesgenerated = maxfringesize = 0
    
    if method == "bfs":
        path, totalcost, nodespopped, nodesexpanded, nodesgenerated, maxfringesize =  bfs(startstate, goalstate, searchdump)
    if method == "ucs":
        path, totalcost, nodespopped, nodesexpanded, nodesgenerated, maxfringesize =  ucs(startstate, goalstate, searchdump)
    if method == "greedy":
        path, totalcost, nodespopped, nodesexpanded, nodesgenerated, maxfringesize =  greedy(startstate, goalstate, searchdump)
    if method == "a*":
        path, totalcost, nodespopped, nodesexpanded, nodesgenerated, maxfringesize =  astar(startstate, goalstate, searchdump)
    
    printresult( path, totalcost, nodespopped, nodesexpanded, nodesgenerated, maxfringesize)
    
    if dumpflag:
        searchdump.writefile()