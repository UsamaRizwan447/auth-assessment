from django.urls import path
from .views import linkedin_login, linkedin_callback, login_page_ui, dashboard, user_logout

urlpatterns = [
    path("linkedin/", linkedin_login, name="linkedin_login"),
    path("linkedin/backToApp/", linkedin_callback, name="linkedin_callback"),
    path("login/", login_page_ui, name="login_page_ui"),
    path("dashboard/", dashboard, name="dashboard"),
    path("logout/", user_logout, name="logout"),
]
