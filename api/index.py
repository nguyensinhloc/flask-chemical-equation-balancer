from flask import Flask, request, render_template_string
from sympy import Eq, symbols, solve, Integer

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chemical Equation Balancer</title>
</head>
<body>
    <h1>Chemical Equation Balancer</h1>
    <form method="POST">
        <input type="text" name="equation" placeholder="H2 + O2 = H2O" required>
        <button type="submit">Balance</button>
    </form>
    {% if result %}
        <h2>Result: {{ result }}</h2>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def balance_equation():
    result = None
    if request.method == 'POST':
        equation_input = request.form['equation']
        result = balance_chemical_equation(equation_input)
    return render_template_string(HTML_PAGE, result=result)

def balance_chemical_equation(equation):
    # Split the equation into left and right parts
    left, right = equation.split('=')
    left = left.split('+')
    right = right.split('+')

    # Extract all unique elements
    elements = set(''.join(filter(str.isalpha, char)) for char in equation)

    # Create symbols for coefficients with integer assumption
    coefficients = symbols(' '.join(['a{}'.format(i) for i in range(len(left) + len(right))]), integer=True)

    # Create equations based on the element counts
    equations = []
    for element in elements:
        left_count = 0
        right_count = 0
        for i, compound in enumerate(left):
            count = compound.count(element)
            if count > 0:
                left_count += coefficients[i] * count
        for i, compound in enumerate(right):
            count = compound.count(element)
            if count > 0:
                right_count += coefficients[len(left) + i] * count
        equations.append(Eq(left_count, right_count))

    # Add the condition that all coefficients are greater than zero
    positive_solution = solve(equations, coefficients, dict=True)
    positive_solution = [sol for sol in positive_solution if all(coeff > 0 for coeff in sol.values())]

    # If no positive integer solution, return the original equation
    if not positive_solution:
        return "Cannot balance the equation."

    # Use the first positive solution
    solution = positive_solution[0]

    # Generate the balanced equation
    balanced_left = ' + '.join('{}{}'.format(int(solution[coeff]), compound) for coeff, compound in zip(coefficients[:len(left)], left))
    balanced_right = ' + '.join('{}{}'.format(int(solution[coeff]), compound) for coeff, compound in zip(coefficients[len(left):], right))
    balanced_equation = '{} = {}'.format(balanced_left, balanced_right)

    return balanced_equation

if __name__ == '__main__':
    app.run()
