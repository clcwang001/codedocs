from django.contrib import admin
from .models import OrganisationDetails, UserHasOrganisation, Users, Activities, UserHasActivities

# Register your models here.
# Register your models here.
admin.site.register(Users)
admin.site.register(Activities)
admin.site.register(UserHasActivities)
admin.site.register(UserHasOrganisation)
admin.site.register(OrganisationDetails)
