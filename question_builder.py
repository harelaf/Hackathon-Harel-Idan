import random

class Question_Builder:
    
    def __init__(self):
        self.operator_functions = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b,
        }
        self.ans = ''
        self.eq = ''
    
    def normal_question():
        while len(str(self.ans)) != 1:        
            first_number = random.choice(range(0, 16))
            op1, op_func1 = random.choice(list(self.operator_functions.items()))
            second_number = random.choice(range(0, 16))
            op2, op_func2 = random.choice(list(self.operator_functions.items()))
            third_number = random.choice(range(0, 16))
            try:
                if op1 == '/' or op1 == '*':
                    self.ans = op_func2(op_func1(first_number, second_number), third_number) # (first */ second) +- third 
                    self.eq = f'({first_number} {op1} {second_number}) {op2} {third_number}'
                elif op2 == '/' or op2 == '*':
                    self.ans = op_func1(first_number, op_func2(second_number, third_number)) # first +- (second */ third)
                    self.eq = f'{first_number} {op1} ({second_number} {op2} {third_number})'
                else:
                    self.ans = op_func2(op_func1(first_number, second_number), third_number)
                    self.eq = f'{first_number} {op1} {second_number} {op2} {third_number}'
                
            except ZeroDivisionError:
                continue


    def linear_equation_question():

        while type(ans) != int:        
            first_number = random.choice(range(0, 10))
            op1, op_func1 = random.choice(list(self.operator_functions.items()))
            second_number = random.choice(range(0, 16))
            op2, op_func2 = random.choice(list(self.operator_functions.items()))
            third_number = random.choice(range(0, 16))
            try:
                if op1 == '/' or op1 == '*':
                    self.ans = op_func2(op_func1(first_number, second_number), third_number) # (first */ second) +- third 
                    self.eq = f'(X {op1} {second_number}) {op2} {third_number} = {ans}'
                elif op2 == '/' or op2 == '*':
                    self.ans = op_func1(first_number, op_func2(second_number, third_number)) # first +- (second */ third)
                    self.eq = f'X {op1} ({second_number} {op2} {third_number}) = {ans}'
                else:
                    self.ans = op_func2(op_func1(first_number, second_number), third_number)
                    self.eq = f'X {op1} {second_number} {op2} {third_number} = {ans}'
                
            except ZeroDivisionError:
                continue

        return first_number, eq


    def question_bank():
        
       # ans, eq = question_type_1(operator_functions, ans, eq)
        return ans, eq