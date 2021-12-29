import random


class QuestionBuilder:

    def _init_(self):
        self.all_operator_functions = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b,
        }
        self.plus_minus_functions = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
        }

    def get_numbers_and_ops(self, bound, ops):
        first_number = random.choice(range(0, bound))
        op1, op_func1 = random.choice(list(ops.items()))
        second_number = random.choice(range(0, 16))
        op2, op_func2 = random.choice(list(ops.items()))
        third_number = random.choice(range(0, 16))

        return first_number, op1, op_func1, second_number, op2, op_func2, third_number

    def normal_question(self):
        ans = ''
        eq = ''
        while len(str(ans)) != 1:
            first_number, op1, op_func1, second_number, op2, op_func2, third_number = self.get_numbers_and_ops(16,
                                                                                                               self.all_operator_functions)
            try:
                if op1 == '/' or op1 == '*':
                    ans = op_func2(op_func1(first_number, second_number), third_number)  # (first */ second) +- third
                    eq = f'({first_number} {op1} {second_number}) {op2} {third_number} ='
                elif op2 == '/' or op2 == '*':
                    ans = op_func1(first_number, op_func2(second_number, third_number))  # first +- (second */ third)
                    eq = f'{first_number} {op1} ({second_number} {op2} {third_number}) ='
                else:
                    ans = op_func2(op_func1(first_number, second_number), third_number)
                    eq = f'{first_number} {op1} {second_number} {op2} {third_number} ='

            except ZeroDivisionError:
                continue

        return ans, eq

    def linear_equation_question(self):
        first_number = 0
        ans = ''
        eq = ''
        while type(ans) != int:
            first_number, op1, op_func1, second_number, op2, op_func2, third_number = self.get_numbers_and_ops(10,
                                                                                                               self.all_operator_functions)
            try:
                if op1 == '/' or op1 == '*':
                    ans = op_func2(op_func1(first_number, second_number),
                                   third_number)  # (first */ second) +- third
                    eq = f'(X {op1} {second_number}) {op2} {third_number} = {ans}'
                elif op2 == '/' or op2 == '*':
                    ans = op_func1(first_number, op_func2(second_number, third_number))  # first +- (second */ third)
                    eq = f'X {op1} ({second_number} {op2} {third_number}) = {ans}'
                else:
                    ans = op_func2(op_func1(first_number, second_number), third_number)
                    eq = f'X {op1} {second_number} {op2} {third_number} = {ans}'

            except ZeroDivisionError:
                continue

        return first_number, eq

    def quadratic_equation_question(self):
        first_number, second_number, third_number = 0, 0, 0
        ans = ''
        eq = ''
        while type(ans) != int:
            first_number, op1, op_func1, second_number, op2, op_func2, third_number = self.get_numbers_and_ops(10,
                                                                                                               self.plus_minus_functions)
            try:
                ans = op_func2(op_func1(first_number ** 2, third_number * first_number), second_number)
                if third_number == 1:
                    eq = f'X^2 {op1} X {op2} {second_number} = {ans}'
                else:
                    eq = f'X^2 {op1} {third_number}X {op2} {second_number} = {ans}'

            except ZeroDivisionError:
                continue

            quadratic_formula = lambda a, b, c: (
            (-b + (b * 2 - 4 * a * c) * 0.5) / 2 * a, (-b - (b * 2 - 4 * a * c) * 0.5) / 2 * a)
            roots = quadratic_formula(1, op_func1(0, third_number), op_func2(0, second_number) - ans)

            if len(str(roots[0])) == 3 and len(str(roots[1])) == 3:
                ans = ''

        return first_number, eq

    def determinant_question(self):
        ans = ''
        mat = ''
        while len(str(ans)) != 1:
            a = random.choice(range(0, 10))
            b = random.choice(range(0, 10))
            c = random.choice(range(0, 10))
            d = random.choice(range(0, 10))

            ans = a * d - b * c
            mat = [[a, b], [c, d]]

        eq = f'determinant of \n{mat[0]}\n{mat[1]}'
        return ans, eq

    def get_question(self):
        prob = random.random()

        if prob <= 0.25:
            return self.normal_question()
        elif 0.25 < prob <= 0.5:
            return self.linear_equation_question()
        elif 0.5 < prob <= 0.75:
            return self.quadratic_equation_question()
        else:
            return self.determinant_question()
