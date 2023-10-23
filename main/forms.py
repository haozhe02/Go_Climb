from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SearchCrag(forms.Form):
    name = forms.CharField(label="Name", max_length=200)

class CreateCountry(forms.Form):
    name = forms.CharField(label="Name", max_length=200)

class CreatePost(forms.Form):
    title = forms.CharField(label="Title", max_length=200)
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40, 'style': " width: 100%;padding: 12px 20px 12px 50px;"}), strip=False)
    image = forms.ImageField(required=False)
    create_button = forms.CharField(label="Create Post", widget=forms.HiddenInput(attrs={'class': 'submit-button'}), required=False)
    save_button = forms.CharField(label="Save As Draft", widget=forms.HiddenInput(attrs={'class': 'submit-button'}), required=False)

    title.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Title'})
    text.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Content'})

class CreateComment(forms.Form):
    text = forms.CharField(max_length=500)

class SignupForm(UserCreationForm):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField(max_length=150)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    username.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Username'})
    first_name.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'First Name'})
    last_name.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Last Name'})
    email.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Email'})
    password1.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Password', 'id': 'password1'})
    password2.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Re-type Password','id': 'password2'})

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class CreateSection(forms.Form):
    title = forms.CharField(label="Title", max_length=200)

    title.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Title'})

class CreateTopic(forms.Form):
    title = forms.CharField(label="Title", max_length=200)
    description = forms.CharField(label="Title", max_length=200)

    title.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Title'})
    description.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Description'})

class ContactUsForm(forms.Form):
    firstname = forms.CharField(label="Title", max_length=200)
    lastname = forms.CharField(label="Title", max_length=200)
    email = forms.EmailField(max_length=150)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 30}), strip=False)

    firstname.widget.attrs.update({"class": "form-control"})
    lastname.widget.attrs.update({"class": "form-control"})
    email.widget.attrs.update({"class": "form-control"})
    message.widget.attrs.update({"class": "form-control"})


class EditLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField(max_length=150)
    
    username.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Username'})
    first_name.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'First Name'})
    last_name.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Last Name'})
    email.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Email'})

class DateInput(forms.DateInput):
    input_type = 'date'

class CreateClimbingActivity(forms.Form):
    locName = forms.CharField(max_length=150)
    distance = forms.CharField(max_length=150)
    date = forms.DateField(widget=DateInput)
    timeCompleted = forms.CharField(max_length=150)

    locName.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'locName'})
    distance.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'distance (m)', 'id': 'distance'})
    date.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'date'})
    timeCompleted.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Time Completed: hh:mm:ss', 'id': 'timeCompleted'})

class EditAbout(forms.Form):    
    about = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 30}), strip=False)

    about.widget.attrs.update({"class": "form-control"})

class EditSocialMedia(forms.Form):
    facebook = forms.CharField(max_length=150)
    youtube = forms.CharField(max_length=150)
    
    facebook.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Facebook Link'})
    youtube.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Youtube Link'})

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}), strip=False)
    text.widget.attrs.update({"class": "form-control"})

class AddTagsForm(forms.Form):
    tags = forms.CharField(max_length=500)
    tags.widget.attrs.update({"class": "full-width has-padding has-border", 'placeholder': 'Tags'})