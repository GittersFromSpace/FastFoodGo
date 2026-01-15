from flask import Flask, request, redirect
from flask_restx import Api, Resource, fields
from src.business import OrderItem, calculate_order_total, validate_status_transition

app = Flask(__name__)
app.config['RESTX_MASK_SWAGGER'] = False

api = Api(
    app,
    version='1.0',
    title='FastFood Order Management API',
    description='REST API for managing fast food orders',
    doc='/docs'
)

ns = api.namespace('api/orders', description='Order operations')

order_item_model = api.model('OrderItem', {
    'product_name': fields.String(required=True, example='Burger'),
    'quantity': fields.Integer(required=True, example=2),
    'unit_price': fields.Float(required=True, example=9.99)
})

calculate_request_model = api.model('CalculateOrderRequest', {
    'items': fields.List(fields.Nested(order_item_model), required=True),
    'tax_rate': fields.Float(required=False, example=0.20, default=0.0)
})

calculate_response_model = api.model('CalculateOrderResponse', {
    'total': fields.Float(),
    'subtotal': fields.Float(),
    'tax': fields.Float()
})

status_transition_model = api.model('StatusTransitionRequest', {
    'current_status': fields.String(required=True, example='pending'),
    'new_status': fields.String(required=True, example='confirmed')
})

status_transition_response_model = api.model('StatusTransitionResponse', {
    'valid': fields.Boolean(),
    'current_status': fields.String(),
    'new_status': fields.String()
})


@app.route('/')
def index():
    return redirect('/docs')


@api.route('/health')
class Health(Resource):
    def get(self):
        return {'status': 'healthy', 'service': 'FastFood Order Management'}, 200


@ns.route('/calculate')
class CalculateOrder(Resource):
    @ns.expect(calculate_request_model)
    @ns.marshal_with(calculate_response_model)
    def post(self):
        try:
            data = request.json
            items = [
                OrderItem(
                    product_name=item['product_name'],
                    quantity=item['quantity'],
                    unit_price=item['unit_price']
                )
                for item in data['items']
            ]
            
            tax_rate = data.get('tax_rate', 0.0)
            total = calculate_order_total(items, tax_rate)
            subtotal = sum(item.get_total() for item in items)
            tax = round(subtotal * tax_rate, 2)
            
            return {
                'total': total,
                'subtotal': round(subtotal, 2),
                'tax': tax
            }, 200
            
        except ValueError as e:
            api.abort(400, f'Validation error: {str(e)}')
        except TypeError as e:
            api.abort(400, f'Type error: {str(e)}')
        except KeyError as e:
            api.abort(400, f'Missing required field: {str(e)}')
        except Exception as e:
            api.abort(500, f'Internal error: {str(e)}')


@ns.route('/validate-transition')
class ValidateTransition(Resource):
    @ns.expect(status_transition_model)
    @ns.marshal_with(status_transition_response_model)
    def post(self):
        try:
            data = request.json
            current_status = data['current_status']
            new_status = data['new_status']
            is_valid = validate_status_transition(current_status, new_status)
            
            return {
                'valid': is_valid,
                'current_status': current_status,
                'new_status': new_status
            }, 200
            
        except ValueError as e:
            api.abort(400, f'Validation error: {str(e)}')
        except TypeError as e:
            api.abort(400, f'Type error: {str(e)}')
        except KeyError as e:
            api.abort(400, f'Missing required field: {str(e)}')
        except Exception as e:
            api.abort(500, f'Internal error: {str(e)}')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
