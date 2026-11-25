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
    SSO_REDIRECT_URI="https://lk.guimc.bmstu.ru/fablab/api/accounts/sso/callback/",
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
        self.assertEqual(
            params["redirect_uri"],
            ["https://lk.guimc.bmstu.ru/fablab/api/accounts/sso/callback/"],
        )
        self.assertEqual(params["state"], [self.client.session["sso_oauth_state"]])

    @patch("app.accounts.views.requests.get")
    @patch("app.accounts.views.requests.post")
    def test_get_callback_exchanges_code_and_hands_off_one_time_ticket(
        self,
        token_post,
        userinfo_get,
    ):
        session = self.client.session
        session["sso_oauth_state"] = "valid-state"
        session.save()

        token_response = Mock()
        token_response.ok = True
        token_response.json.return_value = {"access_token": "sso-access"}
        token_post.return_value = token_response

        userinfo_response = Mock()
        userinfo_response.raise_for_status.return_value = None
        userinfo_response.json.return_value = {
            "guid": "bmstu-guid",
            "firstname": "Иван",
            "lastname": "Иванов",
            "email": "ivan@example.test",
        }
        userinfo_get.return_value = userinfo_response

        response = self.client.get(
            reverse("sso-callback"),
            {"code": "oauth-code", "state": "valid-state"},
        )

        self.assertEqual(response.status_code, 302)
        callback_location = urlparse(response["Location"])
        self.assertEqual(
            f"{callback_location.scheme}://{callback_location.netloc}{callback_location.path}",
            "https://lk.guimc.bmstu.ru/fablab/sso/callback/",
        )
        ticket = parse_qs(callback_location.fragment)["ticket"][0]
        self.assertEqual(ticket, self.client.session["sso_login_ticket"])

        token_post.assert_called_once()
        self.assertEqual(
            token_post.call_args.kwargs["data"],
            {
                "grant_type": "authorization_code",
                "code": "oauth-code",
                "client_id": "bmstu-guimc",
                "client_secret": "test-secret",
                "redirect_uri": "https://lk.guimc.bmstu.ru/fablab/api/accounts/sso/callback/",
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

        complete_response = self.client.post(
            reverse("sso-complete"),
            data=json.dumps({"ticket": ticket}),
            content_type="application/json",
        )
        self.assertEqual(complete_response.status_code, 200)
        self.assertIn("access", complete_response.json())
        self.assertIn("refresh", complete_response.json())

        reused_ticket_response = self.client.post(
            reverse("sso-complete"),
            data=json.dumps({"ticket": ticket}),
            content_type="application/json",
        )
        self.assertEqual(reused_ticket_response.status_code, 400)

    @patch("app.accounts.views.requests.post")
    def test_get_callback_rejects_mismatched_state(self, token_post):
        session = self.client.session
        session["sso_oauth_state"] = "expected-state"
        session.save()

        response = self.client.get(
            reverse("sso-callback"),
            {"code": "oauth-code", "state": "wrong-state"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("error=sso_state", response["Location"])
        token_post.assert_not_called()

    def test_complete_rejects_expired_ticket(self):
        session = self.client.session
        session["sso_login_ticket"] = "expired-ticket"
        session["sso_login_ticket_created_at"] = 0
        session["sso_login_tokens"] = {"access": "access", "refresh": "refresh"}
        session.save()

        response = self.client.post(
            reverse("sso-complete"),
            data=json.dumps({"ticket": "expired-ticket"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn("sso_login_ticket", self.client.session)

