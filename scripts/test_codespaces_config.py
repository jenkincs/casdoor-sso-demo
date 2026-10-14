import pathlib
import tempfile
import unittest
from codespaces_config import create_config

class ConfigTest(unittest.TestCase):
    def test_restarts_keep_credentials_and_refresh_callback_hosts(self):
        with tempfile.TemporaryDirectory() as directory:
            first=create_config('demo-one',directory)
            second=create_config('demo-two',directory)
            self.assertEqual(first['DEMO_PASSWORD'],second['DEMO_PASSWORD'])
            self.assertEqual(first['BOOKING_CLIENT_SECRET'],second['BOOKING_CLIENT_SECRET'])
            self.assertEqual(second['BOOKING_URL'],'https://demo-two-8080.app.github.dev')
            self.assertIn('@postgres:5432/casdoor',second['DATABASE_URL'])
            self.assertNotIn('ADMIN_PASSWORD',pathlib.Path(directory,'status.json').read_text())
            self.assertEqual(pathlib.Path(directory,'runtime.env').stat().st_mode & 0o777,0o600)
    def test_reject_invalid_host(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):create_config('demo.bad/host',directory)

if __name__=='__main__':unittest.main()
