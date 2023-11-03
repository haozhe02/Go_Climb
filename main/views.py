from django.shortcuts import render, redirect
from .forms import *
from .models import *
import requests
#import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import datetime
import csv
#import ast
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import datetime as dti, timedelta
from django.views.decorators.csrf import csrf_exempt
from geopy.geocoders import Nominatim
import environ
from twilio.rest import Client
from django.core.paginator import Paginator

# Create your views here.
def home(response):
    return render(response, 'index.html', {})

def createPost(response, id):
    if response.method == "POST":
        form = CreatePost(response.POST, response.FILES)
        print(response.POST)
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
                checkPostCount(response.user)
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

    hours = int(dates[4].split(':')[0])
    minutes = int(dates[4].split(':')[1])
    seconds = int(dates[4].split(':')[2])

    return dti(year, month, day, hours, minutes, seconds)

def deletePost(response, id):
    post = ForumPost.objects.get(id=id)
    subtopic = post.topic
    if post.user == response.user or response.user.account.is_admin:
        post.delete()
    subtopic.minusPostCount()
    maintopic = subtopic.mainTopic
    maintopic.minusPostCount()

    referring_page = response.META.get('HTTP_REFERER')

    if referring_page:
        return HttpResponseRedirect(referring_page)
    else:
        return redirect('/viewPost/'+str(post.id))

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
        return redirect('/viewPost/' +str(post.id))
    else:
        post = ForumPost.objects.get(id=id)
        editpost = CreatePost(initial={'title': post.title, 'text': post.text, 'image': post.image})
    return render(response, 'editPost.html', {'editpost': editpost, 'post':post})

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
    reminder = None
    hazards = []

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

    if list_of_data['cod'] != '404' and list_of_data['cod'] != '400':
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
            if uv_data['result']['uv'] >= 9:
                hazards.append("UV index Too High, not recommended for climbing!")

        if air_pollution_data:
            data['air_quality'] =  getQuality(int(air_pollution_data['list'][0]['main']['aqi'])) 
            data['air_pollution_component'] = air_pollution_data['list'][0]['components']

            if int(air_pollution_data['list'][0]['main']['aqi']) >= 4:
                hazards.append("Air Quality Not Good, not recommended for climbing!")

        if str(list_of_data['weather'][0]['id']).startswith("7"):
            reminder = "Having " + str(list_of_data['weather'][0]['description']) + " in this area now. Not recommended for climbing"

        if str(list_of_data['weather'][0]['id']).startswith("2"):
            reminder = "It is having THUNDERSTORM in this area now. Not recommended for climbing!"

        if str(list_of_data['weather'][0]['id']).startswith("8"):
            reminder = "Weather is ok in this area now. Climbing is considered safe."

        if str(list_of_data['weather'][0]['id']).startswith("5"):
            reminder = "It is raining now in this area now. Please consider carefully before climbing!"

        if str(list_of_data['weather'][0]['id']).startswith("3"):
            reminder = "It is drizzling in this area now. Please consider carefully before climbing!"

        if str(list_of_data['weather'][0]['id']).startswith("6"):
            reminder = "It is snowing in this area now. Please consider carefully before climbing!"

        if list_of_data['main']['temp'] >= 40:
            hazards.append("Temperature Too High, not recommended for climbing!")

        if list_of_data['main']['temp'] <= -10:
            hazards.append("Temperature Too Low, not recommended for climbing!")

        if list_of_data['wind']['speed'] >= 13:
            hazards.append('Wind Speed Too Strong, not recommended for climbing!')
        
        
    else:
        data = {'message': str(list_of_data['message']), 'cod': str(list_of_data['cod'])}

   
    
    if forecast_data['cod'] != '404' and forecast_data['cod'] != '400':
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
    return render(response, 'weather.html', {'data':data, 'Hours': Hours, 'Days': Days, 'reminder':reminder, 'hazards': hazards})

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

#def get_lat_long(response):
    geolocator = Nominatim(user_agent="my_geocoder")

    file = open("static/crags.csv")
    csvreader = csv.reader(file)
    locations = []
    for row in csvreader:
        locations.append({
            'country': row[0],
            'region': row[1], 
            'name':row[2],
            'desc':row[3], 
            'rocktype':row[4], 
            'altitude':row[5][:-1]
        })

    counter=0
    crags = []
    for loc in locations:
        counter+=1
        print(counter)
        location = geolocator.geocode(loc['name'])
        if location is not None:
            loc['latitude'] = location.latitude
            loc['longitude'] = location.longitude
            crags.append(loc)
    
    for crag in crags:
        Crag.objects.create(country=crag['country'], region=crag['region'], name=crag['name'], desc=crag['desc'], rocktype=crag['rocktype'], altitude=crag['altitude'], latitude=crag['latitude'], longitude=crag['longitude'])
    return JsonResponse({'wow': "wow"})
def clear_all_params(response):
    url = response.path 
    return HttpResponseRedirect(url)

def search1(response):
    #file = open("static/crags.csv")
    #csvreader = csv.reader(file)
    #crags = []
    #for row in csvreader:
    #    Crag.objects.create(country=row[0], region=row[1], name=row[2], desc=row[3], rocktype=row[4], altitude=row[5][:-1])
    crags=Crag.objects.all().order_by('id')
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
        if user.is_authenticated:
            for history in user.searchHistories.all():
                if searchInput == history.text:
                    exist = True

            if not exist:
                SearchHistory.objects.create(user=user, text=searchInput)

        searchList = []
        if searchInput != "":
            for crag in crags:
                if str(searchInput).lower().replace(" ","") in crag.name.lower().replace(" ",""):
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
        p = Paginator(crags, 10)
        crags = p.get_page(1)
        return render(response, 'search.html', {'crags':crags, 'countries': countries, 'search':searchInput, 'locations': locations, 'condition': condition, 'sort':sort, 'limitSearchHistory': limitSearchHistory})

    if response.GET.get('search') != None:
        searchInput = response.GET.get('search')
        
        user = response.user
        exist = False
        if user.is_authenticated:
            for history in user.searchHistories.all():
                if searchInput == history.text:
                    exist = True

            if not exist:
                SearchHistory.objects.create(user=user, text=searchInput)
        
        searchList = []
        if searchInput != "":
            for crag in crags:
                if str(searchInput).lower().replace(" ","") in crag.name.lower().replace(" ",""):
                    searchList.append(crag)
            crags = searchList

    filterlist1 = []
    if(response.GET.get('condition') != None):
        condition = response.GET.get('condition')
        if(condition != '0'):
            for crag in crags:
                if int(crag.altitude) >= int(condition):
                    filterlist1.append(crag)
            crags = filterlist1

    filterlist2 = []
    if(response.GET.get('location') != None):
        locations = response.GET.getlist('location')
        for country in locations:
            for crag in crags:
                if crag.country == country:
                    filterlist2.append(crag)
        crags = filterlist2

    if(response.GET.get('sort') != None):
        sort = response.GET.get('sort')
        if(sort == 'altAsc'):
            sortCrags = sorted(crags, key=lambda x: int(x.altitude))
            crags = sortCrags
        elif(sort == 'altDsc'):
            sortCrags = sorted(crags, key=lambda x: int(x.altitude), reverse=True)
            crags = sortCrags 
        else:
            sortCrags = crags
            crags = sortCrags
    p = Paginator(crags, 10)
    page = response.GET.get('page')
    crags = p.get_page(page)
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
    month = ""
    year = ""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    years = []
    topview = ""
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

    for topic in topics:
        if topic['latest_post'] != None:
            yearitem = topic['latest_post'].date[11:15]
            if yearitem not in years:
                years.append(int(yearitem))
    years.sort()
    return render(response, "forum.html", {'sections': sections, 'topics': topics, 'month': month, 'months': months, 'year': year, 'years': years, 'topview': topview})

def topic(response, id):
    maintopic = MainTopic.objects.get(id=id)   
    maintopic.addView()
    return render(response, 'topic.html', {'maintopic': maintopic})

def subtopic(response, id):
    subtopic = SubTopic.objects.get(id=id) 
    maintopic = subtopic.mainTopic
    posts = subtopic.posts.all().order_by('id')
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
            if(user.account.accountSuspended):
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
                badge = Badge.objects.get(name="New")
                user.account.addAchievement(achievement)
                user.account.addBadge(badge)
                user.account.addShowingBadge(badge)
                for userObj in User.objects.all():
                    if userObj.account.is_admin:
                        text = "A new account is created - " + str(user)
                        newNoti = Notification(user=userObj, text=text)
                        newNoti.save()
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
    recommendations = []
    result = {}
    training_plans = []
    certificates = []
    if response.user.is_authenticated:
        experienced = Achievement.objects.get(title='Experienced Climber')
        advanced = Achievement.objects.get(title='Advanced Climber')  
        master = Achievement.objects.get(title='Master Climber')      
        elite = Achievement.objects.get(title='Elite Climber')    
        legendary = Achievement.objects.get(title='Legendary Climber')
        achievements = response.user.account.achievements.all()
        result = calculateStatitic(response.user)
        if legendary in achievements or elite in achievements:
            recommendations  = Crag.objects.filter(altitude__gte=800).order_by('?')[:5]
            training_plans.append({
                'link':'https://www.youtube.com/watch?v=-cSUBVA9TK8',
                'title': '5 Ways to Maximise Your Grip (without a Hangboard)'
            })

            training_plans.append({
                'link':'https://www.youtube.com/watch?v=3q9oeoku0jM',
                'title': '13 Tips to improve your climbing'
            })

            training_plans.append({
                'link':'https://www.youtube.com/watch?v=kR1buRTIKhk',
                'title': '20 Pro Tips EVERY Climber should know'
            })

            training_plans.append({
                'link:': 'https://www.youtube.com/watch?v=2LEnGELJxw0',
                'title': '7 Key Techniques to Master in Climbing (with Huge Announcement!)'
            })

            certificates.append({
                'link': 'https://amga.com/amga-multi-pitch-instructor/',
                'title': 'Multi Pitch Instructor'
            })

            certificates.append({
                'link': 'https://amga.com/rock-guide/',
                'title': 'Rock Guide'
            })

            certificates.append({
                'link': 'https://amga.com/alpine-guide/',
                'title': 'Alpine Guide'
            })
            
        elif master in achievements or advanced in achievements or experienced in achievements:
            recommendations  = Crag.objects.filter(altitude__range=(500, 799)).order_by('?')[:5]
            training_plans.append({
                'link':'https://www.youtube.com/watch?v=-cSUBVA9TK8',
                'title': '5 Ways to Maximise Your Grip (without a Hangboard)'
            })

            training_plans.append({
                'link':'https://www.youtube.com/watch?v=3q9oeoku0jM',
                'title': '13 Tips to improve your climbing'
            })

            training_plans.append({
                'link':'https://www.youtube.com/watch?v=kR1buRTIKhk',
                'title': '20 Pro Tips EVERY Climber should know'
            })

            training_plans.append({
                'link:': 'https://www.youtube.com/watch?v=2LEnGELJxw0',
                'title': '7 Key Techniques to Master in Climbing (with Huge Announcement!)'
            })

            certificates.append({
                'link': 'https://amga.com/single-pitch-instructor/',
                'title': 'Single Pitch Instructor'
            })
        else:
            recommendations = Crag.objects.filter(altitude__lt=500).order_by('?')[:5]
            training_plans.append({
                'link':'https://www.youtube.com/watch?v=2SaOEUZQ2G8',
                'title': 'Basic Skills for Mountain Climbing - How to Climb a Mountain'
            })

            training_plans.append({
                'link':'https://www.youtube.com/watch?v=b2v4brHpdxY',
                'title': 'TOP 10 Tips for Beginner Boulderers'
            })

            training_plans.append({
                'link':'https://www.youtube.com/watch?v=Lb8QkUemXiM',
                'title': 'How to Maximize Your First Year of Climbing'
            })

            training_plans.append({
                'link':'https://www.youtube.com/watch?v=TIudRBkNjWA',
                'title': 'The 5 Basic Principles of Climbing'
            })

            certificates = None

    return render(response, "profile.html", {'recommendations': recommendations, 'result': result, 'training_plans': training_plans, 'certificates': certificates})

def calculateStatitic(user):
    one_week_ago = dti.now() - timedelta(days=7)
    one_month_ago = dti.now() - timedelta(days=30)

    routes_last_week = user.activities.all().filter(date__gte=one_week_ago)
    total_route_climbed_last_week = routes_last_week.count()
    
    total_dist_last_week = 0
    total_time_last_week = 0
    for route in routes_last_week:
        total_dist_last_week += route.distance
        if route.timeCompleted != None:
            total_time_last_week += convertToSec(route.timeCompleted)
    
    time_per_route_week = 0
    distance_per_route_week = 0
    if total_route_climbed_last_week != 0:
        time_per_route_week = convertBackToSec(round(total_time_last_week/total_route_climbed_last_week))
        distance_per_route_week = total_dist_last_week/total_route_climbed_last_week

    
    routes_last_month = user.activities.all().filter(date__gte=one_month_ago)
    total_route_climbed_last_month = routes_last_month.count()

    total_dist_last_month = 0
    total_time_last_month = 0
    for route in routes_last_month:
        total_dist_last_month += route.distance
        if route.timeCompleted != None:
            total_time_last_month += convertToSec(route.timeCompleted)
    
    time_per_route_month = 0
    distance_per_route_month = 0
    if total_route_climbed_last_week != 0:
        time_per_route_month = convertBackToSec(round(total_time_last_month/total_route_climbed_last_month))
        distance_per_route_month = total_dist_last_month/total_route_climbed_last_month

    result = {
        'total_route_climbed_last_week': total_route_climbed_last_week,
        'total_dist_last_week': total_dist_last_week,
        'time_per_route_week': time_per_route_week,
        'distance_per_route_week': distance_per_route_week,
        'total_route_climbed_last_month': total_route_climbed_last_month,
        'total_dist_last_month': total_dist_last_month,
        'time_per_route_month': time_per_route_month,
        'distance_per_route_month': distance_per_route_month
    }
    return result 

def convertToSec(time):
    time_array = time.split(":")
    hour = time_array[0]
    minutes = time_array[1]
    seconds = time_array[2]
    total_seconds = ((int(hour) * 60) + int(minutes))* 60 + int(seconds)
    return total_seconds 

def convertBackToSec(totalseconds):
    hours, remainder = divmod(totalseconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return (str(hours)+":"+str(minutes)+":"+str(seconds))

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

    referring_page = response.META.get('HTTP_REFERER')

    if referring_page:
        return HttpResponseRedirect(referring_page)
    else:
        return redirect("/subtopic/"+str(subtopic.id))

def viewAccounts(response):
    users = []
    if response.user.account.is_admin:
        users = User.objects.all()
    return render(response, 'viewAccounts.html', {'users':users})

def suspendAccount(response, id):
    if response.user.account.is_admin:
        userObj = User.objects.get(id=id)
        userObj.account.updateAccountSuspend(status=True)
    return redirect('/viewAccounts/')

def activateAccount(response, id):
    if response.user.account.is_admin:
        userObj = User.objects.get(id=id)
        userObj.account.updateAccountSuspend(status=False)
    return redirect('/viewAccounts/')

def suspendProfile(response, id):
    userObj = User.objects.get(id=id)
    if response.user.account.is_admin or response.user == userObj:
        print("yes")
        userObj.account.updateProfileSuspend(status=True)
        print(userObj.account.profileSuspended)
    
    referring_page = response.META.get('HTTP_REFERER')

    if referring_page:
        return HttpResponseRedirect(referring_page)
    else:
        return redirect('/profile/')

def activateProfile(response, id):
    userObj = User.objects.get(id=id)
    if response.user.account.is_admin or response.user == userObj:
        userObj.account.updateProfileSuspend(status=False)
    referring_page = response.META.get('HTTP_REFERER')

    if referring_page:
        return HttpResponseRedirect(referring_page)
    else:
        return redirect('/profile/')
    
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
            timeCompleted = form.cleaned_data["timeCompleted"]
            climbActivity = ClimbingActivity(user=user, locName=locName, distance=distance, date=date, timeCompleted=timeCompleted) 
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
            text = "You have a new achievement - " + str(achievement)
            newNoti = Notification(user=user, text=text)
            newNoti.save()
        badge = Badge.objects.get(name="Beginner")
        if badge not in user.account.badges.all():
            user.account.addBadge(badge)
            user.account.addShowingBadge(badge)
            text = "You have a new badge - " + str(badge)
            newNoti = Notification(user=user, text=text)
            newNoti.save()
        
    
    #Intermediate
    if(user.account.totalRoute >= 20):
        achievement = Achievement.objects.get(title='Intermediate Climber')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)
            text = "You have a new achievement - " + str(achievement)
            newNoti = Notification(user=user, text=text)
            newNoti.save()
        badge = Badge.objects.get(name="Intermediate")
        if badge not in user.account.badges.all():
            user.account.addBadge(badge)
            user.account.addShowingBadge(badge)
            text = "You have a new badge - " + str(badge)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

    #Experienced
    if(user.account.totalRoute >= 50):
        achievement = Achievement.objects.get(title='Experienced Climber')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)
            text = "You have a new achievement - " + str(achievement)
            newNoti = Notification(user=user, text=text)
            newNoti.save()
        badge = Badge.objects.get(name="Experienced")
        if badge not in user.account.badges.all():
            user.account.addBadge(badge)
            user.account.addShowingBadge(badge)
            text = "You have a new badge - " + str(badge)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

    #Advanced
    if(user.account.totalRoute >= 100):
        achievement = Achievement.objects.get(title='Advanced Climber')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)
            text = "You have a new achievement - " + str(achievement)
            newNoti = Notification(user=user, text=text)
            newNoti.save()
        badge = Badge.objects.get(name="Advanced")
        if badge not in user.account.badges.all():
            user.account.addBadge(badge)
            user.account.addShowingBadge(badge)
            text = "You have a new badge - " + str(badge)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

    #Master
    if(user.account.totalRoute >= 200):
        achievement = Achievement.objects.get(title='Master Climber')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)
            text = "You have a new achievement - " + str(achievement)
            newNoti = Notification(user=user, text=text)
            newNoti.save()
        badge = Badge.objects.get(name="Master")
        if badge not in user.account.badges.all():
            user.account.addBadge(badge)
            user.account.addShowingBadge(badge)
            text = "You have a new badge - " + str(badge)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

    #Elite
    if(user.account.totalRoute >= 500):
        achievement = Achievement.objects.get(title='Elite Climber')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)
            text = "You have a new achievement - " + str(achievement)
            newNoti = Notification(user=user, text=text)
            newNoti.save()
        badge = Badge.objects.get(name="Elite")
        if badge not in user.account.badges.all():
            user.account.addBadge(badge)
            user.account.addShowingBadge(badge)
            text = "You have a new badge - " + str(badge)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

    #Legendary
    if(user.account.totalRoute >= 1000):
        achievement = Achievement.objects.get(title='Legendary Climber')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)
            text = "You have a new achievement - " + str(achievement)
            newNoti = Notification(user=user, text=text)
            newNoti.save()
        badge = Badge.objects.get(name="Legendary")
        if badge not in user.account.badges.all():
            user.account.addBadge(badge)
            user.account.addShowingBadge(badge)
            text = "You have a new badge - " + str(badge)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

    #1000-Meter Explorer
    if(user.account.totalDistance >= 1000):
        achievement = Achievement.objects.get(title='1000-Meter Explorer')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)
            text = "You have a new achievement - " + str(achievement)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

    #10000-Meter Explorer
    if(user.account.totalDistance >= 10000):
        achievement = Achievement.objects.get(title='10000-Meter Explorer')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)
            text = "You have a new achievement - " + str(achievement)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

    #100000-Meter Explorer
    if(user.account.totalDistance >= 100000):
        achievement = Achievement.objects.get(title='100000-Meter Explorer')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)
            text = "You have a new achievement - " + str(achievement)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

    #500000-Meter Explorer
    if(user.account.totalDistance >= 500000):
        achievement = Achievement.objects.get(title='500000-Meter Explorer')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)
            text = "You have a new achievement - " + str(achievement)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

    #1000000-Meter Explorer
    if(user.account.totalDistance >= 1000000):
        achievement = Achievement.objects.get(title='1000000-Meter Explorer')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)
            text = "You have a new achievement - " + str(achievement)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

    #5000000-Meter Explorer
    if(user.account.totalDistance >= 5000000):
        achievement = Achievement.objects.get(title='5000000-Meter Explorer')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)
            text = "You have a new achievement - " + str(achievement)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

    #10000000-Meter Explorer
    if(user.account.totalDistance >= 10000000):
        achievement = Achievement.objects.get(title='10000000-Meter Explorer')
        if(achievement not in user.account.achievements.all()):
            user.account.addAchievement(achievement)
            text = "You have a new achievement - " + str(achievement)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

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

def editEmergency(response, id):
    if(response.user != User.objects.get(id=id)):
        return redirect('/profile/')
    if response.method == "POST":
        form = EditEmergency(response.POST)
        if form.is_valid():
            user = User.objects.get(id=id)
            number = form.cleaned_data["number"]
            user.account.setEmergencyContact(number)
            return redirect('/profile/')
    else:
        user = User.objects.get(id=id)
        editemergency = EditEmergency(initial={'number': user.account.emergencyContact})
    return render(response, 'editEmergencyContact.html', {'editemergency':editemergency})

def followUser(response, id):
    user = response.user
    userToFollow = User.objects.get(id=id)
    text = "You have a new follower - " + str(user)
    newNotification = Notification(user=userToFollow, text=text)
    newNotification.save()
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
                checkPostCount(response.user)
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

def checkPostCount(user):
    post_count = 0
    for post in user.posts.all():
        post_count += 1
    if post_count >= 1:
        badge = Badge.objects.get(name="Bronze Contributor")
        if badge not in user.account.badges.all():
            user.account.addBadge(badge)
            user.account.addShowingBadge(badge)
            text = "You have a new badge - " + str(badge)
            newNoti = Notification(user=user, text=text)
            newNoti.save()
    
    if post_count >= 10:
        badge = Badge.objects.get(name="Silver Contributor")
        if badge not in user.account.badges.all():
            user.account.addBadge(badge)
            user.account.addShowingBadge(badge)
            text = "You have a new badge - " + str(badge)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

    if post_count >= 100:
        badge = Badge.objects.get(name="Gold Contributor")
        if badge not in user.account.badges.all():
            user.account.addBadge(badge)
            user.account.addShowingBadge(badge)
            text = "You have a new badge - " + str(badge)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

    if post_count >= 1000:
        badge = Badge.objects.get(name="Gold Contributor")
        if badge not in user.account.badges.all():
            user.account.addBadge(badge)
            user.account.addShowingBadge(badge)
            text = "You have a new badge - " + str(badge)
            newNoti = Notification(user=user, text=text)
            newNoti.save()

def deleteDraft(response, id):
    draft = PostDraft.objects.get(id=id)
    subtopic = draft.topic
    if draft.user == response.user:
        draft.delete()
    return redirect('/subtopic/'+str(subtopic.id))

def addTagsForPost(response, id):
    post = ForumPost.objects.get(id=id)
    if response.method == "POST":
        form = AddTagsForm(response.POST)
        if form.is_valid():
            tags = form.cleaned_data["tags"].split(", ")
            for tag in tags:
                exist = False
                for tagAvail in Tag.objects.all():
                    if str(tag) == tagAvail.name:
                        exist=True
                if exist:
                    name = str(tag)
                    tagExist = Tag.objects.get(name=name)
                    tagExist.addPost(post)
                else:
                    newTag = Tag(name=tag)
                    newTag.save()
                    newTag.addPost(post)
        return redirect('/viewPost/' +str(post.id))
    else:
        addtags = AddTagsForm()
        tags = []
        for tag in Tag.objects.all():
            if post in tag.posts.all():
                tags.append(tag)
    return render(response, 'addTags.html', {'addtags': addtags, 'post': post, 'tags': tags})

def addTagsForSubTopic(response, id):
    subtopic = SubTopic.objects.get(id=id)
    if response.method == "POST":
        form = AddTagsForm(response.POST)
        if form.is_valid():
            tags = form.cleaned_data["tags"].split(", ")
            for tag in tags:
                exist = False
                for tagAvail in Tag.objects.all():
                    if str(tag) == tagAvail.name:
                        exist=True
                if exist:
                    name = str(tag)
                    tagExist = Tag.objects.get(name=name)
                    tagExist.addST(subtopic)
                else:
                    newTag = Tag(name=tag)
                    newTag.save()
                    newTag.addST(subtopic)
        return redirect('/topic/' +str(subtopic.mainTopic.id))
    else:
        addtags = AddTagsForm()
        tags = []
        for tag in Tag.objects.all():
            if subtopic in tag.subtopics.all():
                tags.append(tag)
    return render(response, 'addTags.html', {'addtags': addtags, 'subtopic': subtopic, 'tags': tags})

def addTagsForMainTopic(response, id):
    maintopic = MainTopic.objects.get(id=id)
    if response.method == "POST":
        form = AddTagsForm(response.POST)
        if form.is_valid():
            tags = form.cleaned_data["tags"].split(", ")
            for tag in tags:
                exist = False
                for tagAvail in Tag.objects.all():
                    if str(tag) == tagAvail.name:
                        exist=True
                if exist:
                    name = str(tag)
                    tagExist = Tag.objects.get(name=name)
                    tagExist.addMT(maintopic)
                else:
                    newTag = Tag(name=tag)
                    newTag.save()
                    newTag.addMT(maintopic)
        return redirect('/forum/')
    else:
        addtags = AddTagsForm()
        tags = []
        for tag in Tag.objects.all():
            if maintopic in tag.maintopics.all():
                tags.append(tag)
    return render(response, 'addTags.html', {'addtags': addtags, 'maintopic': maintopic, 'tags': tags})

def tags(response, id):    
    tag = Tag.objects.get(id=id)

    maintopics = []
    subtopics = []
    posts = []
    topics = []
    
    for maintopic in MainTopic.objects.all():
        for tagCheck in maintopic.tags.all():
            if tagCheck == tag:
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
        for tagCheck in subtopic.tags.all():
            if tagCheck == tag:
                subtopics.append(subtopic)

    for post in ForumPost.objects.all():
        for tagCheck in post.tags.all():
            if tagCheck == tag:
                posts.append(post)
    

    flaggedPosts = []
    if response.user.is_authenticated:
        for flaggedPost in response.user.flaggedPosts.all():
            flaggedPosts.append(flaggedPost.post)
    allFP = []
    for flaggedPost in FlaggedPost.objects.all():
            allFP.append(flaggedPost.post)
    return render(response, 'tags.html',  {'tag': tag, 'maintopics': maintopics, 'subtopics': subtopics, 'posts': posts, 'flaggedPosts': flaggedPosts, 'allFP': allFP, 'topics': topics})

def removeTagsForPost(response, postid, tagid):
    post = ForumPost.objects.get(id=postid)
    tag = Tag.objects.get(id=tagid)
    if response.user.is_authenticated:
        tag.posts.remove(post)
        tag.save()

    referring_page = response.META.get('HTTP_REFERER')

    if referring_page:
        return HttpResponseRedirect(referring_page)
    else:
        return redirect('/viewPost/'+str(post.id))
    
def removeTagsForSubTopic(response, stid, tagid):
    subtopic = SubTopic.objects.get(id=stid)
    tag = Tag.objects.get(id=tagid)
    if response.user.is_authenticated:
        tag.subtopics.remove(subtopic)
        tag.save()

    referring_page = response.META.get('HTTP_REFERER')

    if referring_page:
        return HttpResponseRedirect(referring_page)
    else:
        return redirect('/subtopic/'+str(subtopic.id))
    
def removeTagsForMainTopic(response, mtid, tagid):
    maintopic = MainTopic.objects.get(id=mtid)
    tag = Tag.objects.get(id=tagid)

    if response.user.is_authenticated:
        tag.maintopics.remove(maintopic)
        tag.save()

    referring_page = response.META.get('HTTP_REFERER')

    if referring_page:
        return HttpResponseRedirect(referring_page)
    else:
        return redirect('/forum/')

def viewAvailableBadges(response):
    allbadges = Badge.objects.all()   
    return render(response, 'viewBadges.html', {'allbadges': allbadges}) 

def unshowBadge(response, id):
    badge = Badge.objects.get(id=id)
    if badge in response.user.account.showingBadges.all():
        response.user.account.removeShowingBadge(badge)
    return redirect('/viewAvailableBadges/')

def showBadge(response, id):
    badge = Badge.objects.get(id=id)
    if badge not in response.user.account.showingBadges.all():
        response.user.account.addShowingBadge(badge)
    return redirect('/viewAvailableBadges/')

def filterTopics(response):
    month = ""
    year = ""
    topview = ""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
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

    years = []
    for topic in topics:
        if topic['latest_post'] != None:
            yearitem = topic['latest_post'].date[11:15]
            if yearitem not in years:
                years.append(int(yearitem))
    years.sort()

    if response.method == 'POST':
        filterlist1 = []
        if 'topview' in response.POST:
            topview = response.POST['topview']
            if topview == 'on':
                for section in sections: 
                    highestView = 0
                    toptopic = None
                    for topic in topics:
                        if topic["maintopic"] in section.maintopics.all():
                            if topic["maintopic"].totalView >= highestView:
                                highestView = topic["maintopic"].totalView
                                toptopic = topic
                    if toptopic != None:
                        filterlist1.append(toptopic)
                topics = filterlist1

        filterlist2 = []
        if(response.POST.get('month') != None):
            month = response.POST['month']
            for section in sections:  
                for topic in topics:
                    if topic['latest_post'] != None and topic["maintopic"] in section.maintopics.all():
                        if month in topic['latest_post'].date:
                            filterlist2.append(topic)
            topics = filterlist2

        filterlist3 = []
        if(response.POST.get('year') != None):
            year = response.POST['year']
            for section in sections:  
                for topic in topics:
                    if topic['latest_post'] != None and topic["maintopic"] in section.maintopics.all():
                        if year in topic['latest_post'].date:
                            filterlist3.append(topic)
            topics = filterlist3
    return render(response, "forum.html", {'sections': sections, 'topics': topics, 'months': months, 'month': month, 'years': years, 'year': year, 'topview': topview})

def checkAltitude(response):
    if response.method == "POST":
        altitude = response.POST.get("altitude", None)
        if altitude:
            if int(altitude) >= 2500:
                data = {
                    'result': "Altitude greater or equal 2500m, Please be aware",
                    'danger': True
                }
                
            else:
                data = {
                    'result': "Altitude normal",
                    'danger': False
                }
            return JsonResponse({"data": data})
        else:
            data = {
                    'result': "Data not received.",
                    'danger': False
                }
            return JsonResponse({"data": data})

def checkAuthentication(response):
    if response.user.is_authenticated:
        tracking = response.user.account.tracking
        return JsonResponse({'is_authenticated': True, 'tracking': tracking})
    else:
        return JsonResponse({'is_authenticated': False})
    
def checkNotifications(response):
    if response.user.is_authenticated:
        notifications = []

        for notification in response.user.notifications.all():
            #notification.setNotified(status=False)
            if notification.is_notified == False:
                notifications.append(notification.text)
                notification.setNotified(status=True)
        if len(notifications) == 0:
            return JsonResponse({'notify': False})
        else:
            return JsonResponse({'notify': True, 'notifications': notifications})
    else:
        return JsonResponse({'notify': False})

def notifications(response):
    notifications = []
    if response.user.is_authenticated:
        notifications = response.user.notifications.all().order_by("-id")
        chats = response.user.chats.all()
    return render(response, 'notifications.html', {'notifications': notifications, 'chats': chats})    

def autoSuggest(response):
    query = response.GET.get('query', '')
    #suggestionsOri = Crag.objects.filter(name__icontains=query)[:7]
    crags = Crag.objects.all()
    suggestionsOri = []
    for crag in crags:
        if str(query).lower().replace(" ","") in crag.name.lower().replace(" ",""):
            suggestionsOri.append(crag)
    if len(suggestionsOri) > 7:
        suggestionsOri = suggestionsOri[:7]
    suggestions = []
    for suggestion in suggestionsOri:
        suggestions.append(suggestion.name)
    return JsonResponse({'suggestions': suggestions})

@csrf_exempt
def loginAR(response):
    if response.method == 'POST':
        try:
            if response.user.is_authenticated:
                logout(response)    
            username = response.POST.get('username')
            password = response.POST.get('password')
            user = authenticate(response, username=username, password=password)
            if user is None:
                return JsonResponse({'success': False, 'error': 'Error! User not found'})
            if(user.account.accountSuspended):
                return JsonResponse({'success': False, 'message': "Error! Account Suspended or Deleted"})
            if(user.account.is_premium == False):
                return JsonResponse({'success': False, 'message': "Error! Account Is Not Premium"})
            login(response, user)
            return JsonResponse({'success': True, 'message': 'Login Successfully'})
        except Exception as e:
            return JsonResponse({'message': 'Error processing form data'}, status=400)
    else:
        return JsonResponse({'message': 'Only POST requests accepted'}, status=405)

def logoutAR(response):
    if response.user.is_authenticated:
        logout(response)
        return JsonResponse({'success': True, 'message': 'Logout Successfully'})
    else:
        return JsonResponse({'success': False, 'message': 'Logout Failed'})
    
def generateReport(response):
    one_week_ago = dti.now() - timedelta(days=7)

    recent_users = User.objects.filter(date_joined__gte=one_week_ago)

    totalUserPastWeek = 0
    for user in recent_users:
        totalUserPastWeek +=1

    one_month_ago = dti.now() - timedelta(days=30)

    last_month_users = User.objects.filter(date_joined__gte=one_month_ago)

    totalUserPastMonth = 0
    for user in last_month_users:
        totalUserPastMonth +=1

    recent_posts_count = 0
    last_month_posts_count = 0
    for post in ForumPost.objects.all():
        if getDateTime(post.date) >= one_week_ago:
            recent_posts_count += 1

        if getDateTime(post.date) >= one_month_ago:
            last_month_posts_count +=1

    total_topic_view = 0
    most_popular_topic = MainTopic.objects.all().first()
    for topic in MainTopic.objects.all():
        total_topic_view += topic.totalView
        if topic.totalView >= most_popular_topic.totalView:
            most_popular_topic = topic

    total_subtopic_view = 0
    most_popular_subtopic = SubTopic.objects.all().first()
    for subtopic in SubTopic.objects.all():
        total_subtopic_view += subtopic.totalView
        if subtopic.totalView >= most_popular_subtopic.totalView:
            most_popular_subtopic = subtopic

    total_post_view = 0
    most_popular_post = ForumPost.objects.all().first()
    for post in ForumPost.objects.all():
        total_post_view += post.totalView
        if post.totalView >= most_popular_post.totalView:
            most_popular_post = post
    report = {
        'recent_users': recent_users, 
        'totalUserPastWeek': totalUserPastWeek,
        'last_month_users': last_month_users,
        'totalUserPastMonth': totalUserPastMonth,
        'recent_posts_count': recent_posts_count,
        'last_month_posts_count': last_month_posts_count,
        'total_topic_view': total_topic_view,
        'most_popular_topic': most_popular_topic,
        'total_subtopic_view': total_subtopic_view,
        'most_popular_subtopic': most_popular_subtopic,
        'total_post_view': total_post_view,
        'most_popular_post': most_popular_post.title,
    }
    return render(response, 'report.html',{'report': report})

@csrf_exempt
def ARcreateClimbActivity(response):
    if response.user.is_authenticated == False:
        return JsonResponse({'success': False, 'message': 'User Not Logged In'})
    if response.method == "POST":
        try:
            user = response.user
            locName = response.POST.get('locName')
            distance = response.POST.get('distance')
            dateReceived = response.POST.get('date')
            timeCompleted = response.POST.get('timeCompleted')
            date = dti.strptime(dateReceived, "%Y-%m-%dT%H:%M:%S")
            climbActivity = ClimbingActivity(user=user, locName=locName, distance=distance, date=date, timeCompleted=timeCompleted) 
            climbActivity.save()
            user.account.updateRouteAndDist()
            checkAchievement(user)
            return JsonResponse({'success': True, 'message': 'Upload Successfully'})
        except Exception as e:
            return JsonResponse({'message': 'Error processing form data'}, status=400)
    else:
        return JsonResponse({'message': 'Only POST requests accepted'}, status=405)
    
def reactPost(response, postid, number):
    post = ForumPost.objects.get(id=postid)
    if response.user.is_authenticated:
        post.reaction(number, response.user)

    referring_page = response.META.get('HTTP_REFERER')

    if referring_page:
        return HttpResponseRedirect(referring_page)
    else:
        return redirect('/subtopic/'+str(post.topic.id))

def removeReactPost(response, postid, number):
    post = ForumPost.objects.get(id=postid)
    if response.user.is_authenticated:
        post.cancelReaction(number, response.user)

    referring_page = response.META.get('HTTP_REFERER')

    if referring_page:
        return HttpResponseRedirect(referring_page)
    else:
        return redirect('/subtopic/'+str(post.topic.id))
    

def moveup(response, boxid):
    user = response.user
    user.account.moveup(boxid)
    return redirect('/profile/')

def movedown(response, boxid):
    user = response.user
    user.account.movedown(boxid)
    return redirect('/profile/')

def chat(response, id):
    user1 = response.user
    user2 = User.objects.get(id=id)

    chats_with_both_users = None

    for chat in Chat.objects.all():
        if user1 in chat.users.all() and user2 in chat.users.all():
            chats_with_both_users = chat

    if chats_with_both_users == None:
        name = "Chat Between " + str(user1.username) + " and " + str(user2.username)
        chats_with_both_users = Chat.objects.create(name=name)
        chats_with_both_users.users.add(user1)
        chats_with_both_users.users.add(user2)
        chats_with_both_users.save()
    return render(response, 'chat.html', {'chat': chats_with_both_users})

def directChat(response, id):
    chat = Chat.objects.get(id=id)
    if response.user.is_authenticated and response.user in chat.users.all():
        return render(response, 'chat.html', {'chat': chat})
    else:
        referring_page = response.META.get('HTTP_REFERER')
        if referring_page:
            return HttpResponseRedirect(referring_page)
        else:
            return redirect('/notifications/')

def sendMessage(response, id):
    if response.user.is_authenticated:
        message = response.POST['message']
        date = response.POST['date']
        user = response.user
        chat = Chat.objects.get(id=id)

        new_message = Message.objects.create(text=message, user=user, chat=chat, date=date)
        new_message.save()
        return JsonResponse({'message':'Message sent!'})
    else:
        return JsonResponse({'message':'Message not sent!'})

def getMessages(response, id):
    chat = Chat.objects.get(id=id)

    messages = Message.objects.filter(chat=chat)
    messages_to_send = []
    for message in messages:
        messages_to_send.append({
            'user': message.user.username,
            'text': message.text,
            'date': message.date
        })
    return JsonResponse({"messages":messages_to_send})

def map(response):
    return render (response, 'map.html')

def getCrags(response):
    crags = Crag.objects.all()
    crags_to_send = []
    for crag in crags:
        crags_to_send.append({
            'name': crag.name,
            'latitude': crag.latitude,
            'longitude': crag.longitude,
            'desc': crag.desc,
            'altitude': crag.altitude
        })
    return JsonResponse({'crags': crags_to_send})

@csrf_exempt
def contactEmergency(response):
    if response.method == 'POST':
        if response.user.is_authenticated:
            if response.user.account.emergencyContact != None:
                env = environ.Env()

                environ.Env.read_env()

                account_sid = env('TWILIO_ACCOUNT_SID')
                auth_token = env('TWILIO_AUTH_TOKEN')
                client = Client(account_sid, auth_token)

                latitude = response.POST['latitude']
                longitude = response.POST['longitude']

                bodyMessage = "This is from GoClimb. Help!, "+ response.user.first_name + " " + response.user.last_name + " is in danger!" + " His/Her location is at (" + latitude + "," + longitude + ")!"                
            
                message = client.messages \
                                .create(
                                    body=bodyMessage,
                                    from_='+14408534336',
                                    to=response.user.account.emergencyContact
                                )

                if message.status == "sent":
                    return JsonResponse({'message': 'Contacted Successfully!'})
                elif message.status == "queued":
                    return JsonResponse({'message': 'Tried to Contacted!'})
                else:
                    return JsonResponse({'message': 'Failed to Contacted!'})
            else:
                return JsonResponse({'message': 'No Emergency Contact to contact!'})
    return JsonResponse({'message': "Invalid Request"})

def subscribe(response):
    if response.user.is_authenticated and (response.user.account.is_premium == False):
        response.user.account.setPremium(True)
        text = "You have subscribed to premium!"
        newNoti = Notification(user=response.user, text=text)
        newNoti.save()
    referring_page = response.META.get('HTTP_REFERER')

    if referring_page:
        return HttpResponseRedirect(referring_page)
    else:
        return redirect('/home/')
    
def track(response):
    if response.user.is_authenticated:
        response.user.account.setTracking(status=True)

    referring_page = response.META.get('HTTP_REFERER')

    if referring_page:
        return HttpResponseRedirect(referring_page)
    else:
        return redirect('/profile/')
    
def untrack(response):
    if response.user.is_authenticated:
        response.user.account.setTracking(status=False)

    referring_page = response.META.get('HTTP_REFERER')

    if referring_page:
        return HttpResponseRedirect(referring_page)
    else:
        return redirect('/profile/')

@csrf_exempt
def updateCoor(response):
    if response.method == 'POST':
        if response.user.is_authenticated:
            date = response.POST['date']
            coor = response.POST['coor']

            if coor != None and date != None:
                response.user.account.setLastCoorDate(date=date)
                response.user.account.setLastCoor(coor=coor)

                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False})
        else:
            return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': False})
    