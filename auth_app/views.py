from django.shortcuts import render

from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import requests

oauth = OAuth()
oauth.register(
    "linkedin",
    client_id=settings.LINKEDIN_CLIENT_ID,
    client_secret=settings.LINKEDIN_CLIENT_SECRET,
    authorize_url="https://www.linkedin.com/oauth/v2/authorization",
    access_token_url="https://www.linkedin.com/oauth/v2/accessToken",
    client_kwargs={"scope": "openid profile email"},
)

def login_page_ui(request):
    return render(request, "loginPage.html")


def linkedin_login(request):
    redirect_uri = settings.LINKEDIN_REDIRECT_URI
    return oauth.linkedin.authorize_redirect(request, redirect_uri)


def linkedin_callback(request):
    try:
        code = request.GET.get("code")
        if not code:
            print("No authorization code received")
            return redirect("/")  # Redirect if no code received

        # Exchanging auth code for access token
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET,
        }
        token_headers = {"Content-Type": "application/x-www-form-urlencoded"}

        token_response = requests.post(token_url, data=token_data, headers=token_headers)
        token_json = token_response.json()

        access_token = token_json.get("access_token")
        if not access_token:
            return redirect("/")  # Redirect if token retrieval fails

        # Fetch user profile and email using OpenID Connect
        userinfo_url = "https://api.linkedin.com/v2/userinfo"
        userinfo_headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = requests.get(userinfo_url, headers=userinfo_headers)
        userinfo_data = userinfo_response.json()

        # Extract user data
        email = userinfo_data.get("email", "")
        first_name = userinfo_data.get("given_name", "")
        last_name = userinfo_data.get("family_name", "")

        if not email:
            print("Error: Email missing from LinkedIn OpenID response")
            return redirect("/")

        # Check if user exists, else create one
        user, created = User.objects.get_or_create(email=email, defaults={
            "username": email.split("@")[0],
            "first_name": first_name,
            "last_name": last_name,
        })

        # Log in the user
        login(request, user)
        return redirect(settings.LOGIN_REDIRECT_URL)

    except Exception as e:
        print("Exception in LinkedIn Callback:", e)
        return redirect("/")

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

def user_logout(request):
    logout(request)
    return redirect("/auth/login/")