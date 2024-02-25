from rest_framework import serializers
from .models import OrganisationDetails, UserHasOrganisation, Users, Activities, UserHasActivities

class UsersSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Users
        fields = ('userId', 'userType', 'username', 'password', 'email', 'contactNumber', 'isOrganisation', 'isApprovedOrganisation')

class ActivitiesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Activities
        fields = '__all__'

class UserHasActivitiesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserHasActivities
        fields = '__all__'
        
class UserHasOrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHasOrganisation
        fields = '__all__'
        
class OrganisationDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationDetails
        fields = '__all__'