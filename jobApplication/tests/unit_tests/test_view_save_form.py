

import itertools
import logging
import random
import re
from tkinter import NO
from typing import Any, Generator
import pytest
import django.db.models
import django.db.transaction
from jobApplication import models, forms, views
from jobApplication.tests.unit_tests.conftest import no_of_remaining_applications



@pytest.fixture
def non_emails():
    def _non_emails():
        #yield " "
        yield "ABCDEFGHIJK"
        yield "ABCDEF.GHIJK.com"
    return _non_emails


@pytest.fixture
def corr_data(email_not_in_db, 
              jobs_with_few_applications,
              db):
    def _corr_data():
        nonlocal email_not_in_db, jobs_with_few_applications
        for email in email_not_in_db():
            for job in jobs_with_few_applications():
                yield {'email' : email,
                        'job' : job.pk,
                        'first_name' : f'John',
                        'other_name' : f'Drake',
                        'resume' : "dfafa"}
    return _corr_data

@pytest.fixture
def wrong_data1(non_emails, jobs_with_few_applications,
                db):
    def _wrong_data1():
        nonlocal non_emails, jobs_with_few_applications

        for email in non_emails():
            for job in jobs_with_few_applications():
                for i, j in itertools.combinations(range(3), r=2):
                    yield {'email' : email,
                            'job' : job.pk,
                            'first_name' : f'John{i}',
                            'other_name' : f'Drake{j}',
                            'resume' : "dfafa"}
    
    return _wrong_data1

@pytest.fixture
def mass_apply(initialize_jobs,
                no_of_remaining_applications,
                jobs_with_few_applications,
                db):
    for job in jobs_with_few_applications():
        job:'models.Jobs'
        for application_no in range(no_of_remaining_applications(job)):
            data = {'email' : 'jon_snow@gmail.com',
                    'job' : job.pk,
                    'first_name' : f'John',
                    'other_name' : f'Drake',
                    'resume' : "my resume"}
            views.save_form(None, None, test_data=data)
        
@pytest.fixture
def wrong_data_with_jobs_with_enough_applications(
        mass_apply, 
        no_of_remaining_applications,
        jobs_with_enough_applications,
        email_not_in_db
    ):
    def _wrong_data():
        for job in jobs_with_enough_applications():
            for email in email_not_in_db():
                yield {'email' : 'jon_snow@gmail.com',
                        'job' : job.pk,
                        'max_applications' : job.max_applications,
                        'remaining_applications' : no_of_remaining_applications(job) ,
                        'first_name' : f'John',
                        'other_name' : f'Drake',
                        'resume' : "my resume"}
    return _wrong_data


@pytest.mark.django_db
def test_corr_data(corr_data):
    for data in corr_data():
        assert views.save_form(None, None, test_data=data)

# @pytest.mark.skip(reason="No email validation in db, just at form level")
# @pytest.mark.django_db
# def test_invalid_emails(wrong_data1):
#     assertion_errors = []
#     for data in wrong_data1():
#         logging.info(f'wrong_data1: {data}')
#         try:
#             assert views.save_form(None, None, test_data=data) == False, f'data wrongly sent to db: {data}'
#             logging.info(f'Assertion Passed: {data}')
#         except AssertionError as e:
#             assertion_errors.append(e)
#             logging.error(f'Assertion failed: {e}')
#             raise e

    
# @pytest.mark.django_db
# def test_invalid_jobs(wrong_data_with_jobs_with_enough_applications):
#     for data in wrong_data_with_jobs_with_enough_applications():
#         logging.warning(data)
#         assert views.save_form(None, None, test_data=data) == False
    