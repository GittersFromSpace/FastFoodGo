"""Unit tests for the FastFood API."""

import pytest
import json
from src.api import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'service' in data


def test_calculate_order_success(client):
    """Test successful order calculation."""
    payload = {
        'items': [
            {'product_name': 'Burger', 'quantity': 2, 'unit_price': 9.99},
            {'product_name': 'Fries', 'quantity': 1, 'unit_price': 3.50}
        ],
        'tax_rate': 0.20
    }
    
    response = client.post(
        '/api/orders/calculate',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total' in data
    assert 'subtotal' in data
    assert 'tax' in data
    assert data['subtotal'] == 23.48
    assert data['tax'] == 4.70
    assert data['total'] == 28.18


def test_calculate_order_no_tax(client):
    """Test order calculation without tax."""
    payload = {
        'items': [
            {'product_name': 'Burger', 'quantity': 1, 'unit_price': 10.00}
        ]
    }
    
    response = client.post(
        '/api/orders/calculate',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 10.00
    assert data['subtotal'] == 10.00
    assert data['tax'] == 0.00


def test_calculate_order_empty_items(client):
    """Test order calculation with empty items list."""
    payload = {
        'items': [],
        'tax_rate': 0.20
    }
    
    response = client.post(
        '/api/orders/calculate',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 400


def test_calculate_order_negative_quantity(client):
    """Test order calculation with negative quantity."""
    payload = {
        'items': [
            {'product_name': 'Burger', 'quantity': -1, 'unit_price': 10.00}
        ]
    }
    
    response = client.post(
        '/api/orders/calculate',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 400


def test_calculate_order_missing_field(client):
    """Test order calculation with missing required field."""
    payload = {
        'items': [
            {'product_name': 'Burger', 'quantity': 1}  # Missing unit_price
        ]
    }
    
    response = client.post(
        '/api/orders/calculate',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 400


def test_validate_transition_valid(client):
    """Test valid status transition."""
    payload = {
        'current_status': 'pending',
        'new_status': 'confirmed'
    }
    
    response = client.post(
        '/api/orders/validate-transition',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['valid'] is True
    assert data['current_status'] == 'pending'
    assert data['new_status'] == 'confirmed'


def test_validate_transition_invalid(client):
    """Test invalid status transition."""
    payload = {
        'current_status': 'delivered',
        'new_status': 'pending'
    }
    
    response = client.post(
        '/api/orders/validate-transition',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['valid'] is False


def test_validate_transition_missing_field(client):
    """Test status transition validation with missing field."""
    payload = {
        'current_status': 'pending'
        # Missing new_status
    }
    
    response = client.post(
        '/api/orders/validate-transition',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 400


def test_swagger_docs_accessible(client):
    """Test that Swagger documentation is accessible."""
    response = client.get('/api/docs')
    assert response.status_code == 200
