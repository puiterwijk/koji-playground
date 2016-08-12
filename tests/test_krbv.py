import unittest

# This is python-mock, not the rpm mock tool we know and love
import mock

import koji


class KrbVTestCase(unittest.TestCase):

    @mock.patch('koji.krbV', new=None)
    @mock.patch('koji.gssapi', new=None)
    @mock.patch('koji.ClientSession._setup_connection', new=mock.MagicMock())
    def test_krbv_disabled(self):
        """ Test that when krb libs are absent, we behave rationally. """
        self.assertEquals(koji.krbV, None)
        self.assertEquals(koji.gssapi, None)
        session = koji.ClientSession('whatever')
        with self.assertRaises(ImportError):
            session.krb_login()

    @mock.patch('koji.krbV', new=None)
    @mock.patch('koji.gssapi', new=None)
    @mock.patch('koji.ClientSession._setup_connection', new=mock.MagicMock())
    @mock.patch('koji.ClientSession._callMethod', new=mock.MagicMock())
    @mock.patch('koji.ClientSession.logout', new=mock.MagicMock())
    @mock.patch('koji.ClientSession.krb_gssapi_login')
    @mock.patch('koji.ClientSession.krb_krbV_login')
    def test_krbv_disabled(self, krb_krbV_login, krb_gssapi_login):
        """ Test that correct krb codepath is used """

        mocks = (krb_krbV_login, krb_gssapi_login)
        sinfo = {'session-id': '23', 'session-key': 'fnord'}
        sinfo_str = '23 fnord'
        login_args = ('principal', 'keytab', 'ccache', 'proxyuser')

        with mock.patch('koji.gssapi', new=True):
            krb_gssapi_login.return_value = sinfo_str
            session = koji.ClientSession('whatever')
            session.krb_login(*login_args)
            krb_krbV_login.assert_not_called()
            krb_gssapi_login.assert_called_with(*login_args)
            assert session.sinfo == sinfo

        for m in mocks:
            m.reset_mock()

        with mock.patch('koji.krbV', new=True):
            krb_krbV_login.return_value = sinfo_str
            session = koji.ClientSession('whatever')
            session.krb_login(*login_args)
            krb_gssapi_login.assert_not_called()
            krb_krbV_login.assert_called_with(*login_args)
            assert session.sinfo == sinfo
