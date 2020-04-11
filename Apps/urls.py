from django.conf.urls import url
from Apps import views


urlpatterns = [
    url(r'^apps/$', views.AppsView.as_view()),
    url(r'^apps/(?P<pk>\w+)/$', views.AppView.as_view()),
]
