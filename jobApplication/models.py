from django.db import models
from django.utils import timezone


# Create your models here.

class Applicant(models.Model):
    email = models.EmailField(unique=True, null=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    def __str__(self) -> str:
        return f"{self.email}, {self.first_name}"

class Companies(models.Model):
    company_name = models.CharField(max_length=255)
    def __str__(self) -> str:
        return f"{self.company_name}"

class Jobs(models.Model):
    title = models.TextField()
    company = models.ForeignKey(to=Companies, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    max_applications = models.IntegerField()
    def __str__(self) -> str:
        return f"{self.title} at {str(self.company)}"

class Applications(models.Model):
    applicant = models.ForeignKey(to=Applicant, on_delete=models.CASCADE)
    job = models.ForeignKey(to=Jobs, on_delete=models.CASCADE)
    application_time = models.DateTimeField(default=timezone.now)
    resume_text = models.TextField(max_length=10000, editable=True, 
                                   default='No Resume')
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['applicant', 'job'],
                                     name='unique_composite_key')
        ]

    def __str__(self) -> str:
        return f"{self.applicant} for {str(self.job)}"




def available_jobs():
    return (
        Jobs.objects
            .annotate(appl_count=models.Count('applications'))
            .filter(appl_count__lt=models.F('max_applications'))
    )

