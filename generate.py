from sudoku import *
from thread import Threads
from copy import *

class SudokuCreater():

    def __init__(self, sudoku):
        self.sudoku= sudoku
        dom= ['1','2','3','4','5','6','7','8','9']
        self.constraints= self.sudoku.board_constraints()
        self.domain= dict()
        # all unassigned variables in the board have a domain [1,9]
        for var in self.sudoku.variables:
            if(self.sudoku.structure[var.i][var.j]=='0'):
                self.domain[var]= deepcopy(dom)
            else:
                self.domain[var]= list(self.sudoku.structure[var.i][var.j])



    def solve(self):
        # we'll enforce node consistency through the GUI part
        self.ac3()
        return self.backtrack(dict())
    

    def domain_update(self,X_value, Y):
        """
        revise function will call this function to check if X_value is chosen as a value for variable X, does that leave any option for Y?
        """
        for Y_value in self.domain[Y]:
            if Y_value != X_value:
                return True

        return False

    def revise(self, X, Y):
        """
        makes X arc consistent wrt to Y
        """
        revised= False
            #if a value in X's domain doesn't leave any option for Y, remove that value from X's domain
        threads= []
        for X_value in self.domain[X]:
            threads.append(Threads(target= self.domain_update, args=(X_value,Y)))

        for thread in threads:
            thread.start()

        for thread in threads:
            if(thread.join()== False):
                self.domain[X].remove(thread.args()[0])
                revised= True
        return revised
     
    def add_arcs(self,variable):
        # adds arc wrt to variable
        arcs=[]
        for constraint in self.constraints[variable]:
            arcs.append((variable, constraint))
        return arcs

    def initial_arcs(self):
        threads=[]
        arcs=[]
        for var in self.sudoku.variables:
            threads.append(Threads(target= self.add_arcs, args=(var,))) 
        for thread in threads:
            thread.start()
        for thread in threads:
            arcs+= thread.join()
        return arcs

    

    def ac3(self, arcs= None):
        if arcs== None:
            arcs= self.initial_arcs()

        while(len(arcs)!=0):
            arc= arcs.pop()
            X= arc[0]
            Y= arc[1]
            if self.revise(X,Y):
                #if revision emptied the domain of X, there's no solution
                if(len(self.domain[X]) == 0):
                    return False
                threads=[]
                for constraint in self.constraints[X]:
                    if constraint == Y:
                        continue
                    else:
                        threads.append(Threads(target= self.revise, args= (constraint, X)))

                for thread in threads:
                    thread.start()

                for thread in threads:
                    if(thread.join()):
                        if(len(self.domain[thread.args()[0]]) ==0):
                            return False

        return True       

                        
    def assignment_complete(self, assignment):
        return len(assignment) == len(self.sudoku.variables)

    def is_constraint_consistent(self, constraint, assignment, assigned):
        """
        will be called by  is_consistent function to check if constraint is assigned or not
        and if it is assigned, it's assignment should not be equal to assigned
        """
        if constraint in assignment:
            if assignment[constraint] == assigned:
                return False
        return True
    def is_consistent(self, assignment, var, assigned):
        """
        checks if var= assigned is consistent with the assignment done so far
        """
        threads= []

        for constraint in self.constraints[var]:
            threads.append(Threads(target= self.is_constraint_consistent, args= (constraint, assignment, assigned)))

        for thread in threads:
            thread.start()

        for thread in threads:
            if(thread.join()== False):
                return False
        return True

    def values_left_in_domain(self,variable):
        """
        returns no. of values left in the domain of the variable
        """
        return len(self.domain[variable])

    def select_unassigned_variable(self, assignment):
        """
        We'll choose the variable that has least possible values left in it's domain
        """
        threads=[]
        domain_values= dict()
        for variable in self.sudoku.variables:
            if variable not in assignment:
                threads.append(Threads(target= self.values_left_in_domain, args=(variable,)))
        for thread in threads:
            thread.start()

        for thread in threads:
            domain_values[thread.args()[0]] = thread.join()

        return sorted(domain_values, key= domain_values.get)[0]

    def no_of_constraints(self, value, assignment, var):
        """
        will be called by order_domain_values function to count the no. of contraints var= value puts on the neighnours of var
        """
        count =0
        for constraint in self.constraints[var]:
            if value in self.domain[constraint]:
                count+=1

        return count

    def order_domain_values(self, assignment, var):
        """
        orders the domain of the variable var according to the constraints it puts on it's neighbours
        """
        number_constrained= dict()
        threads= []
        for value in self.domain[var]:
            threads.append(Threads(target= self.no_of_constraints, args= (value, assignment, var)))
        for thread in threads:
            thread.start()

        for thread in threads:
            number_constrained[thread.args()[0]] = thread.join()
        return sorted(number_constrained, key= number_constrained.get)

    def backtrack(self, assignment):
        if self.assignment_complete(assignment):
            return assignment
        var= self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(assignment, var):
            if self.is_consistent(assignment, var, value):
                assignment[var]= value
                #makes inferences from new assignment with ac3
                arcs= [(constraint, var) for constraint in self.constraints[var] 
                        if constraint not in assignment]
                #make a copy of domains before calling ac3 so that changes to domains can be reverted if needed
                t1= Threads(target= deepcopy, args= (self.domain,))
                t1.start()
                if self.ac3(arcs= arcs):
                    result = self.backtrack(assignment)
                    if result != None:
                        return result
                assignment[var].remove(value)
                self.domains= t1.join()
        return None
    
    def print_assignment(self, assignment):
        for i in range(len(self.sudoku.structure)):
            if i%3==0 and i!=0:
                print("- - - - - - - -")

            for j in range(len(self.sudoku.structure[i])):
                if j%3==0 and j!=0:
                    print(" | ", end="")
                if j==8:
                    if(self.sudoku.structure[i][j]=='0'):
                        print(assignment[Variable(i=i, j=j)])
                    else:
                        print(self.sudoku.structure[i][j])
                else:
                    if(self.sudoku.structure[i][j]=='0'):
                        print(str(assignment[Variable(i=i, j=j)]) + " ", end= "" )
                    else:
                        print(str(self.sudoku.structure[i][j]) + " " , end="")


def main():
    sudoku= Sudoku("problems/5.txt")
    
    creator= SudokuCreater(sudoku)
    assignment= creator.solve()
    creator.print_assignment(assignment)

    print(assignment[Variable(0,0)])
    

if __name__ == "__main__":
    main()

