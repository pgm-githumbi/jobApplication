from typing import Any, Mapping, Optional, Type, Union
from django import forms
from django.forms.utils import ErrorList
from django.db import models

from .models import Applications, Jobs



class JobApplicationForm(forms.Form):
    CHOICES = set()
    first_name = forms.CharField(label='First Name ', max_length=100)
    other_name = forms.CharField(label='Other Name ', max_length=100)
    email = forms.EmailField(max_length=100, widget=forms.EmailInput())
    resume = forms.CharField(max_length=100000)
    job = None
    
    def __init__(self, *args, **kwargs) -> None:
        job_choices = set(kwargs.pop('choices', []))
        self.CHOICES = self.CHOICES.union(job_choices)
        super().__init__(*args, **kwargs)
        self.fields['job'] = forms.ChoiceField(choices=list(self.CHOICES),)
        


 
class JobApplicationFormBuilder:
    def __init__(self, request=None) -> None:
        self.form = None
        self.job_choices = []
        self.request = request
    
    
    def add_job(self, job_choice:'tuple[str,str]'):
        self.job_choices.append(job_choice)
        return self
    
    def add_jobs(self, jobs_query_set):
        for job in jobs_query_set:
            job: 'Jobs'
            job_str = f"{job.title} at {job.company.company_name}"
            choice = (job.pk, job_str)
            self.job_choices.append(choice)
        return self
        

    def build(self):
        args = []
        kwargs = {}
        if self.request is not None:
            args = [self.request.POST,]
        kwargs['choices']  = self.job_choices
        self.form = JobApplicationForm(*args, **kwargs)

        return self.form