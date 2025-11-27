from flask import Flask, render_template, request, redirect, url_for
from varasto import Varasto

app = Flask(__name__)

# In-memory storage for warehouses
warehouses = {}
warehouse_counter = 0


def get_next_id():
    global warehouse_counter
    warehouse_counter += 1
    return warehouse_counter


@app.route('/')
def index():
    """Display all warehouses."""
    return render_template('index.html', warehouses=warehouses)


@app.route('/warehouse/new', methods=['GET', 'POST'])
def new_warehouse():
    """Create a new warehouse."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        try:
            capacity = float(request.form.get('capacity', 0))
            initial_balance = float(request.form.get('initial_balance', 0))
        except ValueError:
            error = 'Invalid number format'
            return render_template('new_warehouse.html', error=error)

        if not name:
            error = 'Name is required'
            return render_template('new_warehouse.html', error=error)

        warehouse_id = get_next_id()
        warehouses[warehouse_id] = {
            'name': name,
            'varasto': Varasto(capacity, initial_balance),
            'warehouse_items': []
        }
        return redirect(url_for('index'))

    return render_template('new_warehouse.html')


@app.route('/warehouse/<int:warehouse_id>')
def view_warehouse(warehouse_id):
    """View a specific warehouse."""
    if warehouse_id not in warehouses:
        return redirect(url_for('index'))

    warehouse = warehouses[warehouse_id]
    return render_template('view_warehouse.html',
                           warehouse_id=warehouse_id,
                           warehouse=warehouse)


@app.route('/warehouse/<int:warehouse_id>/add', methods=['POST'])
def add_items(warehouse_id):
    """Add items to a warehouse."""
    if warehouse_id not in warehouses:
        return redirect(url_for('index'))

    item_name = request.form.get('item_name', '').strip()
    try:
        amount = float(request.form.get('amount', 0))
    except ValueError:
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    if amount > 0 and item_name:
        warehouses[warehouse_id]['varasto'].lisaa_varastoon(amount)
        warehouses[warehouse_id]['warehouse_items'].append({
            'name': item_name,
            'amount': amount
        })
    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/remove', methods=['POST'])
def remove_items(warehouse_id):
    """Remove items from a warehouse."""
    if warehouse_id not in warehouses:
        return redirect(url_for('index'))

    item_index = request.form.get('item_index')
    try:
        item_index = int(item_index)
    except (ValueError, TypeError):
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    items = warehouses[warehouse_id]['warehouse_items']
    if 0 <= item_index < len(items):
        item = items[item_index]
        warehouses[warehouse_id]['varasto'].ota_varastosta(item['amount'])
        items.pop(item_index)

    return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))


@app.route('/warehouse/<int:warehouse_id>/edit', methods=['GET', 'POST'])
def edit_warehouse(warehouse_id):
    """Edit warehouse name."""
    if warehouse_id not in warehouses:
        return redirect(url_for('index'))

    warehouse = warehouses[warehouse_id]

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            warehouse['name'] = name
        return redirect(url_for('view_warehouse', warehouse_id=warehouse_id))

    return render_template('edit_warehouse.html',
                           warehouse_id=warehouse_id,
                           warehouse=warehouse)


@app.route('/warehouse/<int:warehouse_id>/delete', methods=['POST'])
def delete_warehouse(warehouse_id):
    """Delete a warehouse."""
    if warehouse_id in warehouses:
        del warehouses[warehouse_id]
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
