from django import forms
from django.utils import timezone

from common.forms import ModelFormWithHelper
from common.helpers import SubmitCancelFormHelper
from meetup.models import Meetup
from users.models import SystersUser


class AddMeetupForm(ModelFormWithHelper):
    """Form to create new Meetup. The created_by and the meetup_location of which meetup belong to
    are expected to be provided when initializing the form:

    * created_by - currently logged in user
    * meetup_location - to which Meetup belongs
    """
    class Meta:
        model = Meetup
        fields = ('title', 'slug', 'date', 'time', 'venue', 'description')
        widgets = {'date': forms.DateInput(attrs={'type': 'text', 'class': 'datepicker'}),
                   'time': forms.TimeInput(attrs={'type': 'text', 'class': 'timepicker'})}
        helper_class = SubmitCancelFormHelper
        helper_cancel_href = "{% url 'about_meetup_location' meetup_location.slug %}"

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by')
        self.meetup_location = kwargs.pop('meetup_location')
        super(AddMeetupForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        """Override save to add created_by and meetup_location to the instance"""
        instance = super(AddMeetupForm, self).save(commit=False)
        instance.created_by = SystersUser.objects.get(user=self.created_by)
        instance.meetup_location = self.meetup_location
        if commit:
            instance.save()
        return instance

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise forms.ValidationError("Date should not be before today's date.")
        return date

    def clean_time(self):
        time = self.cleaned_data.get('time')
        date = self.cleaned_data.get('date')
        if time:
            if date == timezone.now().date() and time < timezone.now().time():
                raise forms.ValidationError("Time should not be a time that has already passed.")
        return time


class EditMeetupForm(ModelFormWithHelper):
    """Form to edit Meetup"""
    class Meta:
        model = Meetup
        fields = ('title', 'slug', 'date', 'time', 'description', 'venue')
        widgets = {'date': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker'}),
                   'time': forms.TimeInput(attrs={'type': 'time', 'class': 'timepicker'})}
        helper_class = SubmitCancelFormHelper
        helper_cancel_href = "{% url 'view_meetup' meetup_location.slug meetup.slug %}"
