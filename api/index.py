from flask import Flask, request, render_template
import numpy as np
from scipy.optimize import nnls

app = Flask(__name__)

# Helper function to parse the chemical equation
def parse_equation(equation):
    # Split the equation into reactants and products
    reactants, products = equation.split('->')
    reactants = reactants.split('+')
    products = products.split('+')

    # Get a list of all unique elements in the equation
    elements = set(''.join(reactants + products))
    return reactants, products, elements

# Function to balance chemical equations
def balance_equation(equation):
    try:
        reactants, products, elements = parse_equation(equation)

        # Create a matrix to represent the atoms on each side of the equation
        atom_matrix = []
        for element in elements:
            atom_count = []
            # Count the atoms in reactants
            for compound in reactants:
                atom_count.append(compound.count(element))
            # Count the atoms in products (negated)
            for compound in products:
                atom_count.append(-compound.count(element))
            atom_matrix.append(atom_count)

        # Convert the list to a NumPy array
        atom_matrix = np.array(atom_matrix, dtype=float)

        # Use non-negative least squares to solve the system
        # The result should be close to zero for a balanced equation
        coefficients, _ = nnls(atom_matrix.T, np.zeros(len(elements)))

        # Find the smallest integer that can be multiplied to get whole numbers
        multiplier = np.lcm.reduce(np.array(coefficients * 1000000, dtype=int))
        balanced_coefficients = (coefficients * multiplier).astype(int)

        # Construct the balanced equation
        balanced_equation = ' + '.join([f'{coef} {comp}' for coef, comp in zip(balanced_coefficients[:len(reactants)], reactants)])
        balanced_equation += ' -> '
        balanced_equation += ' + '.join([f'{coef} {comp}' for coef, comp in zip(balanced_coefficients[len(reactants):], products)])

        return balanced_equation
    except Exception as e:
        # Handle any exceptions that occur during the balancing process
        return f"An error occurred while balancing the equation: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            equation = request.form['equation']
            balanced = balance_equation(equation)
            return render_template('index.html', balanced=balanced)
        return render_template('index.html', balanced=None)
    except Exception as e:
        # Handle any exceptions that occur during the request handling
        return render_template('error.html', error_message=str(e))
