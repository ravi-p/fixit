from django import forms
import re
from models import TaskQ
from models import FLOOR_CHOICES, ROOM_CHOICES
from models import STATUS_CHOICES, PRIORITY_CHOICES,APP_CHOICES
from datetime import datetime
from django.utils.safestring import mark_safe
import pdb

ground_val = "Invalid Room. Valid options are WC, Accounts, Server, Common Passage, Stairwell, Lift and Conference."
first_val = "Invalid Room. Valid options are First, Second, Third, WC, Common Passage, Stairwell, Lift and Conference"
second_val = third_val = first_val
pantry_val = "Invalid Room. Valid option is sink, lunch area, barbeque area, table top & battery room"
all_val = "Invalid Room. Valid options are WC, Common Passage, Stairwell, Lift and Conference."
GF=['0', '4', '5', '6', '8', '9', '10']
FF=['0', '1', '2', '3', '4', '8', '9', '10']
SF=['0', '1', '2', '3', '4', '8', '9', '10']
TF=['0', '1', '2', '3', '4', '8', '9', '10']
PF=['7','11','12','13','14']
All=['0', '4', '8', '9', '10']

class HorizRadioRenderer(forms.RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
            """Outputs radios"""
            return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

class TaskAdminForm(forms.ModelForm):

    floor = forms.CharField(label='Floor',
                required=True,
                widget=forms.Select(attrs={'class': 'form-control',
                'placeholder': 'Select Floor'}, choices=FLOOR_CHOICES ))

    room = forms.CharField(label='Room',
                required=True,
                widget=forms.Select(attrs={'class': 'form-control',
                'placeholder': 'Select Room'}, choices=ROOM_CHOICES ))

    title = forms.CharField(label='Title',
                required=True,
                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Problem Title'}),
                error_messages={
                    'required': 'Title field can not be empty'} )

    desc = forms.CharField(label='Description',
                required=True,
                widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '5',\
                'cols': '60', 'placeholder': 'Enter Problem Statement'}),
                error_messages={
                    'required': 'Description field can not be empty'} )

    priority = forms.CharField(label='Priority',
                required=True,
                widget=forms.Select(attrs={'class': 'form-control',
                'placeholder': 'Select Task Priority'},
                choices=PRIORITY_CHOICES ))

    repeatable = forms.BooleanField(label='Repeatable Task',
                required=False,
                widget=forms.CheckboxInput(attrs={'class': 'checkbox',
                'title': 'Check for repeatable tasks',
                'placeholder': 'Is task repeatable?'},
                ))

    repeat_time = forms.CharField(label='Repeat Task at',
                required=False, max_length=255,
                widget=forms.TextInput(attrs={'class': 'form-control', \
                'placeholder': 'Schedule Task @'}),
                error_messages={})
                    #'required': 'Repeat time field can not be empty'} )
    app = forms.ChoiceField(required=True,widget=forms.RadioSelect(renderer=HorizRadioRenderer),choices=APP_CHOICES)

    status = forms.CharField(label='Status',
                required=False,
                widget=forms.Select(attrs={'class': 'form-control',
                'placeholder': 'Select Status'}, choices=STATUS_CHOICES ))

    class Meta:
        model = TaskQ
        exclude = ['created', 'modified', 'cuser', 'euser']

    def __init__(self, *args, **kwargs):
        super(TaskAdminForm, self).__init__(*args, **kwargs)


    def clean_floor(self):
        if self.cleaned_data['floor']:
            if self.cleaned_data['floor'] == '-1':
                raise forms.ValidationError('Floor field is required.')
        return self.cleaned_data['floor']


    def clean_room(self):
        if self.cleaned_data['room']:
            if self.cleaned_data['room'] == '-1':
                raise forms.ValidationError('Room field is required.')

            # If Floor==Ground then valid Room options are WC, Accounts and
            # Conference
            if self.cleaned_data['floor'] == '0':
                if self.cleaned_data['room'] not in GF:
                    raise forms.ValidationError(ground_val)

            # If Floor==First then valid Room options are WC, First, Second,
            # Third and Conference.
            if self.cleaned_data['floor'] == '1':
                if self.cleaned_data['room'] not in FF:
                    raise forms.ValidationError(first_val)

            # If Floor==Second then valid Room options are WC, First, Second,
            # Third and Conference.
            if self.cleaned_data['floor'] == '2':
                if self.cleaned_data['room'] not in SF:
                    raise forms.ValidationError(second_val)

            # If Floor==Third then valid Room options are WC, First, Second,
            # Third and Conference.
            if self.cleaned_data['floor'] == '3':
                if self.cleaned_data['room'] not in TF:
                    raise forms.ValidationError(third_val)

            # If Floor==Pantry then valid Room options are Lunch area and
            # Server room.
            if self.cleaned_data['floor'] == '4':
                if self.cleaned_data['room'] not in PF:
                    raise forms.ValidationError(pantry_val)

            # If Floor==All then valid Room options are WC and Conference.
            if self.cleaned_data['floor'] == '5':
                if self.cleaned_data['room'] not in All:
                    raise forms.ValidationError(all_val)

        return self.cleaned_data['room']

    def clean_title(self):
        if self.cleaned_data['title']:
            if self.cleaned_data['title'].strip() == '':
                raise forms.ValidationError('Title field is required.')
        return self.cleaned_data['title']

    def clean_desc(self):
        if self.cleaned_data['desc']:
            if self.cleaned_data['desc'].strip() == '':
                raise forms.ValidationError('Description field is required.')
        return self.cleaned_data['desc']

    def clean_repeat_time(self):
        if not self.cleaned_data['repeatable']:
            return self.cleaned_data['repeat_time']
        else:
            temp_time = self.cleaned_data['repeat_time']
            if not temp_time:
                raise forms.ValidationError('Repeat time field is required.')
            else:
                if ' ' in temp_time:
                    time_str = temp_time.split()[1]
                else:
                    time_str = "%s:00"%temp_time
                date_str = datetime.now().strftime("%Y-%m-%d ")
                datetime_str = "%s %s"%(date_str, time_str)
                date_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                return date_obj
        #self.cleaned_data['repeat_time']

    def clean_app(self):
        if self.cleaned_data['app']:
            if self.cleaned_data['app'] not in ['infra','housekeep']:
                raise forms.ValidationError('Invalid App')
        return self.cleaned_data['app']

    def clean(self):
        return self.cleaned_data



class TaskForm(TaskAdminForm):



    class Meta:
        model = TaskQ
        exclude = ['created', 'modified', 'cuser', 'euser','status','app']


class TaskUpdateForm(TaskForm):
    class Meta:
        model=TaskQ
        exclude = ['created', 'modified', 'cuser', 'euser','status','app']
    def __init__(self, *args, **kwargs):
        super(TaskUpdateForm, self).__init__(*args, **kwargs)
        try:
            EndIndex=int(self.initial['priority'])
        except KeyError:
            EndIndex=len(PRIORITY_CHOICES)
            pass
        self.fields['priority'] = forms.ChoiceField(label='Priority',required=True,\
             widget=forms.Select(attrs={'class': 'form-control'}),\
             choices=PRIORITY_CHOICES[:EndIndex])

