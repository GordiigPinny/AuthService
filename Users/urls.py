from django.conf.urls import url
from Users import views


urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view()),
    url(r'^user_info/$', views.UserInfoView.as_view()),
    url(r'^users/$', views.UserListView.as_view()),
    url(r'^users/(?P<pk>\d+)/$', views.UserDetailView.as_view()),
]
