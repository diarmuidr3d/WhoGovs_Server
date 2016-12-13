from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?i)person/(?P<person_id>[0-9]+)/$', views.person, name="representative"),
]