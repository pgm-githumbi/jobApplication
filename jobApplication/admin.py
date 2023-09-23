from django.contrib import admin
from .models import Applicant, Applications, Jobs, Companies

# Register your models here.
admin.site.register(Applications)
admin.site.register(Jobs)
admin.site.register(Applicant)
admin.site.register(Companies)
