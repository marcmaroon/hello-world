import sys

def readstates(file):
    #parse file into states
    states = []
    with open(file, 'r') as file:
        for line in file:
            #skip end line
            if line == "END OF FILE":
                break
            line = line.strip()
            arr = line.split() 
            states.append(list(map(int, arr)))
    return states

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python expense_8_puzzle.py <start_file> <goal_file>")
        sys.exit(1)
    
    startfile = sys.argv[1]
    goalfile = sys.argv[2]
    start_states = readstates(startfile)
    goal_states = readstates(goalfile)
    print(f"Loaded {len(start_states)} states:")
    for state in start_states:
        print(state)