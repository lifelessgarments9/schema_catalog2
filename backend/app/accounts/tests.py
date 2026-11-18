from urllib.parse import parse_qs, urlparse
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings

from app.accounts.models import User


@override_settings(
    SSO_BASE_URL="https://sso.bmstu.ru/portal4/oauth2",
    SSO_CLIENT_ID="bmstu-guimc",
    SSO_CLIENT_SECRET="test-secret",
    SSO_REDIRECT_URI="https://catalog.example.test/accounts/sso/callback/",
    FRONTEND_URL="https://catalog.example.test",
)
class SSOOAuthTests(TestCase):
    def test_login_redirects_with_oauth_state_and_callback_uri(self):
        response = self.client.get("/accounts/sso/login/")
        location = urlparse(response["Location"])
        params = parse_qs(location.query)

        self.assertEqual(location.path, "/portal4/oauth2/authorize")
        self.assertEqual(params["response_type"], ["code"])
        self.assertEqual(params["client_id"], ["bmstu-guimc"])
        self.assertEqual(params["redirect_uri"], [
            "https://catalog.example.test/accounts/sso/callback/"
        ])
        self.assertEqual(params["state"], [self.client.session["sso_oauth_state"]])

    @patch("app.accounts.views.requests.get")
    @patch("app.accounts.views.requests.post")
    def test_callback_exchanges_code_and_creates_local_user(self, token_post, userinfo_get):
        session = self.client.session
        session["sso_oauth_state"] = "valid-state"
        session.save()

        token_response = Mock()
        token_response.json.return_value = {"access_token": "sso-access"}
        token_post.return_value = token_response

        userinfo_response = Mock()
        userinfo_response.json.return_value = {
            "guid": "bmstu-guid",
            "firstname": "Иван",
            "lastname": "Иванов",
            "email": "ivan@example.test",
        }
        userinfo_get.return_value = userinfo_response

        response = self.client.get(
            "/accounts/sso/callback/",
            {"code": "oauth-code", "state": "valid-state"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith(
            "https://catalog.example.test/sso-callback#access="
        ))
        token_post.assert_called_once()
        self.assertEqual(
            token_post.call_args.kwargs["data"],
            {
                "grant_type": "authorization_code",
                "code": "oauth-code",
                "redirect_uri": "https://catalog.example.test/accounts/sso/callback/",
            },
        )
        self.assertEqual(
            token_post.call_args.kwargs["auth"],
            ("bmstu-guimc", "test-secret"),
        )
        userinfo_get.assert_called_once_with(
            "https://sso.bmstu.ru/portal4/oauth2/userinfo",
            headers={"Authorization": "Bearer sso-access"},
            timeout=10,
        )

        user = User.objects.get(username="sso_bmstu-guid")
        self.assertEqual(user.email, "ivan@example.test")
        self.assertEqual(user.first_name, "Иван")
        self.assertEqual(user.last_name, "Иванов")
        self.assertFalse(user.has_usable_password())

    @patch("app.accounts.views.requests.post")
    def test_callback_rejects_invalid_state_without_token_exchange(self, token_post):
        session = self.client.session
        session["sso_oauth_state"] = "expected-state"
        session.save()

        response = self.client.get(
            "/accounts/sso/callback/",
            {"code": "oauth-code", "state": "attacker-state"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("error=sso_state", response["Location"])
        token_post.assert_not_called()
