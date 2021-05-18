from thread import Threads

#A variable is any unfilled position on the board
class Variable():
    def __init__(self, i, j):
        self.i= i
        self.j= j

    def __hash__(self):
        return hash((self.i, self.j))
    
    def __str__(self):
        return f"{(self.i, self.j)}"

    def __eq__(self, other):
        return (self.i == other.i and self.j == other.j)


class Sudoku():
    def __init__(self, structure_file):
        with open(structure_file) as f:
            contents= f.read().splitlines()
            self.structure = []
            for row in contents:
                self.structure.append(list(row))

        self.variables=[]
        for l in range(9):
            for m in range(9):
                self.variables.append(Variable(i=l, j=m))

    def print_board(self):
        for i in range(len(self.structure)):
            if i%3==0 and i!=0:
                print("- - - - - - - - -")

            for j in range(len(self.structure[i])):
                if j%3 ==0 and j!=0:
                    print(" | ", end= "")
                if j==8:
                    print(self.structure[i][j])
                else:
                    print(str(self.structure[i][j]) + " " , end= "")
    
    def row_constraints(self, i, j):
        """
        row constraints for a variable express the idea that the variable's value cannot be equal
        to any other element in that row
        """

        constraints= []
        for k in range(9):
            if k!=j:
                constraints.append(Variable(i,k)) 
        return constraints


    def column_constraints(self, i, j):
        """
        column_constraints for a variable express the idea that the variable's value cannot be equal 
        to any other element in that column_j
        """
        constraints= []
        for k in range(9):
            if k!=i:
                constraints.append(Variable(k,j)) 
        return constraints

    def box_constraints(self, i, j):
        """
        box contraints for a variable express the idea that the variable's value cannot be equal 
        to any other element in that box
        """
        box_x= i//3
        box_y= j//3

        constraints= []

        for l in range(box_x*3, 3*(box_x+1)):
            for m in range(box_y*3, 3*(box_y +1)):
                if(l!= i and m!=j): 
                    constraints.append(Variable(l,m)) 
        return constraints

    def variable_constraints(self, variable):
        constraints= []
        i= variable.i
        j= variable.j

        t1= Threads(target= self.row_constraints, args= (i,j))
        t2= Threads(target= self.column_constraints, args= (i,j))
        t3= Threads(target= self.box_constraints, args= (i,j))

        t1.start()
        t2.start()
        t3.start()

        constraints= t1.join() + t2.join() + t3.join()

        return constraints


    def board_constraints(self):
        """
        Add contraints for each of the variables and put in contraints dictionary
        """
        threads= []
        constraints= dict()
        for variable in self.variables:
            threads.append(Threads(target= self.variable_constraints, args= (variable,)))

        for thread in threads:
            thread.start()

        for thread in threads:
            variable= thread.args()[0]
            constraints[variable]= thread.join()
        return constraints
