#project/test_basic.py

import os
import unittest
import web_api
import json

os.environ['FLASK_CONFIG'] = os.path.abspath('instance/config.yaml')
app = web_api.create_app(debug=False, raise_errors=False)

# from web_api import create_app

class BasicTests(unittest.TestCase):
   # executed prior to each test
   def setUp(self):
       self.app = app
       self.app = app.test_client()

   # executed after each test
   def tearDown(self):
       pass

   def test_main_page(self):
       response = self.app.get('/ping', follow_redirects=True)
       print(json.loads(response.data))
       self.assertEqual(response.status_code, 200)

def run():
    unittest.main()

if __name__ == '__main__':
    run()
