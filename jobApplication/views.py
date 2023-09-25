
import logging
from sqlite3 import DatabaseError, IntegrityError
from typing import Callable
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import Applicant, Applications, Jobs, Companies, available_jobs
from .forms import JobApplicationForm, JobApplicationFormBuilder
from django.db import DataError, Error, OperationalError, models, transaction
from django.urls import reverse




# Create your views here.
def application_success(request):
    return render(request, 'jobApplication/form_submission_success.html')

def index(request):
    # Query to return jobs with less applications than
    # `max_applications`
    form, template_name = None, 'jobApplication/index.html'
    if request.method == 'POST':
        form_builder = JobApplicationFormBuilder(request)
        form_builder.add_jobs(available_jobs())
        form = form_builder.build()

        if form.is_valid():
            if save_form(form) == True:
                return form_successfully_stored()
        else:
            print('Form was invalid: ', form_builder.build().fields['job'].choices, '\n')
            return render(request, template_name, {'form' : form_builder.build()})

    form_builder = JobApplicationFormBuilder()
    form_builder.add_jobs(available_jobs())
    form = form_builder.build()
    
    print('New Form Request: ',form.fields['job'].choices, '\n')
    return render(request, template_name, {'form' : form})

def save_form(form:'JobApplicationForm', is_repeat_application:'Callable'=None,
              test_data=None):
    cleaned_data = test_data or form.cleaned_data
    email = cleaned_data['email']
    first_name = cleaned_data['first_name']
    last_name = cleaned_data['other_name']
    job = cleaned_data['job']
    job = Jobs.objects.get(pk=job)
    resume = cleaned_data['resume']
    try:
        with transaction.atomic():
            applicant, _ = Applicant.objects.get_or_create(
                email= email, first_name=first_name, last_name=last_name,
                defaults={}
            )

            application, created = Applications.objects.get_or_create(
                applicant=applicant, job=job, defaults={'resume_text' : resume}
            )
    except (DataError, IntegrityError, ) as e:
        if form:
            form.add_error(None, 'Something went wrong. The application was not stored')
        return False
    except OperationalError as e:
        logging.warning(e)
        if form:
            form.add_error(None, 'Something went wrong. The application was not stored')
        return False
    except Error as e:
        logging.warning(e)
        if form:
            form.add_error(None, 'Something went wrong. The application was not stored')
        return False
    
    
    
    if not created:
        if form:
            form.add_error(None, 'This application was already submitted')
        print(f'This application was already submitted')
    if not created and is_repeat_application != None:
        is_repeat_application()
    return True
    

def form_successfully_stored():
    return HttpResponseRedirect(reverse('success_page'))



    
        

    


    