import os      

def calcexpr(expression):
    # create a stack 
    stack = []
    # char stack
    arr = expression.split()
    
    for char in arr:
        if char.isdigit():
            stack.append(float(char))
        else:
            y = stack.pop()
            x = stack.pop()
            
            if char == '+':
                result = x + y
            if char == '-':
                result = x - y
            if char == '*':
                result = x*y
            if char == '/':
                result = x/y
            
            stack.append(result)
            
    return (stack[0])

if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(__file__))
    RPNfile = os.path.join(currentdir, "inputRPN.txt")
    
    # open file 
    with open(RPNfile, "r") as file:
        # readlines
        lines = file.readlines()
        
        for line in lines:
            total = calcexpr(line.strip())
            print(total)
            
            
    
    
    