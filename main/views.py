from django.shortcuts import render, redirect
from .forms import *
from .models import *
import requests
import json
from django.http import HttpResponse
import datetime
import csv
import ast
from django.contrib.auth import authenticate, login

# Create your views here.
def home(response):
    return render(response, 'index.html', {})

def createPost(response, id):
    if response.method == "POST":
        form = CreatePost(response.POST, response.FILES)

        if form.is_valid():
            title = form.cleaned_data["title"]
            text = form.cleaned_data["text"]
            image = form.cleaned_data["image"]
            post = ForumPost(title=title, text=text, image=image)
            post.save()
            response.user.posts.add(post)
            subtopic = SubTopic.objects.get(id =id)
            subtopic.posts.add(post)
            subtopic.PostCount += 1
            maintopic = subtopic.mainTopic
            maintopic.PostCount += 1
            subtopic.save()
            maintopic.save()

        return redirect('/subtopic/' +str(id))
    else:
        subtopic = SubTopic.objects.get(id =id)
        createpost = CreatePost()
    return render(response, 'createPost.html', {'createpost': createpost, 'subtopic': subtopic})

def deletePost(response, id):
    post = ForumPost.objects.get(id=id)
    subtopic = post.topic
    if post.user == response.user:
        post.delete()
    subtopic.PostCount -= 1
    maintopic = subtopic.mainTopic
    maintopic.PostCount -= 1
    subtopic.save()
    maintopic.save()
    return redirect('/subtopic/'+str(subtopic.id))

def editPost(response, id):
    if response.method == "POST":
        form = CreatePost(response.POST, response.FILES)

        if form.is_valid():
            post = ForumPost.objects.get(id=id)
            post.title = form.cleaned_data["title"]
            post.text = form.cleaned_data["text"]
            post.image = form.cleaned_data["image"]
            post.save()
            subtopic = post.topic
        return redirect('/subtopic/' +str(subtopic.id))
    else:
        post = ForumPost.objects.get(id=id)
        subtopic = post.topic
        editpost = CreatePost(initial={'title': post.title, 'text': post.text, 'image': post.image})
    return render(response, 'editPost.html', {'editpost': editpost, 'subtopic':subtopic})

def searchPost(response):
    id = response.POST['id']
    searchInput = response.POST['search'].rstrip()
   
    subtopic = SubTopic.objects.get(id=id) 
    maintopic = subtopic.mainTopic
    posts = []
    if searchInput != "":
        for post in subtopic.posts.all():
            if searchInput.lower() in post.title.lower():
                posts.append(post)
    return render(response, 'subtopic.html', {'subtopic': subtopic, 'maintopic': maintopic, 'posts': posts})



def weather(response):
    city = "Singapore"
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=2f4e8d6ef5b417a779cc2ea7404460fd'
    list_of_data = requests.get(url.format(city)).json()

    url2 = 'https://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&appid=2f4e8d6ef5b417a779cc2ea7404460fd'
    forecast_data = requests.get(url2.format(city)).json()
    uv_data = None
    air_pollution_data = None

    if response.method == 'POST':
        if(response.POST.get('city')) == None:
            latitude = response.POST['latitude']
            longitude = response.POST['longitude']
            url = 'https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&units=metric&appid=2f4e8d6ef5b417a779cc2ea7404460fd'
            list_of_data = requests.get(url.format(latitude, longitude)).json()

            url2 = 'https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&units=metric&appid=2f4e8d6ef5b417a779cc2ea7404460fd'
            forecast_data = requests.get(url2.format(latitude, longitude)).json()

            url3 = 'http://api.openweathermap.org/data/2.5/air_pollution?lat={}&lon={}&appid=2f4e8d6ef5b417a779cc2ea7404460fd'
            air_pollution_data = requests.get(url3.format(latitude, longitude)).json()

            url4 = 'https://api.openuv.io/api/v1/uv?lat={}&lng={}&alt=100&dt='
            headers = {
                "x-access-token": "openuv-99grlneq2l6a-io",
                "Content-Type": "application/json",
            }
            uv_data = requests.get(url4.format(latitude, longitude), headers=headers).json()

        else:
            city = response.POST['city']
            if(city == ""):
                city = "Singapore"
            url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=2f4e8d6ef5b417a779cc2ea7404460fd'
            list_of_data = requests.get(url.format(city)).json()  

            url2 = 'https://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&appid=2f4e8d6ef5b417a779cc2ea7404460fd'
            forecast_data = requests.get(url2.format(city)).json()

    if list_of_data['cod'] != '404':
        dateNtime = str(datetime.datetime.fromtimestamp(list_of_data['dt'])).split(" ")
        date = dateNtime[0]
        timestring = dateNtime[1][0:5]
        day = datetime.datetime.fromtimestamp(list_of_data['dt']).strftime('%A')
        sunrise = str(datetime.datetime.fromtimestamp(list_of_data['sys']['sunrise'])).split(" ")[1][0:5]
        sunset = str(datetime.datetime.fromtimestamp(list_of_data['sys']['sunset'])).split(" ")[1][0:5]
        data = {
            'cod': str(list_of_data['cod']),                
            'date': date,
            'time': timestring,
            'city' : str(list_of_data['name']) ,
            'day': day,
            'temp': str(list_of_data['main']['temp']) + '°C',
            'feels_like': str(list_of_data['main']['feels_like']) + '°C',
            'pressure': str(list_of_data['main']['pressure']),
            'humidity': str(list_of_data['main']['humidity']),
            'windspeed': str(list_of_data['wind']['speed']),
            'main':str(list_of_data['weather'][0]['main']),
            'description': str(list_of_data['weather'][0]['description']),
            'icon': list_of_data['weather'][0]['icon'],
            'sunrise': sunrise,
            'sunset': sunset,
        }
        if uv_data:
            data['uv'] = uv_data['result']['uv']
            print(data['uv'])

        if air_pollution_data:
            data['air_quality'] =  getQuality(int(air_pollution_data['list'][0]['main']['aqi'])) 
            data['air_pollution_component'] = air_pollution_data['list'][0]['components']
    else:
        data = {'message': str(list_of_data['message']), 'cod': str(list_of_data['cod'])}

   
    
    if forecast_data['cod'] != '404':
        three_hours = forecast_data['list'][0]
        Hours = []
        threeHour = {
            'time': str(datetime.datetime.fromtimestamp(three_hours['dt'])).split(" ")[1][0:5],
            'color': color(str(datetime.datetime.fromtimestamp(three_hours['dt'])).split(" ")[1][0:5]),
            'temp': str(three_hours['main']['temp']) + '°C',
            'windspeed': str(three_hours['wind']['speed']),
            'icon': three_hours['weather'][0]['icon']
        }
        six_hours = forecast_data['list'][1]
        sixHour = {
            'time': str(datetime.datetime.fromtimestamp(six_hours['dt'])).split(" ")[1][0:5],
            'color': color(str(datetime.datetime.fromtimestamp(six_hours['dt'])).split(" ")[1][0:5]),
            'temp': str(six_hours['main']['temp']) + '°C',
            'windspeed': str(six_hours['wind']['speed']),
            'icon': six_hours['weather'][0]['icon']
        }
        nine_hours = forecast_data['list'][2]
        nineHour = {
            'time': str(datetime.datetime.fromtimestamp(nine_hours['dt'])).split(" ")[1][0:5],
            'color': color(str(datetime.datetime.fromtimestamp(nine_hours['dt'])).split(" ")[1][0:5]),
            'temp': str(nine_hours['main']['temp']) + '°C',
            'windspeed': str(nine_hours['wind']['speed']),
            'icon': nine_hours['weather'][0]['icon']
        }
        twelve_hours = forecast_data['list'][3]
        twelveHour = {
            'time': str(datetime.datetime.fromtimestamp(twelve_hours['dt'])).split(" ")[1][0:5],
            'color': color(str(datetime.datetime.fromtimestamp(twelve_hours['dt'])).split(" ")[1][0:5]),
            'temp': str(twelve_hours['main']['temp']) + '°C',
            'windspeed': str(twelve_hours['wind']['speed']),
            'icon': twelve_hours['weather'][0]['icon']
        }
        fifteen_hours = forecast_data['list'][4]
        fifteenHour = {
            'time': str(datetime.datetime.fromtimestamp(fifteen_hours['dt'])).split(" ")[1][0:5],
            'color': color(str(datetime.datetime.fromtimestamp(fifteen_hours['dt'])).split(" ")[1][0:5]),
            'temp': str(fifteen_hours['main']['temp']) + '°C',
            'windspeed': str(fifteen_hours['wind']['speed']),
            'icon': fifteen_hours['weather'][0]['icon']
        }
        Hours.append(threeHour)
        Hours.append(sixHour)
        Hours.append(nineHour)
        Hours.append(twelveHour)
        Hours.append(fifteenHour)


        day1 = forecast_data['list'][8]
        dayOne = {
            'date': str(datetime.datetime.fromtimestamp(day1['dt'])).split(" ")[0],
            'day': datetime.datetime.fromtimestamp(day1['dt']).strftime('%A'),
            'temp': str(day1['main']['temp']) + '°C',
            'icon': day1['weather'][0]['icon']
        }
        day2 = forecast_data['list'][16]
        dayTwo = {
            'date': str(datetime.datetime.fromtimestamp(day2['dt'])).split(" ")[0],
            'day': datetime.datetime.fromtimestamp(day2['dt']).strftime('%A'),
            'temp': str(day2['main']['temp']) + '°C',
            'icon': day2['weather'][0]['icon']
        }
        day3 = forecast_data['list'][24]
        dayThree = {
            'date': str(datetime.datetime.fromtimestamp(day3['dt'])).split(" ")[0],
            'day': datetime.datetime.fromtimestamp(day3['dt']).strftime('%A'),
            'temp': str(day3['main']['temp']) + '°C',
            'icon': day3['weather'][0]['icon']
        }
        day4 = forecast_data['list'][32]
        dayFour = {
            'date': str(datetime.datetime.fromtimestamp(day4['dt'])).split(" ")[0],
            'day': datetime.datetime.fromtimestamp(day4['dt']).strftime('%A'),
            'temp': str(day4['main']['temp']) + '°C',
            'icon': day4['weather'][0]['icon']
        }
        day5 = forecast_data['list'][39]
        dayFive = {
            'date': str(datetime.datetime.fromtimestamp(day5['dt'])).split(" ")[0],
            'day': datetime.datetime.fromtimestamp(day5['dt']).strftime('%A'),
            'temp': str(day5['main']['temp']) + '°C',
            'icon': day5['weather'][0]['icon']
        }
        Days = []
        Days.append(dayOne)
        Days.append(dayTwo)
        Days.append(dayThree)
        Days.append(dayFour)
        Days.append(dayFive)
    else:
        Hours = []
        Days = []
    return render(response, 'weather.html', {'data':data, 'Hours': Hours, 'Days': Days})

def getQuality(index):
    if(index == 1):
        return "Good"
    elif(index == 2):
        return "Fair"
    elif(index == 3):
        return "Moderate"
    elif(index == 4):
        return "Poor"
    elif(index == 5):
        return "Very Poor"
    else:
        return "Not Available"

def search1(response):
    file = open("static/crags.csv")
    csvreader = csv.reader(file)
    crags = []
    for row in csvreader:
        data = {
            'country': row[0],
            'region': row[1],
            'name': row[2],
            'desc': row[3],
            'rocktype': row[4],
            'altitude': row[5][:-1]
        }
        crags.append(data)

    countries = []
    for data in crags:
        if data['country'] not in countries:
            countries.append(data['country'])
    searchInput = ""
    condition = ""
    sort = ""
    locations = []

    limitSearchHistory = SearchHistory.objects.filter(user=response.user).order_by('-id')[:20]

    if response.method == 'POST':
        searchInput = response.POST['search']
        
        user = response.user
        exist = False
        for history in user.searchHistories.all():
            if searchInput == history.text:
                exist = True

        if not exist:
            SearchHistory.objects.create(user=user, text=searchInput)

        searchList = []
        if searchInput != "":
            for crag in crags:
                if searchInput in crag['name']:
                    searchList.append(crag)
            crags = searchList
        
        filterlist1 = []
        if(response.POST.get('condition') != None):
            condition = response.POST['condition']
            if(condition != '0'):
                for crag in crags:
                    if int(crag['altitude']) >= int(condition):
                        filterlist1.append(crag)
                crags = filterlist1

        filterlist2 = []
        if(response.POST.get('location') != None):
            locations = response.POST.getlist('location')
            for country in locations:
                for crag in crags:
                    if crag['country'] == country:
                        filterlist2.append(crag)
            crags = filterlist2

        if(response.POST.get('sort') != None):
            sort = response.POST['sort']
            if(sort == 'altAsc'):
                sortCrags = sorted(crags, key=lambda x: int(x['altitude']))
                print(sortCrags)
                crags = sortCrags
            elif(sort == 'altDsc'):
                sortCrags = sorted(crags, key=lambda x: int(x['altitude']), reverse=True)
                crags = sortCrags 
            else:
                sortCrags = crags
                crags = sortCrags
    return render(response, 'search.html', {'crags':crags, 'countries': countries, 'search':searchInput, 'locations': locations, 'condition': condition, 'sort':sort, 'limitSearchHistory': limitSearchHistory})


def color(time):
    if(time >= '06:00' and time < '08:00'):
        return "orange"
    elif(time >= '08:00' and time < '17:00' ):
        return "blue"
    elif(time >= '17:00' and time < '19:00'):
        return "orange"
    else:
        return "purple"

def forum1(response):
    sections = Section.objects.all()
    return render(response, "forum.html", {'sections': sections})

def topic(response, id):
    maintopic = MainTopic.objects.get(id=id)   
    return render(response, 'topic.html', {'maintopic': maintopic})

def subtopic(response, id):
    subtopic = SubTopic.objects.get(id=id) 
    maintopic = subtopic.mainTopic
    posts = subtopic.posts.all()
    flaggedPosts = []
    for flaggedPost in response.user.flaggedPosts.all():
        flaggedPosts.append(flaggedPost.post)
    return render(response, 'subtopic.html', {'subtopic': subtopic, 'maintopic': maintopic, 'posts':posts, 'flaggedPosts': flaggedPosts})

def contact(response):
    contactus = ContactUsForm()
    if response.method == 'POST':
        form = ContactUsForm(response.POST)

        if form.is_valid():
            firstname = form.cleaned_data["firstname"]
            lastname = form.cleaned_data["lastname"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]
            contactusObj = ContactUs(firstname=firstname, lastname=lastname, email=email, message=message)
            contactusObj.save()
        return redirect('/success')
    return render(response, "contact.html", {'contactus': contactus})

def success(response):
    contactus = ContactUsForm()
    success = "Successfully Sent!"
    return render(response, "contact.html", {'contactus': contactus, 'success':success})

def loginUser(response):
    signupform = SignupForm()
    if response.method == 'POST':
        if(response.POST.get('loginUsername') != None ) and (response.POST.get('password') != None ):
            username = response.POST['loginUsername']
            password = response.POST['password']
            user = authenticate(response, username=username, password=password)
            if user is None:
                return render(response, "login.html", {'error': "Invalid username or password", "signupform": SignupForm()})
            if(user.account.suspended):
                return render(response, "login.html", {'error': "Account Suspended or Deleted", "signupform": SignupForm()})
            login(response, user)
            return redirect("/home")

        if (response.POST.get('username') != None) and (response.POST.get('password1') != None) and (response.POST.get('password2') != None):
            details = {
                'username': response.POST['username'],
                'email': response.POST['email'],
                'first_name': response.POST['first_name'],
                'last_name': response.POST['last_name'],
                'password1': response.POST['password1'],
                'password2': response.POST['password2']
            }
            signupform = SignupForm(details)
            if signupform.is_valid():
                signupform.save()
                user = User.objects.get(username=signupform.cleaned_data['username'])
                Account.objects.create(user=user)
                return render(response, "login.html", {'signupform': signupform, 'successful': 'Account Created Successfully'})
            else:
                errorsDetail = []
                for field, errors in signupform.errors.items():
                    for error in errors:
                        print(f"Field: {field}, Error: {error}")
                        errorsDetail.append(error)
                return render(response, "login.html", {'signupform': signupform, 'successful': 'Create Account Failed, Please Try Again!', 'errorDetails':errorsDetail})
        
    return render(response, "login.html", {'signupform': signupform})

def ARroute(response):
    return render(response, "ARRoute.html")

def profile(response):
    return render(response, "profile.html")

def createSection(response):
    if response.method == "POST":
        form = CreateSection(response.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            section = Section(title=title)
            section.save()

        return redirect('/forum/')
    else:
        createsection = CreateSection()
    return render(response, 'createSection.html', {'createsection':createsection})

def deleteSection(response, id):
    section = Section.objects.get(id=id)
    if(response.user.account.is_admin):
        section.delete()
    return redirect('/forum/')

def createTopic(response, id):
    if response.method == "POST":
        form = CreateTopic(response.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            section = Section.objects.get(id =id)
            maintopic = MainTopic(section=section, title=title, description=description, PostCount=0, SubTopicCount=0)
            maintopic.save()
            section.save()
        return redirect('/forum/')
    else:
        createtopic = CreateTopic()
    return render(response, 'createTopic.html', {'createtopic': createtopic})

def deleteTopic(response, id):
    maintopic = MainTopic.objects.get(id=id)
    if(response.user.account.is_admin):
        maintopic.delete()
    return redirect('/forum/')

def createSubtopic(response, id):
    if response.method == "POST":
        form = CreateTopic(response.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            maintopic = MainTopic.objects.get(id =id)
            subtopic = SubTopic(mainTopic=maintopic, title=title, description=description, PostCount=0)
            maintopic.SubTopicCount += 1
            subtopic.save()
            maintopic.save()

        return redirect('/topic/' +str(id))
    else:
        maintopic = MainTopic.objects.get(id =id)
        createtopic = CreateTopic()
    return render(response, 'createSubtopic.html', {'createtopic': createtopic, 'maintopic': maintopic})

def deleteSubtopic(response, id):
    subtopic = SubTopic.objects.get(id=id)
    maintopic = subtopic.mainTopic
    maintopic.SubTopicCount -= 1
    maintopic.save()
    if(response.user.account.is_admin):
        subtopic.delete()
    return redirect('/topic/'+str(maintopic.id))

def admin(response):
    contactus = ContactUs.objects.all()
    return render(response, 'admin.html', {'contactus':contactus})

def markContactDone(response, id):
    contactus = ContactUs.objects.get(id=id)
    if(response.user.account.is_admin):
        contactus.status = True
        contactus.save()
    return redirect('/adminPortal')

def editLogin(response, id):
    if(response.user != User.objects.get(id=id)):
        return redirect('/profile/')
    if response.method == "POST":
        form = EditLoginForm(response.POST)
        if form.is_valid():
            user = User.objects.get(id=id)
            username = form.cleaned_data["username"]
            users = User.objects.all()
            for userCheck in users:
                if(user != userCheck ):
                    if(userCheck.username == username):
                        editLoginform = EditLoginForm(initial={'username': user.username, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name})
                        return render(response, 'editLogin.html', {'editLoginform':editLoginform, 'fail':"Username Exist, Please Choose Another One!"})
            user.username = form.cleaned_data["username"]
            user.email = form.cleaned_data["email"]
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save()
            return redirect('/profile/')
    else:
        user = User.objects.get(id=id)
        editLoginform = EditLoginForm(initial={'username': user.username, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name})
    return render(response, 'editLogin.html', {'editLoginform':editLoginform})


def viewProfile(response, id):
    user = User.objects.get(id=id)
    return render(response, 'viewProfile.html', {'userProf':user})

def flagPost(response, id):
    post = ForumPost.objects.get(id=id)
    exist = False
    for flaggedPost in FlaggedPost.objects.all():
        if post == flaggedPost.post:
            exist = True
    if exist:
        flaggedPost = FlaggedPost.objects.get(post=post)
        flaggedPost.users.add(response.user)
    else:
        flaggedPost = FlaggedPost(post = post)
        flaggedPost.save()
        flaggedPost.users.add(response.user)

    subtopic = post.topic
    #print(FlaggedPost.objects.all())
    print(response.user.flaggedPosts.all())

    return redirect("/subtopic/"+str(subtopic.id))

def viewAccounts(response):
    users = []
    if response.user.account.is_admin:
        users = User.objects.all()
    return render(response, 'viewAccounts.html', {'users':users})

def suspendAccount(response, id):
    if response.user.account.is_admin:
        userObj = User.objects.get(id=id)
        userObj.account.updateSuspend(status=True)
    return redirect('/viewAccounts/')

def activateAccount(response, id):
    if response.user.account.is_admin:
        userObj = User.objects.get(id=id)
        userObj.account.updateSuspend(status=False)
    return redirect('/viewAccounts/')

def searchAccount(response):
    searchInput = response.POST['search'].rstrip()
   
    users = []
    if response.user.account.is_admin:
        if searchInput != "":
            for userObj in User.objects.all():
                if searchInput.lower() in userObj.username.lower():
                    users.append(userObj)
    return render(response, 'viewAccounts.html', {'users':users})

def suspendAccountByUser(response, id):
    user = User.objects.get(id=id)
    if response.user == user:
        user.account.updateSuspend(status=True)
    return redirect('/logout/')


def createClimbActivity(response):
    if response.method == "POST":
        form = CreateClimbingActivity(response.POST)

        if form.is_valid():
            user = response.user
            locName = form.cleaned_data["locName"]
            distance = form.cleaned_data["distance"]
            date = form.cleaned_data["date"]
            climbActivity = ClimbingActivity(user=user, locName=locName, distance=distance, date=date) 
            climbActivity.save()
            user.account.updateRouteAndDist()
            checkAchievement(user)
        return redirect('/profile/')
    else:
        createclimbactivity = CreateClimbingActivity()
    return render(response, 'createClimbActivity.html', {'createclimbactivity': createclimbactivity})

def checkAchievement(user):
    #Beginner
    if(user.account.totalRoute >= 1):
        achievement = Achievement.objects.get(title='Beginner Climber')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)
    
    #Intermediate
    if(user.account.totalRoute >= 20):
        achievement = Achievement.objects.get(title='Intermediate Climber')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)

    #Experienced
    if(user.account.totalRoute >= 50):
        achievement = Achievement.objects.get(title='Experienced Climber')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)

    #Advanced
    if(user.account.totalRoute >= 100):
        achievement = Achievement.objects.get(title='Advanced Climber')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)

    #Veteran
    if(user.account.totalRoute >= 150):
        achievement = Achievement.objects.get(title='Veteran Climber')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)

    #Master
    if(user.account.totalRoute >= 200):
        achievement = Achievement.objects.get(title='Master Climber')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)

    #Pioneer
    if(user.account.totalRoute >= 300):
        achievement = Achievement.objects.get(title='Pioneer Climber')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)

    #Elite
    if(user.account.totalRoute >= 500):
        achievement = Achievement.objects.get(title='Elite Climber')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)

    #Legendary
    if(user.account.totalRoute >= 1000):
        achievement = Achievement.objects.get(title='Legendary Climber')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)

    #1000-Meter Explorer
    if(user.account.totalDistance >= 1000):
        achievement = Achievement.objects.get(title='1000-Meter Explorer')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)

    #10000-Meter Explorer
    if(user.account.totalDistance >= 10000):
        achievement = Achievement.objects.get(title='10000-Meter Explorer')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)

    #100000-Meter Explorer
    if(user.account.totalDistance >= 100000):
        achievement = Achievement.objects.get(title='100000-Meter Explorer')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)

    #500000-Meter Explorer
    if(user.account.totalDistance >= 500000):
        achievement = Achievement.objects.get(title='500000-Meter Explorer')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)

    #1000000-Meter Explorer
    if(user.account.totalDistance >= 1000000):
        achievement = Achievement.objects.get(title='1000000-Meter Explorer')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)

    #5000000-Meter Explorer
    if(user.account.totalDistance >= 5000000):
        achievement = Achievement.objects.get(title='5000000-Meter Explorer')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)

    #10000000-Meter Explorer
    if(user.account.totalDistance >= 10000000):
        achievement = Achievement.objects.get(title='10000000-Meter Explorer')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)

def editAbout(response, id):
    if(response.user != User.objects.get(id=id)):
        return redirect('/profile/')
    if response.method == "POST":
        form = EditAbout(response.POST)
        if form.is_valid():
            user = User.objects.get(id=id)
            about = form.cleaned_data["about"]
            user.account.setAbout(about)
            return redirect('/profile/')
    else:
        user = User.objects.get(id=id)
        editabout = EditAbout(initial={'about': user.account.about})
    return render(response, 'editAbout.html', {'editabout':editabout})

def followUser(response, id):
    user = response.user
    userToFollow = User.objects.get(id=id)
    user.account.addFollowing(userToFollow)
    userToFollow.account.addFollower(user)
    return redirect('/viewProfile/'+str(id))

def viewFollowers(response, id):
    user = User.objects.get(id=id)
    description = 'Followers of '+ str(user)
    follows = user.account.followers.all()
    return render(response, 'viewFollow.html', {'description': description, 'follows':follows})

def viewFollowings(response, id):
    user = User.objects.get(id=id)
    description = 'Followings of '+ str(user)
    follows = user.account.followings.all()
    return render(response, 'viewFollow.html', {'description': description, 'follows':follows})

def unfollowUser(response, id):
    user = response.user
    userToUnfollow = User.objects.get(id=id)
    user.account.removeFollowing(userToUnfollow)
    userToUnfollow.account.removeFollower(user)
    return redirect('/viewProfile/'+str(id))

def editSocialMedia(response, id):
    if(response.user != User.objects.get(id=id)):
        return redirect('/profile/')
    if response.method == "POST":
        form = EditSocialMedia(response.POST)
        if form.is_valid():
            user = User.objects.get(id=id)
            facebook = form.cleaned_data["facebook"]
            youtube = form.cleaned_data["youtube"]
            user.account.updateFacebook(facebook)
            user.account.updateYoutube(youtube)
            return redirect('/profile/')
    else:
        user = User.objects.get(id=id)
        editSocialMedia = EditSocialMedia(initial={'facebook': user.account.facebookLink, 'youtube': user.account.youtubeLink})
    return render(response, 'editSocialMedia.html', {'editSocialMedia':editSocialMedia})

def deleteSearchHistory(response, id):
    searchHistory = SearchHistory.objects.get(id=id)
    if searchHistory.user == response.user:
        searchHistory.delete()
    return redirect('/search/')

def viewPostByUser(response, id):
    userObj = User.objects.get(id=id)
    posts = userObj.posts.all()
    if response.user.account.is_admin:
        return render(response, 'viewPostByUser.html', {'userObj':userObj, 'posts':posts})
    else:
        return redirect('/home/')

def searchPostByUser(response, id):
    searchInput = response.POST['search'].rstrip()
    userObj = User.objects.get(id=id)
    posts = []
    if searchInput != "":
        for post in userObj.posts.all():
            if searchInput.lower() in post.title.lower():
                posts.append(post)
    return render(response, 'viewPostByUser.html', {'userObj': userObj, 'posts': posts})





"""
def search(response):
    form = SearchCrag()
    countries = Country.objects.all()
    return render(response, 'search.html', {'form':form, 'countries': countries})

def result(response):
    if response.method == "POST":
        form = SearchCrag(response.POST)

        if form.is_valid():
            n = form.cleaned_data["name"]
            countryFilter = response.POST['country']
            result = []
            if countryFilter != 'empty':
                country = Country.objects.get(name = countryFilter)
                crags = country.crags.all()
                for crag in crags:
                    if n in crag.name:
                            result.append(crag)
            else:
                c = Country.objects.all()
                for country in c:
                    crags = country.crags.all()
                    for crag in crags:
                        if n in crag.name:
                                result.append(crag)
            if not result:
                return render(response, 'result.html', {'empty':'No Result Found'})
            else:
                return  render(response, 'result.html', {'result': result})
    
    return redirect('/result')

def createCountry(response):
    if response.method == "POST":
        form = CreateCountry(response.POST)

        if form.is_valid():
            n = form.cleaned_data["name"]
            c = Country(name=n)
            c.save()

        return redirect("/country")
    else:
        form = CreateCountry()
    return render(response, 'createCountry.html', {'form': form})

def index(response, id):
    cs = Country.objects.get(id=id)

    if response.method == "POST":
        if response.POST.get("newCrags"):
            name = response.POST.get("new")

            if len(name) > 2:
                cs.crags.create(name=name)
            else:
                print("invalid")
    return render(response, 'countryDetail.html', {'cs':cs})
    
    

def list(response):
    cs = Country.objects.all()
    return render(response, 'countries.html', {'cs':cs})


def forum(response):
    forums = ForumPost.objects.all()
    return render(response, 'forum.html', {'posts': forums})

def comment(response, id):
    post = ForumPost.objects.get(id=id)
    
    form = CreateComment(response.POST)

    if form.is_valid():
        text = form.cleaned_data["text"]
        post.comments.create(text=text)

        return redirect("/forum")
    
    return render(response, 'createComment.html', {'form':form, 'post':post})

def deletePost1(response, id):
    post = ForumPost.objects.get(id=id)

    if post in response.user.posts.all() or response.user.is_staff:
        p = ForumPost.objects.get(id=id)
        p.delete()

    return redirect('/forum')
"""