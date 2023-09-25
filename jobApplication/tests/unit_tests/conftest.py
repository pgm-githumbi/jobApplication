


import logging
import random
import re
from typing import Any, Generator
import pytest
import django.db.models
import django.db.transaction
from jobApplication import models, forms, views





@pytest.fixture
def job_pk_not_in_db(db):
    job:'models.Jobs' = models.Jobs.objects.last()
    pk:'int' 
    if job is None:
        pk = 2
    else:
        pk = job.pk
    return pk

@pytest.fixture
def jobs_in_db(db):
    def _jobs():
        # Get all job IDs
        job_ids = list(models.Jobs.objects.values_list('id', flat=True))

        # Shuffle the job IDs
        random.shuffle(job_ids)

        # Iterate over the shuffled job IDs
        for job_id in job_ids:
            job_id = job_id[0]
            job = models.Jobs.objects.get(id=job_id)
            yield job

    return _jobs

@pytest.fixture(params=range(2), autouse=True)
def initialize_jobs(request, db):
    job_titles = ['CEO', 'CTO', 'Frontend React Developer', 'Backend Node Developer']
    companies = ['Facebook', 'Google', 'Canonical', 'Microsoft', 'Tiktok', 'Reddit']
        
    db_initialised = False
    for i in range(len(companies)):
        company, created = models.Companies.objects.get_or_create(
            company_name = companies[i], 
        )
        if created:
            logging.warning(f"{company} created: {created}")
        for j in range(len(job_titles)):
            with django.db.transaction.atomic():
                jobo, created = models.Jobs.objects.get_or_create(
                    company=company,
                    title=job_titles[j],
                    max_applications=request.param
                )
                #logging.warning(f"{jobo} created: {created}")
                
   



@pytest.fixture(params=[3])
def email_not_in_db(request, db):
    email = 'Peter_1@mail.org'
    no_of_emails = request.param
    def _email_not_in_db():
        nonlocal no_of_emails

        email_pattern = r"^peter_\d+@mail\.org$"
        q = django.db.models.Q(email__regex = email_pattern) 
        applicant = models.Applicant.objects.filter(q).last()
        if applicant is None:
            yield 'Peter_1@mail.org'
            no_of_emails -= 1
            if no_of_emails <= 0:
                yield from _email_not_in_db()
            return
        
        matches = re.match(r'peter_(\\d+)@mail\.org', applicant.email)
        if matches:
            extracted_int = int(matches.group(1)) + 1
        else:
            extracted_int = 2

        while no_of_emails > 0:
            yield f'Peter_{extracted_int}@mail.org'

            extracted_int += 1
            no_of_emails -= 1

    return _email_not_in_db

@pytest.fixture
def emails_in_db(db):
    def _emails_in_db():
        applicant_ids = list(models.Applicant.objects.values_list('id'))
        random.shuffle(applicant_ids)

        for id in applicant_ids:
            id = id[0]
            yield models.Applicant.objects.get(pk=id)
    return _emails_in_db()

@pytest.fixture
def emails_already_applied(db):
    def _emails_already_applied() -> Generator[str, Any, None]:
        applicant_ids = list((
            models.Applications.objects
            .values('applicant__email')
            .annotate(emails='applicant__email')
            .values_list('applicant__id'))
        )
        if len(applicant_ids) == 0:
            return
        random.shuffle(applicant_ids)
        for applicant_id in applicant_ids:
            applicant_id = applicant_id[0]
            yield models.Applicant.objects.get(id=applicant_id).email
    return _emails_already_applied



@pytest.fixture
def jobs_in_db(db, initialize_jobs):
    def _jobs_in_db():
        job_ids = list(models.Jobs.objects.values_list('id'))
        if len(job_ids) == 0:
            return
        
        random.shuffle(job_ids)
        for job_id in job_ids:
            job_id = job_id[0]
            yield models.Jobs.objects.get(id=job_id)
    return _jobs_in_db


@pytest.fixture
def jobs_with_few_applications(db, initialize_jobs):
    def _jobs_with_few_applications():
        jobs = (
            models.Jobs.objects
            .values('applications')
            .annotate(applications_made=django.db.models.Count("applications"))
            .filter(applications_made__lt=django.db.models.F("max_applications"))
            .values_list('id')
        )
        jobs = list(jobs)
        random.shuffle(jobs)
        if len(jobs) == 0:
            return
        
        for job_id in jobs:
            job_id = job_id[0]
            yield models.Jobs.objects.get(id=job_id)

    return _jobs_with_few_applications

@pytest.fixture
def jobs_with_enough_applications(db, initialize_jobs):
    def _jobs_with_enough_applications():
        jobs = (models.Jobs.objects
                .values('applications')
                .annotate(applications_count=django.db.models.Count("applications"))
                .filter(applications_count__exact=django.db.models.F("max_applications"))
                .values_list('id'))
        
        jobs = list(jobs)
        random.shuffle(jobs)
        if len(jobs) == 0:
            return
        
        for job_id in jobs:
            # job_id is a result set tuple 
            job_id = job_id[0]
            yield models.Jobs.objects.get(id=job_id)

    return _jobs_with_enough_applications



@pytest.fixture
def no_of_remaining_applications(initialize_jobs ,db):
    def _no_of_remaininag_applications(job:'models.Jobs'):
        logging.error(f"no of jobs in db: {models.Applications.objects.all().count()}")
        result = (
            models.Jobs.objects
            .filter(id=job.pk)
            .values('applications')
            .annotate(number_of_apps=
                      django.db.models.F("max_applications")
                    - django.db.models.Count('id'))
            .values_list('number_of_apps')
        )
        logging.error(f"No of remaining applications: {result}")
        return list(result)[0][0]
    return _no_of_remaininag_applications
        