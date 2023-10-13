from django.db import models
from django.contrib.auth.models import User

# Create your models here.

"""
class Country(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    

class Crags(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="crags")
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
"""
        
class Section(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class MainTopic(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="maintopics")
    title = models.CharField(max_length=200)
    description = models.TextField()
    PostCount = models.BigIntegerField()
    SubTopicCount = models.BigIntegerField()

    def __str__(self):
        return self.title
    
    def addPostCount(self):
        self.PostCount += 1
        self.save()

    def minusPostCount(self):
        self.PostCount -= 1
        self.save()

    def addSubTopicCount(self):
        self.SubTopicCount += 1
        self.save()

    def minusSubTopicCount(self):
        self.SubTopicCount -= 1
        self.save()

class SubTopic(models.Model):
    mainTopic = models.ForeignKey(MainTopic, on_delete=models.CASCADE, related_name="subtopics")
    title = models.CharField(max_length=200)
    description = models.TextField()
    PostCount = models.BigIntegerField()

    def __str__(self):
        return self.title
    
    def addPostCount(self):
        self.PostCount += 1
        self.save()

    def minusPostCount(self):
        self.PostCount -= 1
        self.save()
        
class ForumPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", null=True)
    topic = models.ForeignKey(SubTopic, on_delete=models.CASCADE, related_name="posts", null=True)
    title = models.CharField(max_length=200)
    text = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    date = models.TextField(null=True)

    def __str__(self):
        return self.title

class Achievement(models.Model):
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=150)

    def __str__(self):
        return self.title

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="account")
    is_admin = models.BooleanField(default=False)
    suspended = models.BooleanField(default=False)
    totalRoute = models.BigIntegerField(default=0)
    totalDistance = models.BigIntegerField(default=0)
    achievements = models.ManyToManyField(Achievement, blank=True)
    about = models.TextField(default="")
    followers = models.ManyToManyField(User, related_name='followings',blank=True)
    followings = models.ManyToManyField(User, related_name='followers', blank=True)
    followersCount = models.BigIntegerField(default=0)
    followingsCount = models.BigIntegerField(default=0)
    facebookLink = models.CharField(max_length=150, default="Empty")
    youtubeLink = models.CharField(max_length=150, default="Empty")

    def __str__(self):
        return self.user.username

    def updateSuspend(self, status):
        self.suspended = status
        self.save()

    def updateRouteAndDist(self):
        activities = self.user.activities.all()
        totalRoute = 0
        totalDistance = 0
        for activity in activities:
            totalRoute += 1
            totalDistance += activity.distance
        self.totalRoute = totalRoute
        self.totalDistance = totalDistance
        self.save()

    def addAchievement(self, achievement):
        self.achievements.add(achievement)
        self.save()
    
    def setAbout(self, about):
        self.about = about
        self.save()

    def addFollower(self, user):
        self.followers.add(user)
        self.followersCount += 1
        self.save()

    def addFollowing(self, user):
        self.followings.add(user)
        self.followingsCount += 1
        self.save()

    def removeFollower(self, user):
        self.followers.remove(user)
        self.followersCount -= 1
        self.save()

    def removeFollowing(self, user):
        self.followings.remove(user)
        self.followingsCount -= 1
        self.save()

    def updateFacebook(self, facebook):
        self.facebookLink = facebook
        self.save()

    def updateYoutube(self, youtube):
        self.youtubeLink = youtube
        self.save()
    
class ContactUs(models.Model):
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    status = models.BooleanField(default=False)

    def __str__(self):
        result = self.firstname + " " + self.lastname + " " + str(self.id)
        return result
    
class FlaggedPost(models.Model):
    post =  models.OneToOneField(ForumPost, on_delete=models.CASCADE, related_name="post")
    users = models.ManyToManyField(User, related_name='flaggedPosts')

    def __str__(self):
        return self.post.title
    
class ClimbingActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities", null=True)
    locName = models.CharField(max_length=200)
    distance = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return self.locName
    
class SearchHistory(models.Model):
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="searchHistories", null=True)

    def __str__(self):
        return self.text
    
class Crag(models.Model):
    country = models.CharField(max_length=150)
    region = models.CharField(max_length=150)
    name =  models.CharField(max_length=150)
    desc =  models.TextField()
    rocktype =  models.CharField(max_length=150)
    altitude = models.BigIntegerField(default=0)

    def __str__(self):
        return self.name

    

class Comment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    date = models.TextField(null=True)

    def __str__(self):
        return str(self.text)


