
import os
import unittest
from web_api import create_app
import json

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

    def test_main_page(self):
        response = self.app.get('/ping', follow_redirects=True)
        print(json.loads(response.data))
        self.assertEqual(response.status_code, 200)

    # def test_main_page(self):
    #     response = self.app.get('/ping', follow_redirects=True)
    #     print(json.loads(response.data))
    #     self.assertEqual(response.status_code, 200)

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
