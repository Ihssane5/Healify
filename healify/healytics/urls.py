
import healytics
from django.urls import path
from . import views

#app_name = "healytics"
urlpatterns = [
    path("", views.healytics, name="healytics"),
    path("uploadPdf/", views.uploadPdf, name="uploadPdf"),
    path("chatPdf/", views.chatPdf, name="chatPdf"),
    path("answerQuery/",views.answerQuery, name="answerQuery"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

]
