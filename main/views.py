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
from django.utils import timezone
from datetime import datetime as dti, timedelta

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
            inputdate = response.POST['date'][:24]
            if 'create_button' in response.POST:
                post = ForumPost(title=title, text=text, image=image,date=inputdate)
                post.save()
                response.user.posts.add(post)
                subtopic = SubTopic.objects.get(id =id)
                subtopic.posts.add(post)
                subtopic.addPostCount()
                maintopic = subtopic.mainTopic
                maintopic.addPostCount()
            elif 'save_button' in response.POST:
                subtopic = SubTopic.objects.get(id =id)
                user = response.user
                draft = PostDraft(title=title, text=text, image=image, user=user, topic =subtopic)
                draft.save()

        return redirect('/subtopic/' +str(id))
    else:
        subtopic = SubTopic.objects.get(id =id)
        createpost = CreatePost()
    return render(response, 'createPost.html', {'createpost': createpost, 'subtopic': subtopic})

def getDateTime(date):
    month_map = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }

    dates = date.split()
    day = int(dates[2])
    month = month_map.get(dates[1])
    year = int(dates[3])

    hours, minutes, seconds = map(int, dates[4].split(':'))

    return dti(year, month, day, hours, minutes, seconds)

def deletePost(response, id):
    post = ForumPost.objects.get(id=id)
    subtopic = post.topic
    if post.user == response.user or response.user.account.is_admin:
        post.delete()
    subtopic.minusPostCount()
    maintopic = subtopic.mainTopic
    maintopic.minusPostCount()
    return redirect('/subtopic/'+str(subtopic.id))

def editPost(response, id):
    if response.method == "POST":
        form = CreatePost(response.POST, response.FILES)

        if form.is_valid():
            post = ForumPost.objects.get(id=id)
            post.title = form.cleaned_data["title"]
            post.text = form.cleaned_data["text"]
            image = form.cleaned_data["image"]
            if image == "" or image == None:
                image = post.image
            post.image = image
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
        offset_seconds = list_of_data['timezone']

        #datentime = list_of_data['dt']
        #dateNtime_utc = dti.utcfromtimestamp(list_of_data['dt'])
        #adjusted_datetime = dti.utcfromtimestamp(list_of_data['dt']) + timedelta(seconds=offset_seconds)
        finaldateNtime = timezone.make_aware((dti.utcfromtimestamp(list_of_data['dt']) + timedelta(seconds=offset_seconds)), timezone.utc)

        #sunrise_time = list_of_data['sys']['sunrise']
        #sunrise_utc = dti.utcfromtimestamp(list_of_data['sys']['sunrise'])
        adjusted_sunrise = dti.utcfromtimestamp(list_of_data['sys']['sunrise']) + timedelta(seconds=offset_seconds)

        #sunset_time = list_of_data['sys']['sunset']
        #sunset_utc = dti.utcfromtimestamp(list_of_data['sys']['sunset'])
        adjusted_sunset= dti.utcfromtimestamp(list_of_data['sys']['sunset']) + timedelta(seconds=offset_seconds)

        date = finaldateNtime.date()
        timestring = finaldateNtime.time()
        day = finaldateNtime.strftime('%A')
        sunrise = timezone.make_aware(adjusted_sunrise, timezone.utc).time()
        sunset = timezone.make_aware(adjusted_sunset, timezone.utc).time()
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

        if air_pollution_data:
            data['air_quality'] =  getQuality(int(air_pollution_data['list'][0]['main']['aqi'])) 
            data['air_pollution_component'] = air_pollution_data['list'][0]['components']
    else:
        data = {'message': str(list_of_data['message']), 'cod': str(list_of_data['cod'])}

   
    
    if forecast_data['cod'] != '404':
        offset_seconds = forecast_data['city']['timezone']
        three_hours = forecast_data['list'][0]
        Hours = []
        threeHour = {
            #'time': str(datetime.datetime.fromtimestamp(three_hours['dt'])).split(" ")[1][0:5],
            'time': timezone.make_aware((dti.utcfromtimestamp(three_hours['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).time(),
            'color': color(timezone.make_aware((dti.utcfromtimestamp(three_hours['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).time()),
            'temp': str(three_hours['main']['temp']) + '°C',
            'windspeed': str(three_hours['wind']['speed']),
            'icon': three_hours['weather'][0]['icon']
        }
        six_hours = forecast_data['list'][1]
        sixHour = {
            'time': timezone.make_aware((dti.utcfromtimestamp(six_hours['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).time(),
            'color': color(timezone.make_aware((dti.utcfromtimestamp(six_hours['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).time()),
            'temp': str(six_hours['main']['temp']) + '°C',
            'windspeed': str(six_hours['wind']['speed']),
            'icon': six_hours['weather'][0]['icon']
        }
        nine_hours = forecast_data['list'][2]
        nineHour = {
            'time': timezone.make_aware((dti.utcfromtimestamp(nine_hours['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).time(),
            'color': color(timezone.make_aware((dti.utcfromtimestamp(nine_hours['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).time()),
            'temp': str(nine_hours['main']['temp']) + '°C',
            'windspeed': str(nine_hours['wind']['speed']),
            'icon': nine_hours['weather'][0]['icon']
        }
        twelve_hours = forecast_data['list'][3]
        twelveHour = {
            'time': timezone.make_aware((dti.utcfromtimestamp(twelve_hours['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).time(),
            'color': color(timezone.make_aware((dti.utcfromtimestamp(twelve_hours['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).time()),
            'temp': str(twelve_hours['main']['temp']) + '°C',
            'windspeed': str(twelve_hours['wind']['speed']),
            'icon': twelve_hours['weather'][0]['icon']
        }
        fifteen_hours = forecast_data['list'][4]
        fifteenHour = {
            'time': timezone.make_aware((dti.utcfromtimestamp(fifteen_hours['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).time(),
            'color': timezone.make_aware((dti.utcfromtimestamp(fifteen_hours['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).time(),
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
            'date': timezone.make_aware((dti.utcfromtimestamp(day1['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).date(),
            'day': timezone.make_aware((dti.utcfromtimestamp(day1['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).date().strftime('%A'),
            'temp': str(day1['main']['temp']) + '°C',
            'icon': day1['weather'][0]['icon']
        }
        day2 = forecast_data['list'][16]
        dayTwo = {
            'date': timezone.make_aware((dti.utcfromtimestamp(day2['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).date(),
            'day': timezone.make_aware((dti.utcfromtimestamp(day2['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).strftime('%A'),
            'temp': str(day2['main']['temp']) + '°C',
            'icon': day2['weather'][0]['icon']
        }
        day3 = forecast_data['list'][24]
        dayThree = {
            'date': timezone.make_aware((dti.utcfromtimestamp(day3['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).date(),
            'day': timezone.make_aware((dti.utcfromtimestamp(day3['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).strftime('%A'),
            'temp': str(day3['main']['temp']) + '°C',
            'icon': day3['weather'][0]['icon']
        }
        day4 = forecast_data['list'][32]
        dayFour = {
            'date': timezone.make_aware((dti.utcfromtimestamp(day4['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).date(),
            'day': timezone.make_aware((dti.utcfromtimestamp(day4['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).strftime('%A'),
            'temp': str(day4['main']['temp']) + '°C',
            'icon': day4['weather'][0]['icon']
        }
        day5 = forecast_data['list'][39]
        dayFive = {
            'date': timezone.make_aware((dti.utcfromtimestamp(day5['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).date(),
            'day': timezone.make_aware((dti.utcfromtimestamp(day5['dt']) + timedelta(seconds=offset_seconds)), timezone.utc).strftime('%A'),
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
    #file = open("static/crags.csv")
    #csvreader = csv.reader(file)
    #crags = []
    #for row in csvreader:
    #    Crag.objects.create(country=row[0], region=row[1], name=row[2], desc=row[3], rocktype=row[4], altitude=row[5][:-1])
    crags=Crag.objects.all()
    countries = []
    for crag in crags:
        if crag.country not in countries:
            countries.append(crag.country)
    searchInput = ""
    condition = ""
    sort = ""
    locations = []

    limitSearchHistory = []
    if response.user.is_authenticated:
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
                if searchInput in crag.name:
                    searchList.append(crag)
            crags = searchList
        
        filterlist1 = []
        if(response.POST.get('condition') != None):
            condition = response.POST['condition']
            if(condition != '0'):
                for crag in crags:
                    if int(crag.altitude) >= int(condition):
                        filterlist1.append(crag)
                crags = filterlist1

        filterlist2 = []
        if(response.POST.get('location') != None):
            locations = response.POST.getlist('location')
            for country in locations:
                for crag in crags:
                    if crag.country == country:
                        filterlist2.append(crag)
            crags = filterlist2

        if(response.POST.get('sort') != None):
            sort = response.POST['sort']
            if(sort == 'altAsc'):
                sortCrags = sorted(crags, key=lambda x: int(x.altitude))
                crags = sortCrags
            elif(sort == 'altDsc'):
                sortCrags = sorted(crags, key=lambda x: int(x.altitude), reverse=True)
                crags = sortCrags 
            else:
                sortCrags = crags
                crags = sortCrags
    return render(response, 'search.html', {'crags':crags, 'countries': countries, 'search':searchInput, 'locations': locations, 'condition': condition, 'sort':sort, 'limitSearchHistory': limitSearchHistory})


#def color(time):
#    if(time >= '06:00' and time < '08:00'):
#        return "orange"
#    elif(time >= '08:00' and time < '17:00' ):
#        return "blue"
#    elif(time >= '17:00' and time < '19:00'):
#        return "orange"
#    else:
#        return "purple"
    
def color(time):
    sixam = dti.now().replace(hour=6, minute=0, second=0, microsecond=0)
    nineam = dti.now().replace(hour=9, minute=0, second=0, microsecond=0)
    fivepm = dti.now().replace(hour=17, minute=0, second=0, microsecond=0)
    sevenpm = dti.now().replace(hour=19, minute=0, second=0, microsecond=0)
    if(time >= sixam.time() and time < nineam.time()):
        return "orange"
    elif(time >= nineam.time() and time < fivepm.time()):
        return "blue"
    elif(time >= fivepm.time() and time < sevenpm.time()):
        return "orange"
    else:
        return "purple"
    
def forum1(response):
    sections = Section.objects.all()
    topics = []
    for section in sections:
        for maintopic in section.maintopics.all():
            try:
                latest_post = ForumPost.objects.filter(topic__mainTopic=maintopic).last()
            except ForumPost.DoesNotExist:
                latest_post = None
            topic = {
                'maintopic': maintopic,
                'latest_post': latest_post
            }
            topics.append(topic)
    return render(response, "forum.html", {'sections': sections, 'topics': topics})

def topic(response, id):
    maintopic = MainTopic.objects.get(id=id)   
    maintopic.addView()
    return render(response, 'topic.html', {'maintopic': maintopic})

def subtopic(response, id):
    subtopic = SubTopic.objects.get(id=id) 
    maintopic = subtopic.mainTopic
    posts = subtopic.posts.all()
    flaggedPosts = []
    subtopic.addView()
    if response.user.is_authenticated:
        for flaggedPost in response.user.flaggedPosts.all():
            flaggedPosts.append(flaggedPost.post)
    allFP = []
    for flaggedPost in FlaggedPost.objects.all():
            allFP.append(flaggedPost.post)
    return render(response, 'subtopic.html', {'subtopic': subtopic, 'maintopic': maintopic, 'posts':posts, 'flaggedPosts': flaggedPosts, 'allFP': allFP})

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
                achievement = Achievement.objects.get(title="Totally New")
                user.account.achievements.add(achievement)
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
            maintopic.addSubTopicCount()
            subtopic.save()

        return redirect('/topic/' +str(id))
    else:
        maintopic = MainTopic.objects.get(id =id)
        createtopic = CreateTopic()
    return render(response, 'createSubtopic.html', {'createtopic': createtopic, 'maintopic': maintopic})

def deleteSubtopic(response, id):
    subtopic = SubTopic.objects.get(id=id)
    maintopic = subtopic.mainTopic
    maintopic.minusSubTopicCount()
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

    #Master
    if(user.account.totalRoute >= 200):
        achievement = Achievement.objects.get(title='Master Climber')
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

def viewPost(response, id):
    post = ForumPost.objects.get(id=id)
    post.addView()
    subtopic = post.topic
    commentform = CommentForm()
    posts = ForumPost.objects.all()
    flaggedPosts = []
    if response.user.is_authenticated:
        for flaggedPost in response.user.flaggedPosts.all():
            flaggedPosts.append(flaggedPost.post)
    allFP = []
    for flaggedPost in FlaggedPost.objects.all():
            allFP.append(flaggedPost.post)
    return render(response, 'viewPost.html', {'post':post, 'subtopic':subtopic, 'commentform': commentform, 'posts':posts, 'flaggedPosts': flaggedPosts, 'allFP': allFP})

def comment(response, id):
    if(response.method == 'POST'):
        post = ForumPost.objects.get(id=id)
        user = response.user
    
        form = CommentForm(response.POST)

        if form.is_valid():
            text = form.cleaned_data["text"]
            inputdate = response.POST['date'][:24]
            comment = Comment(post=post, user=user,text=text, date=inputdate)
            comment.save()
            if 'quote' in response.POST:
                inputlist = response.POST.getlist('quote')
                for entry in inputlist:
                    if entry != "None":
                        postID = int(entry)
                        post = ForumPost.objects.get(id=postID)
                        comment.addQuote(post)
    
    return redirect('/viewPost/'+str(id))

def deleteComment(response, id):
    comment = Comment.objects.get(id=id)
    post = comment.post
    if comment.user == response.user or response.user.account.is_admin or (post in response.user.posts.all()):
        comment.delete()
    return redirect('/viewPost/'+str(post.id))

def saveMainTopic(response, id):
    maintopic = MainTopic.objects.get(id=id)
    if maintopic not in response.user.account.savedMainTopics.all():
        response.user.account.addSavedMT(maintopic)
    return redirect('/forum/')

def saveSubTopic(response, id):
    subtopic = SubTopic.objects.get(id=id)
    maintopic = subtopic.mainTopic
    if subtopic not in response.user.account.savedSubTopics.all():
        response.user.account.addSavedST(subtopic)
    return redirect('/topic/'+str(maintopic.id))

def viewSavedTopics(response):
    topics = []
    for maintopic in MainTopic.objects.all():
        try:
            latest_post = ForumPost.objects.filter(topic__mainTopic=maintopic).last()
        except ForumPost.DoesNotExist:
            latest_post = None
        topic = {
            'maintopic': maintopic,
            'latest_post': latest_post
        }
        topics.append(topic)
    return render(response, 'savedTopics.html', {'topics': topics})

def searchAllMTSTP(response):
    if response.method == "GET":
        return redirect('/forum/')
    
    searchInput = response.POST['search'].rstrip()
   
    maintopics = []
    subtopics = []
    posts = []
    topics = []
    

    if searchInput != "":
        for maintopic in MainTopic.objects.all():
            if searchInput.lower() in maintopic.title.lower():
                maintopics.append(maintopic)
                try:
                    latest_post = ForumPost.objects.filter(topic__mainTopic=maintopic).last()
                except ForumPost.DoesNotExist:
                    latest_post = None
                topic = {
                    'maintopic': maintopic,
                    'latest_post': latest_post
                }
                topics.append(topic)

        for subtopic in SubTopic.objects.all():
            if searchInput.lower() in subtopic.title.lower():
                subtopics.append(subtopic)

        for post in ForumPost.objects.all():
            if searchInput.lower() in post.title.lower():
                posts.append(post)
    else:
        maintopics = MainTopic.objects.all()
        subtopics = SubTopic.objects.all()
        posts = ForumPost.objects.all()
        for maintopic in MainTopic.objects.all():
            try:
                latest_post = ForumPost.objects.filter(topic__mainTopic=maintopic).last()
            except ForumPost.DoesNotExist:
                latest_post = None
            topic = {
                'maintopic': maintopic,
                'latest_post': latest_post
            }
            topics.append(topic)

    flaggedPosts = []
    if response.user.is_authenticated:
        for flaggedPost in response.user.flaggedPosts.all():
            flaggedPosts.append(flaggedPost.post)
    allFP = []
    for flaggedPost in FlaggedPost.objects.all():
            allFP.append(flaggedPost.post)
    return render(response, 'searchAllMTSTP.html', {'maintopics': maintopics, 'subtopics': subtopics, 'posts': posts, 'flaggedPosts': flaggedPosts, 'allFP': allFP, 'topics': topics})

def editDraft(response, id):
    if response.method == "POST":
        form = CreatePost(response.POST, response.FILES)
        if form.is_valid():
            draft = PostDraft.objects.get(id=id)
            title = form.cleaned_data["title"]
            text = form.cleaned_data["text"]
            inputdate = response.POST['date'][:24]
            image = form.cleaned_data["image"]
            if image == "" or image == None:
                image = draft.image
            subtopic = PostDraft.objects.get(id=id).topic
            if 'create_button' in response.POST:
                post = ForumPost(title=title, text=text, image=image,date=inputdate)
                post.save()
                response.user.posts.add(post)
                subtopic.posts.add(post)
                subtopic.addPostCount()
                maintopic = subtopic.mainTopic
                maintopic.addPostCount()
                if draft.user == response.user or response.user.account.is_admin:
                    draft.delete()
            elif 'save_button' in response.POST:
                draft = PostDraft.objects.get(id=id)
                draft.title = title
                draft.text = text
                draft.image = image
                draft.save()
        return redirect('/subtopic/' +str(subtopic.id))
    else:
        draft = PostDraft.objects.get(id=id)
        subtopic = draft.topic
        editdraft = CreatePost(initial={'title': draft.title, 'text': draft.text, 'image': draft.image})
    return render(response, 'editDraft.html', {'editdraft': editdraft, 'subtopic':subtopic, 'draft': draft})

def deleteDraft(response, id):
    draft = PostDraft.objects.get(id=id)
    subtopic = draft.topic
    if draft.user == response.user:
        draft.delete()
    return redirect('/subtopic/'+str(subtopic.id))


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