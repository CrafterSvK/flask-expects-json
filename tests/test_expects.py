import unittest
import json
import flask

from flask_expects_json import expects_json

schema = {
            "type": "object",
            "properties": {
                "price": {"type": "number"},
                "name": {"type": "string"},
            },
            "required": ["price"]
        }


class TestExpects(unittest.TestCase):
    def setup_route(self, schema):
        @self.app.route('/')
        @expects_json(schema)
        def index():
            return 'happy'

    def setUp(self):
        self.app = flask.Flask(__name__)

        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_valid_decorator(self):
        self.setup_route(None)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 400)
        response = self.client.get('/', data=json.dumps(dict()))
        self.assertEqual(response.status_code, 200)

    def test_validation_valid(self):
        self.setup_route(schema)
        response = self.client.get('/', data=json.dumps({"name": "Eggs", "price": 34.99}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(flask.g.data['name'], 'Eggs')
        self.assertEqual(flask.g.data['price'], 34.99)

    def test_validation_invalid(self):
        self.setup_route(schema)
        response = self.client.get('/', data=json.dumps({"name": "Eggs", "price": 'invalid'}))
        self.assertEqual(response.status_code, 400)

    def test_missing_parameter(self):
        self.setup_route(schema)
        response = self.client.get('/', data=json.dumps({"name": "Eggs"}))
        self.assertEqual(response.status_code, 400)

    def test_additional_parameter(self):
        self.setup_route(schema)
        response = self.client.get('/', data=json.dumps({"name": "Eggs", "price": 34.99}))
        self.assertEqual(response.status_code, 200)

    def test_no_schema(self):
        @self.app.route('/')
        @expects_json()
        def index():
            return 'happy'
        response = self.client.get('/', data=json.dumps(dict()))
        self.assertEqual(response.status_code, 200)
