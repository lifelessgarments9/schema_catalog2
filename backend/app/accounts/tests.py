import json
from urllib.parse import parse_qs, urlparse
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from django.urls import reverse

from app.accounts.models import User


@override_settings(
    SSO_BASE_URL="https://sso.bmstu.ru/portal4/oauth2",
    SSO_CLIENT_ID="bmstu-guimc",
    SSO_CLIENT_SECRET="test-secret",
    SSO_REDIRECT_URI="https://lk.guimc.bmstu.ru/fablab/",
    FRONTEND_URL="https://lk.guimc.bmstu.ru/fablab",
)
class SSOOAuthTests(TestCase):
    def test_login_redirect_uses_registered_fablab_uri_and_state(self):
        response = self.client.get(reverse("sso-login"))
        location = urlparse(response["Location"])
        params = parse_qs(location.query)

        self.assertEqual(location.scheme, "https")
        self.assertEqual(location.netloc, "sso.bmstu.ru")
        self.assertEqual(location.path, "/portal4/oauth2/authorize")
        self.assertEqual(params["response_type"], ["code"])
        self.assertEqual(params["client_id"], ["bmstu-guimc"])
        self.assertEqual(params["redirect_uri"], ["https://lk.guimc.bmstu.ru/fablab/"])
        self.assertEqual(params["state"], [self.client.session["sso_oauth_state"]])

    @patch("app.accounts.views.requests.get")
    @patch("app.accounts.views.requests.post")
    def test_callback_exchanges_code_and_returns_app_tokens(self, token_post, userinfo_get):
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

        response = self.client.post(
            reverse("sso-callback"),
            data=json.dumps({"code": "oauth-code", "state": "valid-state"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())
        token_post.assert_called_once()
        self.assertEqual(
            token_post.call_args.kwargs["data"],
            {
                "grant_type": "authorization_code",
                "code": "oauth-code",
                "client_id": "bmstu-guimc",
                "client_secret": "test-secret",
                "redirect_uri": "https://lk.guimc.bmstu.ru/fablab/",
            },
        )
        userinfo_get.assert_called_once_with(
            "https://sso.bmstu.ru/portal4/oauth2/userinfo",
            headers={"Authorization": "Bearer sso-access"},
            timeout=10,
        )
        user = User.objects.get(username="sso_bmstu-guid")
        self.assertEqual(user.email, "ivan@example.test")
        self.assertFalse(user.has_usable_password())

    @patch("app.accounts.views.requests.post")
    def test_callback_rejects_mismatched_state(self, token_post):
        session = self.client.session
        session["sso_oauth_state"] = "expected-state"
        session.save()

        response = self.client.post(
            reverse("sso-callback"),
            data=json.dumps({"code": "oauth-code", "state": "wrong-state"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        token_post.assert_not_called()

