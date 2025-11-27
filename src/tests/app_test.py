import unittest
import sys
import os

# Add src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app, warehouses, warehouse_counter


class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        """Set up test client and clear warehouses before each test."""
        app.testing = True
        self.client = app.test_client()
        warehouses.clear()
        global warehouse_counter
        # Reset the counter through the module
        import app as app_module
        app_module.warehouse_counter = 0

    def tearDown(self):
        """Clean up after each test."""
        warehouses.clear()

    def test_index_page_loads(self):
        """Test that the index page loads successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse Manager', response.data)

    def test_index_shows_no_warehouses_initially(self):
        """Test that the index shows message when no warehouses exist."""
        response = self.client.get('/')
        self.assertIn(b'No warehouses yet', response.data)

    def test_new_warehouse_page_loads(self):
        """Test that the new warehouse page loads successfully."""
        response = self.client.get('/warehouse/new')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create New Warehouse', response.data)

    def test_create_warehouse(self):
        """Test creating a new warehouse."""
        response = self.client.post('/warehouse/new', data={
            'name': 'Test Warehouse',
            'capacity': '100',
            'initial_balance': '10'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Warehouse', response.data)
        self.assertEqual(len(warehouses), 1)

    def test_create_warehouse_without_name(self):
        """Test creating a warehouse without a name shows error."""
        response = self.client.post('/warehouse/new', data={
            'name': '',
            'capacity': '100',
            'initial_balance': '0'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Name is required', response.data)
        self.assertEqual(len(warehouses), 0)

    def test_create_warehouse_invalid_capacity(self):
        """Test creating a warehouse with invalid capacity shows error."""
        response = self.client.post('/warehouse/new', data={
            'name': 'Test',
            'capacity': 'invalid',
            'initial_balance': '0'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid number format', response.data)
        self.assertEqual(len(warehouses), 0)

    def test_view_warehouse(self):
        """Test viewing a warehouse."""
        # Create a warehouse first
        self.client.post('/warehouse/new', data={
            'name': 'View Test',
            'capacity': '50',
            'initial_balance': '25'
        })

        response = self.client.get('/warehouse/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'View Test', response.data)
        self.assertIn(b'25', response.data)  # Balance
        self.assertIn(b'50', response.data)  # Capacity

    def test_view_nonexistent_warehouse_redirects(self):
        """Test viewing a nonexistent warehouse redirects to index."""
        response = self.client.get('/warehouse/999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse Manager', response.data)

    def test_add_items_to_warehouse(self):
        """Test adding items to a warehouse."""
        # Create a warehouse first
        self.client.post('/warehouse/new', data={
            'name': 'Add Test',
            'capacity': '100',
            'initial_balance': '0'
        })

        response = self.client.post('/warehouse/1/add', data={
            'amount': '30'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(warehouses[1]['varasto'].saldo, 30)

    def test_remove_items_from_warehouse(self):
        """Test removing items from a warehouse."""
        # Create a warehouse first
        self.client.post('/warehouse/new', data={
            'name': 'Remove Test',
            'capacity': '100',
            'initial_balance': '50'
        })

        response = self.client.post('/warehouse/1/remove', data={
            'amount': '20'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(warehouses[1]['varasto'].saldo, 30)

    def test_edit_warehouse_page_loads(self):
        """Test that the edit warehouse page loads."""
        # Create a warehouse first
        self.client.post('/warehouse/new', data={
            'name': 'Edit Test',
            'capacity': '100',
            'initial_balance': '0'
        })

        response = self.client.get('/warehouse/1/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Warehouse', response.data)
        self.assertIn(b'Edit Test', response.data)

    def test_edit_warehouse_name(self):
        """Test editing a warehouse name."""
        # Create a warehouse first
        self.client.post('/warehouse/new', data={
            'name': 'Original Name',
            'capacity': '100',
            'initial_balance': '0'
        })

        response = self.client.post('/warehouse/1/edit', data={
            'name': 'New Name'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(warehouses[1]['name'], 'New Name')

    def test_delete_warehouse(self):
        """Test deleting a warehouse."""
        # Create a warehouse first
        self.client.post('/warehouse/new', data={
            'name': 'Delete Test',
            'capacity': '100',
            'initial_balance': '0'
        })

        self.assertEqual(len(warehouses), 1)

        response = self.client.post('/warehouse/1/delete', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(warehouses), 0)

    def test_delete_nonexistent_warehouse(self):
        """Test deleting a nonexistent warehouse doesn't cause error."""
        response = self.client.post('/warehouse/999/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_add_items_to_nonexistent_warehouse(self):
        """Test adding items to nonexistent warehouse redirects."""
        response = self.client.post('/warehouse/999/add', data={
            'amount': '10'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse Manager', response.data)

    def test_remove_items_from_nonexistent_warehouse(self):
        """Test removing items from nonexistent warehouse redirects."""
        response = self.client.post('/warehouse/999/remove', data={
            'amount': '10'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse Manager', response.data)

    def test_multiple_warehouses(self):
        """Test creating and viewing multiple warehouses."""
        # Create two warehouses
        self.client.post('/warehouse/new', data={
            'name': 'Warehouse A',
            'capacity': '100',
            'initial_balance': '10'
        })

        self.client.post('/warehouse/new', data={
            'name': 'Warehouse B',
            'capacity': '200',
            'initial_balance': '50'
        })

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Warehouse A', response.data)
        self.assertIn(b'Warehouse B', response.data)
        self.assertEqual(len(warehouses), 2)


if __name__ == '__main__':
    unittest.main()
