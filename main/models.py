from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.db.models import Q

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
    totalView = models.BigIntegerField(default=0)

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

    def addView(self):
        self.totalView += 1
        self.save()



class SubTopic(models.Model):
    mainTopic = models.ForeignKey(MainTopic, on_delete=models.CASCADE, related_name="subtopics")
    title = models.CharField(max_length=200)
    description = models.TextField()
    PostCount = models.BigIntegerField()
    totalView = models.BigIntegerField(default=0)

    def __str__(self):
        return self.title
    
    def addPostCount(self):
        self.PostCount += 1
        self.save()

    def minusPostCount(self):
        self.PostCount -= 1
        self.save()

    def addView(self):
        self.totalView += 1
        self.save()
        
class ForumPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts", null=True)
    topic = models.ForeignKey(SubTopic, on_delete=models.CASCADE, related_name="posts", null=True)
    title = models.CharField(max_length=200)
    text = RichTextField(blank=True, null=True)
    #text = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    date = models.TextField(null=True)
    totalView = models.BigIntegerField(default=0)

    likeReactions = models.ManyToManyField(User, related_name="reactLike", blank=True)
    likeCount = models.BigIntegerField(default=0)
    laughReactions = models.ManyToManyField(User, related_name="reactLaugh", blank=True)
    laughCount = models.BigIntegerField(default=0)
    loveReactions = models.ManyToManyField(User, related_name="reactLove", blank=True)
    loveCount = models.BigIntegerField(default=0)
    angryReactions = models.ManyToManyField(User, related_name="reactAngry", blank=True)
    angryCount = models.BigIntegerField(default=0)
    scareReactions = models.ManyToManyField(User, related_name="reactScare", blank=True)
    scareCount = models.BigIntegerField(default=0)
    cryReactions = models.ManyToManyField(User, related_name="reactCry", blank=True)
    cryCount = models.BigIntegerField(default=0)

    def __str__(self):
        return self.title
    
    def addView(self):
        self.totalView += 1
        self.save()

    def reaction(self, number, user):
        if number == 1:
            self.likeReactions.add(user)
            self.likeCount+=1
            self.save()
        elif number == 2:
            self.laughReactions.add(user)
            self.laughCount+=1
            self.save()
        elif number == 3:
            self.loveReactions.add(user)
            self.loveCount+=1
            self.save()
        elif number == 4:
            self.angryReactions.add(user)
            self.angryCount+=1
            self.save()
        elif number == 5:
            self.scareReactions.add(user)
            self.scareCount+=1
            self.save()
        elif number == 6:
            self.cryReactions.add(user)
            self.cryCount+=1
            self.save()

    def cancelReaction(self, number, user):
        if number == 1:
            self.likeReactions.remove(user)
            self.likeCount-=1
            self.save()
        elif number == 2:
            self.laughReactions.remove(user)
            self.laughCount-=1
            self.save()
        elif number == 3:
            self.loveReactions.remove(user)
            self.loveCount-=1
            self.save()
        elif number == 4:
            self.angryReactions.remove(user)
            self.angryCount-=1
            self.save()
        elif number == 5:
            self.scareReactions.remove(user)
            self.scareCount-=1
            self.save()
        elif number == 6:
            self.cryReactions.remove(user)
            self.cryCount-=1
            self.save()

class PostDraft(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="drafts")
    topic = models.ForeignKey(SubTopic, on_delete=models.CASCADE, related_name="drafts")
    title = models.CharField(max_length=200)
    #text = models.TextField()
    text = RichTextField(blank=True, null=True)
    image = models.ImageField(null=True, blank=True, upload_to="images/")

    def __str__(self):
        return self.title
    

class Achievement(models.Model):
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=150)

    def __str__(self):
        return self.title
    
class Badge(models.Model):
    name = models.CharField(max_length=150)
    desc = models.TextField(null=True)

    def __str__(self):
        return self.name

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="account")
    is_admin = models.BooleanField(default=False)
    accountSuspended = models.BooleanField(default=False)
    profileSuspended = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    totalRoute = models.BigIntegerField(default=0)
    totalDistance = models.BigIntegerField(default=0)
    achievements = models.ManyToManyField(Achievement, blank=True)
    about = models.TextField(default="", null=True)
    followers = models.ManyToManyField(User, related_name='followings',blank=True)
    followings = models.ManyToManyField(User, related_name='followers', blank=True)
    followersCount = models.BigIntegerField(default=0)
    followingsCount = models.BigIntegerField(default=0)
    facebookLink = models.CharField(max_length=150, default="Empty")
    youtubeLink = models.CharField(max_length=150, default="Empty")
    savedMainTopics = models.ManyToManyField(MainTopic, blank=True, related_name='accountMT')
    savedSubTopics = models.ManyToManyField(SubTopic, blank=True, related_name='accountST')
    badges = models.ManyToManyField(Badge, blank=True, related_name='accounts')
    showingBadges = models.ManyToManyField(Badge, blank=True, related_name='accountsShowing')

    aboutPosition = models.IntegerField(default=1)
    historyPosition = models.IntegerField(default=2)
    achievementPosition = models.IntegerField(default=3)

    badgePosition = models.IntegerField(default=1)
    routesPosition = models.IntegerField(default=2)

    def __str__(self):
        return self.user.username

    def updateAccountSuspend(self, status):
        self.accountSuspended = status
        self.save()

    def updateProfileSuspend(self, status):
        self.profileSuspended = status
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

    def addSavedMT(self, maintopic):
        self.savedMainTopics.add(maintopic)
        self.save()

    def addSavedST(self, subtopic):
        self.savedSubTopics.add(subtopic)
        self.save()

    def addBadge(self, badge):
        self.badges.add(badge)
        self.save()

    def addShowingBadge(self, badge):
        self.showingBadges.add(badge)
        self.save()

    def removeShowingBadge(self, badge):
        self.showingBadges.remove(badge)
        self.save()
    
    def moveup(self, boxid):
        if boxid == 1:
            if self.aboutPosition != 1:
                self.aboutPosition -= 1

                #if about becomes first
                if self.aboutPosition == 1:
                    #if history is at first now
                    if self.historyPosition == 1:
                        self.historyPosition = 2
                    #if achievement is at first now 
                    else:
                        self.achievementPosition = 2
                #if about becomes second        
                else:
                    #if history is at second now
                    if self.historyPosition == 2:
                        self.historyPosition = 3
                    #if achievement is at second now 
                    else:
                        self.achievementPosition = 3
            self.save()       
        elif boxid == 2:
            if self.historyPosition != 1:
                self.historyPosition -= 1

                #if history becomes first
                if self.historyPosition == 1:
                    #if about is at first now
                    if self.aboutPosition == 1:
                        self.aboutPosition = 2
                    #if achievement is at first now 
                    else:
                        self.achievementPosition = 2
                #if history becomes second        
                else:
                    #if about is at second now
                    if self.aboutPosition == 2:
                        self.aboutPosition = 3
                    #if achievement is at second now 
                    else:
                        self.achievementPosition = 3
            self.save()
        elif boxid == 3:
            if self.achievementPosition != 1:
                self.achievementPosition -= 1

                #if achievement becomes first
                if self.achievementPosition == 1:
                    #if about is at first now
                    if self.aboutPosition == 1:
                        self.aboutPosition = 2
                    #if history is at first now 
                    else:
                        self.historyPosition = 2
                #if achievement becomes second        
                else:
                    #if about is at second now
                    if self.aboutPosition == 2:
                        self.aboutPosition = 3
                    #if history is at second now 
                    else:
                        self.historyPosition = 3
            self.save()

        elif boxid == 4:
            if self.badgePosition != 1:
                self.badgePosition = 1
                self.routesPosition = 2
            self.save()

        elif boxid == 5:
            if self.routesPosition != 1:
                self.routesPosition = 1
                self.badgePosition = 2
            self.save()

    def movedown(self, boxid):
        if boxid == 1:
            if self.aboutPosition != 3:
                self.aboutPosition += 1

                #if about becomes second
                if self.aboutPosition == 2:
                    #if history is at second now
                    if self.historyPosition == 2:
                        self.historyPosition = 1
                        self.save()
                    #if achievement is at second now 
                    else:
                        self.achievementPosition = 1
                #if about becomes third        
                else:
                    #if history is at third now
                    if self.historyPosition == 3:
                        self.historyPosition = 2
                    #if achievement is at third now 
                    else:
                        self.achievementPosition = 2
            self.save()       
        elif boxid == 2:
            if self.historyPosition != 3:
                self.historyPosition += 1

                #if history becomes second
                if self.historyPosition == 2:
                    #if about is at second now
                    if self.aboutPosition == 2:
                        self.aboutPosition = 1
                    #if achievement is at second now 
                    else:
                        self.achievementPosition = 1
                #if history becomes third        
                else:
                    #if about is at third now
                    if self.aboutPosition == 3:
                        self.aboutPosition = 2
                    #if achievement is at third now 
                    else:
                        self.achievementPosition = 2
            self.save()
        elif boxid == 3:
            if self.achievementPosition != 3:
                self.achievementPosition -= 1

                #if achievement becomes second
                if self.achievementPosition == 2:
                    #if about is at second now
                    if self.aboutPosition == 2:
                        self.aboutPosition = 1
                    #if history is at second now 
                    else:
                        self.historyPosition = 1
                #if achievement becomes third        
                else:
                    #if about is at third now
                    if self.aboutPosition == 3:
                        self.aboutPosition = 2
                    #if history is at second now 
                    else:
                        self.historyPosition = 2
            self.save()

        elif boxid == 4:
            if self.badgePosition != 2:
                self.badgePosition = 2
                self.routesPosition = 1
            self.save()
                
        elif boxid == 5:
            if self.routesPosition != 2:
                self.routesPosition = 2
                self.badgePosition = 1
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
    timeCompleted = models.CharField(max_length=150, null=True)

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
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    date = models.TextField(null=True)
    quotings = models.ManyToManyField(ForumPost, related_name='quotedBy', blank=True)

    def __str__(self):
        return str(self.text)
    
    def addQuote(self, post):
        self.quotings.add(post)
        self.save()

class Tag(models.Model):
    name = models.CharField(max_length=150)
    posts = models.ManyToManyField(ForumPost, related_name='tags', blank=True)
    maintopics = models.ManyToManyField(MainTopic, related_name='tags', blank=True)
    subtopics = models.ManyToManyField(SubTopic, related_name='tags', blank=True)

    def __str__(self):
        return self.name
    
    def addPost(self, post):
        self.posts.add(post)
        self.save()

    def removePost(self, post):
        self.posts.remove(post)
        self.save()

    def addMT(self, maintopic):
        self.maintopics.add(maintopic)
        self.save()

    def removeMT(self, maintopic):
        self.maintopics.remove(maintopic)
        self.save()

    def addST(self, subtopic):
        self.subtopics.add(subtopic)
        self.save()

    def removeST(self, subtopic):
        self.subtopics.remove(subtopic)
        self.save()
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications", null=True)
    text = models.TextField()
    is_notified = models.BooleanField(default=False)

    def __str__(self):
        return self.text
    
    def setNotified(self, status):
        self.is_notified = status
        self.save()

class Chat(models.Model):
    name = models.CharField(max_length=1000)
    users = models.ManyToManyField(User, related_name="chats", blank=True)

    def __str__(self):
        return self.name
    
class Message(models.Model):
    text = models.TextField()
    date = models.TextField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages", null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages", null=True)

    def __str__(self):
        return self.text
    