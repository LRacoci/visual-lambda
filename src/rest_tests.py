import json
import rest
import unittest

# Classe que faz testes unitarios de comunicao entre o cliente e o servidor
class RestTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    # Metodo chamado antes de cada teste
    def setUp(self):
        self.app = rest.app.test_client()
        self.app.testing = True

    # Metodo chamado apos cada teste
    def tearDown(self):
        pass

    # Testa o status da chamada para pegar o index
    def test_home_status_code(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

    # Testa o tipo do conteudo do index
    def test_content_type(self):
        result = self.app.get('/')
        self.assertIn('text/html', result.content_type)

    # Testa as chamadas para traduzir o codigo em arvore,
    # retornando a arvore (JSON) que seria mostrado na tela
    def test_translate_code(self):
        from glob import glob
        for fileAddress in glob('./lexer_parser/tests/arq*.hs'):
            print fileAddress
            with open(fileAddress) as inpFile:
                code = inpFile.read()
            result = self.app.post('/translateCode', data=json.dumps(dict(code=code)), content_type='application/json', follow_redirects=True)
            with open(fileAddress.replace("lexer_parser", "tree").replace("arq", "tree").replace("hs", "json")) as outFile:
                resp = outFile.read()
            resultJSON = json.loads(result.data)['tree']
            respJSON = json.loads(resp)
            self.assertEqual(resultJSON, respJSON)

if __name__ == '__main__':
    unittest.main()