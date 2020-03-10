from django.conf.urls import url
from Users import views


urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view()),
]
