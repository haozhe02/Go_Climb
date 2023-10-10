from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("", views.home, name="home"),
    path("search/", views.search1, name="search"),
    path("forum/", views.forum1, name="forum"),
    path("createPost/<int:id>", views.createPost, name="createPost"),
    path("weather/", views.weather, name="weather"),
    path("contact/", views.contact, name="contact"),
    path("loginUser/", views.loginUser, name="login"),
    path("ARroute/", views.ARroute, name="arroute"),
    path("profile/", views.profile, name="profile"),
    path("topic/<int:id>/", views.topic, name="topic"), 
    path("subtopic/<int:id>/", views.subtopic, name="subtopic"),
    path("deletePost/<int:id>/", views.deletePost, name="deletePost"),
    path("editPost/<int:id>/", views.editPost, name="editPost"),
    path("searchPost/", views.searchPost, name="searchPost"),
    path("createSection/", views.createSection, name="createSection"),
    path("deleteSection/<int:id>/", views.deleteSection, name="deleteSection"),
    path("createTopic/<int:id>/", views.createTopic, name="createTopic"),
    path("deleteTopic/<int:id>/", views.deleteTopic, name="deleteTopic"),
    path("createSubtopic/<int:id>/", views.createSubtopic, name="createSubtopic"),
    path("deleteSubtopic/<int:id>/", views.deleteSubtopic, name="deleteSubtopic"),
    path("success/", views.success, name="success"),
    path("adminPortal/", views.admin, name="admin"),
    path("markContactDone/<int:id>/", views.markContactDone, name="markContactDone"),
    path("editLogin/<int:id>/", views.editLogin, name="editLogin"),
    path("viewProfile/<int:id>/", views.viewProfile, name="viewProfile"),
    path("flagPost/<int:id>/", views.flagPost, name="flagPost"),
    path("viewAccounts/", views.viewAccounts, name="viewAccounts"),
    path("suspendAccount/<int:id>/", views.suspendAccount, name="suspendAccount"),
    path("activateAccount/<int:id>/", views.activateAccount, name="activateAccount"),
    path("searchAccount/", views.searchAccount, name="searchAccount"),
    path("suspendAccountByUser/<int:id>/", views.suspendAccountByUser, name="suspendAccountByUser"),
    path("createClimbActivity/", views.createClimbActivity, name="createClimbActivity"),
    path("editAbout/<int:id>/", views.editAbout, name="editAbout"),
    
        
    #path("search/result", views.result, name="result"),
    #path("create/", views.createCountry, name="createCountry"),
    #path("country/", views.list, name="list"),
    #path("<int:id>", views.index, name="index"),
    #path("forum/<int:id>", views.editPost, name="editPost"),
    #path("forum/comment/<int:id>", views.comment, name="comment"),
    #path("forum/delete/<int:id>", views.deletePost, name="deletePost"),
    #path("testing/", views.search1, name="testing"),
]