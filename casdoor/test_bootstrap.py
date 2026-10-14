import unittest
from bootstrap import build_initial_data

class BootstrapTest(unittest.TestCase):
    def test_clients_are_distinct_and_admin_signup_is_disabled(self):
        env = {'BOOKING_URL':'https://booking.example','INVOICE_URL':'https://invoice.example',
               'CASDOOR_URL':'https://auth.example','BOOKING_CLIENT_ID':'booking-id',
               'BOOKING_CLIENT_SECRET':'booking-secret','INVOICE_CLIENT_ID':'invoice-id',
               'INVOICE_CLIENT_SECRET':'invoice-secret','ADMIN_CLIENT_ID':'admin-id',
               'ADMIN_CLIENT_SECRET':'admin-secret','DEMO_PASSWORD':'testing-only'}
        data = build_initial_data(env)
        apps = data['applications']
        self.assertEqual(len({app['clientId'] for app in apps}),3)
        self.assertTrue(all(not app['enableSignUp'] for app in apps))
        self.assertTrue(all(app['enableAutoSignin'] for app in apps))
        self.assertEqual(apps[0]['redirectUris'],['https://booking.example/login/oauth2/code/casdoor'])
        self.assertEqual(apps[1]['redirectUris'],['https://invoice.example/callback'])
        self.assertFalse(data['users'][0]['isAdmin'])

if __name__ == '__main__': unittest.main()
