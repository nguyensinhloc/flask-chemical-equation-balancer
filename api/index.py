from flask import Flask, request, render_template_string
from sympy import Eq, symbols, solve, Integer
import re

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
        try:
            result = balance_chemical_equation(equation_input)
        except ValueError as e:
            result = "Error: " + str(e)
    return render_template_string(HTML_PAGE, result=result)

def balance_chemical_equation(equation):
    # Validate input equation
    if '=' not in equation:
        raise ValueError("Invalid equation format. Please use 'A + B = C + D' format.")
    left, right = equation.split('=')
    left = left.split('+')
    right = right.split('+')

    # Extract all unique elements
    elements = set(re.findall(r'([A-Z][a-z]?)(\d*)', equation))

    # Create symbols for coefficients with positive integer assumption
    coefficients = symbols(' '.join(['a{}'.format(i) for i in range(len(left) + len(right))]), positive=True)

    # Create equations based on the element counts
    equations = []
    for element, _ in elements:
        left_count = sum(coefficients[i] * int(count or 1) for i, compound in enumerate(left) for el, count in re.findall(r'([A-Z][a-z]?)(\d*)', compound) if el == element)
        right_count = sum(coefficients[len(left) + i] * int(count or 1) for i, compound in enumerate(right) for el, count in re.findall(r'([A-Z][a-z]?)(\d*)', compound) if el == element)
        equations.append(Eq(left_count, right_count))

    # Solve the equations
    solutions = solve(equations, coefficients, dict=True)
    if not solutions:
        raise ValueError("Cannot balance the equation.")

    # Use the first positive solution
    solution = solutions[0]

    # Generate the balanced equation
    balanced_left = ' + '.join('{}{}'.format(solution[coeff] if solution[coeff] != 1 else '', compound) for coeff, compound in zip(coefficients[:len(left)], left))
    balanced_right = ' + '.join('{}{}'.format(solution[coeff] if solution[coeff] != 1 else '', compound) for coeff, compound in zip(coefficients[len(left):], right))
    balanced_equation = '{} = {}'.format(balanced_left, balanced_right)

    return balanced_equation


if __name__ == '__main__':
    app.run()
