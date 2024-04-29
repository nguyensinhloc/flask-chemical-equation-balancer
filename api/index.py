from flask import Flask, request, render_template_string
from sympy import Eq, symbols, solve

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

    # Create symbols for coefficients
    coefficients = symbols(' '.join(['a{}'.format(i) for i in range(len(left) + len(right))]))

    # Create equations based on the element counts
    equations = []
    for element in elements:
        left_count = sum(coeff * compound.count(element) for coeff, compound in zip(coefficients[:len(left)], left))
        right_count = sum(coeff * compound.count(element) for coeff, compound in zip(coefficients[len(left):], right))
        equations.append(Eq(left_count, right_count))

    # Solve the equations
    solution = solve(equations, coefficients)

    # If no solution, return the original equation
    if not solution:
        return "Cannot balance the equation."

    # Generate the balanced equation
    balanced_left = ' + '.join('{}{}'.format(solution[coeff], compound) for coeff, compound in zip(coefficients[:len(left)], left))
    balanced_right = ' + '.join('{}{}'.format(solution[coeff], compound) for coeff, compound in zip(coefficients[len(left):], right))
    balanced_equation = '{} = {}'.format(balanced_left, balanced_right)

    return balanced_equation

if __name__ == '__main__':
    app.run()
