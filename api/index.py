import base64
import io

import matplotlib.pyplot as plt
from chempy import balance_stoichiometry
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Define a function to balance a chemical equation
def balance_chemical_equation(reactants, products):
    if not reactants or not products:
        return "Error: At least one reactant and one product needed. Please ensure all reactants and products are correctly entered."
    try:
        # Balance the stoichiometry
        balanced_reactants, balanced_products = balance_stoichiometry(reactants, products)
        # Return the balanced equation
        return balanced_reactants, balanced_products
    except Exception as e:
        # Handle the case where reactants or products are missing
        return f"Error: {str(e)}. Please ensure all reactants and products are correctly entered."

# Define a function to visualize the chemical equation
def visualize_chemical_equation(balanced_reactants, balanced_products):
    # Combine the reactants and products
    all_chemicals = list(balanced_reactants.keys()) + list(balanced_products.keys())
    stoichiometric_coefficients = list(balanced_reactants.values()) + list(balanced_products.values())

    # Create a bar chart
    plt.bar(all_chemicals, stoichiometric_coefficients, color='blue')
    plt.xlabel('Chemicals')
    plt.ylabel('Stoichiometric Coefficients')
    plt.title('Visualization of Chemical Reaction Stoichiometry')

    # Save the chart as a PNG image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return plot_url

@app.route('/', methods=['GET', 'POST'])
def balance_equation():
    if request.method == 'POST':
        reactants = set(request.form['reactants'].split())
        products = set(request.form['products'].split())
        result = balance_chemical_equation(reactants, products)
        if isinstance(result, tuple):
            balanced_reactants, balanced_products = result
            visualization = visualize_chemical_equation(balanced_reactants, balanced_products)
            return render_template_string("""
                <!DOCTYPE html>
                <html>
                  <head>
                    <title>Chemical Equation Balancer</title>
                  </head>
                  <body>
                    <h1>Chemical Equation Balancer</h1>
                    <form action="" method="post">
                      <label for="reactants">Reactants:</label>
                      <input type="text" id="reactants" name="reactants"><br><br>
                      <label for="products">Products:</label>
                      <input type="text" id="products" name="products"><br><br>
                      <input type="submit" value="Balance Equation">
                    </form>
                    {% if balanced_reactants %}
                      <h2>Balanced Reactants: {{ balanced_reactants }}</h2>
                      <h2>Balanced Products: {{ balanced_products }}</h2>
                      <img src="data:image/png;base64,{{ visualization }}" alt="Chemical Equation Stoichiometry">
                    {% elif error %}
                      <p>{{ error }}</p>
                    {% endif %}
                  </body>
                </html>
            """, balanced_reactants=balanced_reactants, balanced_products=balanced_products, visualization=visualization)
        else:
            return render_template_string("""
                <!DOCTYPE html>
                <html>
                  <head>
                    <title>Chemical Equation Balancer</title>
                  </head>
                  <body>
                    <h1>Chemical Equation Balancer</h1>
                    <form action="" method="post">
                      <label for="reactants">Reactants:</label>
                      <input type="text" id="reactants" name="reactants"><br><br>
                      <label for="products">Products:</label>
                      <input type="text" id="products" name="products"><br><br>
                      <input type="submit" value="Balance Equation">
                    </form>
                    <p>{{ error }}</p>
                  </body>
                </html>
            """, error=result)
    return render_template_string("""
        <!DOCTYPE html>
        <html>
          <head>
            <title>Chemical Equation Balancer</title>
          </head>
          <body>
            <h1>Chemical Equation Balancer</h1>
            <form action="" method="post">
              <label for="reactants">Reactants:</label>
              <input type="text" id="reactants" name="reactants"><br><br>
              <label for="products">Products:</label>
              <input type="text" id="products" name="products"><br><br>
              <input type="submit" value="Balance Equation">
            </form>
          </body>
        </html>
    """)
