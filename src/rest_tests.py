import json
import rest
import unittest

# Class to do unit tests of communication between client and server
class RestTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    # Method called before each test
    def setUp(self):
        self.app = rest.app.test_client()
        self.app.testing = True

    # Method called after each test
    def tearDown(self):
        pass

    # Test the status of get index
    def test_home_status_code(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

    # Test the content of get index
    def test_content_type(self):
        result = self.app.get('/')
        self.assertIn('text/html', result.content_type)

    # Test the post to translate the code into a tree
    # returnin the tree (JSON) which would be drawed
    def test_translate_code(self):
        from glob import glob
        for fileAddress in glob('./lexer_parser/tests/*.hs'):
            print fileAddress
            with open(fileAddress) as inpFile:
                code = inpFile.read()
            result = self.app.post(
                '/translateCode', data=json.dumps(
                    dict(
                        code=code,
                        eta = "eta" in fileAddress,
                        fold = "fold" in fileAddress,
                        prop = "prop" in fileAddress,
                        memo = "memo" in fileAddress
                    )
                ),
                content_type='application/json',
                follow_redirects=True
            )
            if result._status_code == 200:
                with open(fileAddress.replace(".hs", ".json")) as outFile:
                    resp = outFile.read()
                resultJSON = json.loads(result.data)['tree']
                respJSON = json.loads(resp)
                self.assertEqual(resultJSON, respJSON)
            else:

                with open(fileAddress.replace(".hs", ".err")) as outFile:
                    resp = outFile.read()
                self.assertEqual(result.data.replace("u\'", "\'"), resp)
            print "ok"

if __name__ == '__main__':
    unittest.main()