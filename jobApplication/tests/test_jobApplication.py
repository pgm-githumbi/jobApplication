
from operator import contains
from urllib import response
from django import test
from typing import Any, Generator, Literal
import django.db.models
from django.http import HttpResponse, HttpResponseRedirect
import bs4
import django.urls

from rest_framework import status
import pytest
from django.test import RequestFactory
from .. import views, forms, models

@pytest.fixture
def make_company_record():
    def _make_company_record(company_no:'int'):
        return models.Companies.objects.create(company_name=f'Google_v{company_no}')
        
    
    yield _make_company_record


@pytest.fixture(params=range(0, 20, 4))
def make_job_record(request: type[pytest.FixtureRequest],
                     make_company_record):
    max_applications = request.param
    
    def _make_job_record(job_no:'int', company_no:'int'):
        nonlocal max_applications
        company:'models.Companies' = make_company_record(company_no)
        return models.Jobs.objects.create(
            title=f'Software Eng {job_no}',
            company=company,
            max_applications=max_applications
        )
    
    yield _make_job_record

@pytest.fixture(params=range(10))
def company_no(request)-> 'int':
    return request.param

@pytest.fixture(params=range(10))
def job_no(request: type[pytest.FixtureRequest], company_no: int):
    return range(request.param)

@pytest.fixture
def job_no_company_no_pair(job_no: 'range', company_no: int):
    def _pair() -> Generator[tuple[int, int], Any, None]:
        for next_job_no in job_no:
            yield  next_job_no, company_no
    return _pair

@pytest.fixture
def jobs(make_job_record, job_no_company_no_pair):
    def _job():
        nonlocal job_no_company_no_pair
        for job_no_value, company_no_value in job_no_company_no_pair():
            job:'models.Jobs' = make_job_record(job_no_value, company_no_value)
            yield job
    yield _job

@pytest.fixture(params=range(20))
def form_data(
        request: type[pytest.FixtureRequest], 
        jobs
    ):
    def _form_data():
        nonlocal request
        nonlocal jobs
        for job in jobs:
            job:'models.Jobs'
            yield {
                'first_name': f'John_{request.param}',
                'other_name' : f'Snow_{request.param}',
                'email' : f'john_{request.param}_snow@mail.org',
                'job' : job.pk,
                'resume' : f'Hi I have 4 yrs of fake exp{request.param}'
            }

    yield _form_data

@pytest.fixture
def remaining_allowed_applications(job:'models.Jobs'):
    return (
        models.Applications.objects.filter(job=job)
        .aggregate(
            remaining_applications=
            django.db.models.functions.Coalesce(
                django.db.models.F('job__max_applications') - django.db.models.Count('*'),
                django.db.models.Value('job.max_applications')
            )
        )
    )

@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()

@pytest.fixture
def url() -> Literal['jobApplication/']:
    return 'jobApplication/'

@pytest.fixture()
def initial_get_request(request_factory: RequestFactory, url: Literal['jobApplication/']):
    return request_factory.get(url)


@pytest.fixture
def post_requests(request_factory: RequestFactory, url: Literal['jobApplication/'],
                  form_data: dict[str, str]):
    def _post_requests():
        nonlocal form_data
        nonlocal request_factory
        nonlocal url
        for data in form_data():
            yield request_factory.post(url, data=data)

    return _post_requests

@pytest.fixture(params=[1, 2])
def client(request):
    return test.Client()


def get_fields_and_expected_initials(empty_form:'forms.JobApplicationForm'):
    for field in empty_form.fields:
        yield field, empty_form.fields[field].initial

def is_successful_response(response):
    if status.is_redirect(response.status_code):
        if response.url != django.urls.reverse('success_page'):
            return False
        return True
    return status.is_success(response.status_code)

@pytest.mark.django_db
def test_initial_get(client: test.Client, initial_get_request):
    response = client.get(initial_get_request)
    assert status.is_success(response.status_code)
    assert 'form' in response.context

    rendered_form:'forms.JobApplicationForm' = response.context['form']
    assert isinstance(rendered_form, forms.JobApplicationForm)
  
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    assert soup.find('form', {'method' : 'post'}) is not None

    empty_form = forms.JobApplicationForm()
    # assert there's an input tag with names of each field
    for field_name in empty_form.fields:
        assert soup.find('input', {'name' : field_name})
     
    select_tag = soup.select_one('#id_job')
    assert select_tag is not None
    for option_tag in select_tag.find_all('option'):
        job_pk = int(option_tag['value'])
        # assert that this job exists
        assert models.Jobs.objects.filter(pk=job_pk).exists()

    

    
def test_posts(client: test.Client, form_data, 
               initial_get_request):
    response = client.get(initial_get_request)
    
    

    

    

    


@pytest.mark.django_db
def test_correct_posts(post_requests):
    for post_request in post_requests():
        response = test.Client().post(post_request)
        
        assert status.is_redirect(response.status_code)
        assert response.url == '/jobApplication/form_submission_success.html/'



        
            


