
import os
import unittest
from web_api import create_app
import json
from flask import jsonify

os.environ['FLASK_CONFIG'] = os.path.abspath('config-debug.yaml')
app = create_app(debug=False, raise_errors=False)

# from web_api import create_app

class BasicTests(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app = app.test_client()

    # executed after each test
    def tearDown(self):
        pass

    def test_ping(self):
        response = self.app.get('/ping', follow_redirects=True)
        print(json.loads(response.data))
        self.assertEqual(response.status_code, 200)

    def test_signup(self):
        auth_payload = {'username':'bob','password':'default','is_verified':True}
        auth_payload = json.dumps(auth_payload)
        response = self.app.post('/auth/signup', data = auth_payload, content_type='application/json', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        su_payload = {'username':'bob2','password':'default','is_verified':True}
        su_payload = json.dumps(su_payload)
        response = self.app.post('/auth/signup', data = su_payload, content_type='application/json', follow_redirects=True)

        login_payload = {'username':'bob2','password':'default'}
        login_payload = json.dumps(login_payload)
        response = self.app.post('/auth/login', data = login_payload, content_type='application/json', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_login_bad(self):
        su_payload = {'username':'bob2','password':'default','is_verified':True}
        su_payload = json.dumps(su_payload)
        response = self.app.post('/auth/signup', data = su_payload, content_type='application/json', follow_redirects=True)

        login_payload = {'username':'bob2','password':'default2'}
        login_payload = json.dumps(login_payload)
        response = self.app.post('/auth/login', data = login_payload, content_type='application/json', follow_redirects=True)
        self.assertEqual(response.status_code, 401)

    def test_postjob(self):
        su_payload = {'username':'bob2','password':'default','is_verified':True}
        su_payload = json.dumps(su_payload)
        response = self.app.post('/auth/signup', data = su_payload, content_type='application/json', follow_redirects=True)

        login_payload = {'username':'bob2','password':'default'}
        login_payload = json.dumps(login_payload)
        response = self.app.post('/auth/login', data = login_payload, content_type='application/json', follow_redirects=True)
        token = json.loads(response.data)["token"]

        job_payload = {'is_active':True,
                       'square_feet':10,
                       'pickup_address':'test',
                       'dropoff_address':'test2'}
        job_payload = json.dumps(job_payload)
        response = self.app.post('/job/', data = job_payload, content_type='application/json',headers={'Authorization': 'bearer '+token}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

def run():
    unittest.main()

if __name__ == '__main__':
    run()


# import os
# import unittest
# class TestStringMethods(unittest.TestCase):
#     def test_upper(self):
#         self.assertEqual("foo".upper(), 'FOO')
#
#     def test_isupper(self):
#         self.assertTrue('FOO'.isupper())
#         self.assertFalse('Foo'.isupper())
#
#     def test_split(self):
#         s = 'hello world'
#         self.assertEqual(s.split(), ['hello', 'world'])
#         # check that s.split fails when the separator is not a string
#         with self.assertRaises(TypeError):
#             s.split(2)
#
# if __name__ == '__main__':
#     unittest.main()
