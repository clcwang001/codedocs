from datetime import datetime
from decimal import Decimal
from operator import attrgetter
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout  
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.template import loader
from rest_framework import viewsets
from .models import OrganisationDetails, Users, Activities, UserHasActivities, UserHasOrganisation
from .serializers import OrganisationDetailsSerializer, UserHasOrganisationSerializer, UsersSerializer, ActivitiesSerializer, UserHasActivitiesSerializer
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import login as auth_login
from .forms import CustomUserCreationForm

def index(request):
    organisationalUsers = Users.objects.filter(userType=2, isOrganisation=True, isApprovedOrganisation=True)
    organisationalUserIds = organisationalUsers.values_list('userId', flat=True)
    organisationalDetails = OrganisationDetails.objects.filter(organisationId__in=organisationalUserIds)
    organisationalDonationDetails = UserHasOrganisation.objects.all()
    
    highestVals = [0, 0, 0]
    highestOrgs = [None, None,None]
    for item in organisationalDetails:
        donationsum = 0
        for item2 in organisationalDonationDetails:
            if item.organisationId == item2.organisation:
                donationsum += item2.donations
        if donationsum > highestVals[0]:
            highestVals[2] = highestVals[1]
            highestVals[1] = highestVals[0]
            highestVals[0] = donationsum
            highestOrgs[2] = highestOrgs[1]
            highestOrgs[1] = highestOrgs[0]
            highestOrgs[0] = item
        elif donationsum > highestVals[1]:
            highestVals[2] = highestVals[1]
            highestVals[1] = donationsum
            highestOrgs[2] = highestOrgs[1]
            highestOrgs[1] = item
        elif donationsum > highestVals[2]:
            highestVals[1] = donationsum
            highestOrgs[1] = item
        
        
    
    activities = Activities.objects.all()    
    activtySignups = UserHasActivities.objects.filter(isSignup=True)  
    
    mock_activities = []

    for activity in activities:
        mock_activity = MockActivity(
            activityId=activity.activityId,
            organisationId=activity.organisationId,
            title=activity.title,
            description=activity.description,
            activityImage1=activity.activityImage1,
            activityImage2=activity.activityImage2,
            activityImage3=activity.activityImage3,
            activityType=activity.activityType,
            maximumSignups=activity.maximumSignups,
            currentsignup=activtySignups.filter(activity=activity).count()
        )
        mock_activities.append(mock_activity)
    
    sorted_activities = sorted(mock_activities, key=attrgetter('currentsignup'), reverse=True)
    top3Activities = sorted_activities[:3]

    if request.user.is_authenticated:
        liked = UserHasActivities.objects.filter(user=request.user, isLiked=True)
        mock_activitiesLikedindex = []

        for signup in liked:
            for item in mock_activities:
                if item.activityId == signup.activity.activityId:
                    mock_activitiesLikedindex.append(item.activityId)

        userActivtySignups = UserHasActivities.objects.filter(user=request.user, isSignup=True)     
        mock_activitiesSignups = []

        for signup in userActivtySignups:
            for item in mock_activities:
                if item.activityId == signup.activity.activityId:
                    mock_activitiesSignups.append(item.activityId)
                    
        return render(request, 'Loginpage.html', {'userLoggedIn': request.user, 'organisations':highestOrgs, 'activities':top3Activities, 
                                                'likedActivities':mock_activitiesLikedindex,
                                                'registeredActivities':mock_activitiesSignups})
    else:
        return render(request, 'Loginpage.html', {'userLoggedIn':  {}, 'organisations':highestOrgs, 'activities':top3Activities})

class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

class ActivitiesViewSet(viewsets.ModelViewSet):
    queryset = Activities.objects.all()
    serializer_class = ActivitiesSerializer

class UserHasActivitiesViewSet(viewsets.ModelViewSet):
    queryset = UserHasActivities.objects.all()
    serializer_class = UserHasActivitiesSerializer
    
class UserHasOrganisationViewSet(viewsets.ModelViewSet):
    queryset = UserHasOrganisation.objects.all()
    serializer_class = UserHasOrganisationSerializer  
    
class OrganisationDetailsViewSet(viewsets.ModelViewSet):
    queryset = OrganisationDetails.objects.all()
    serializer_class = OrganisationDetailsSerializer  


class MockActivity:
    def __init__(self,activityId,organisationId,title,description,activityImage1,activityImage2,activityImage3,activityType,maximumSignups,currentsignup):
        self.activityId = activityId
        self.organisationId = organisationId
        self.title = title
        self.description = description 
        self.activityImage1 = activityImage1
        self.activityImage2 = activityImage2 
        self.activityImage3 = activityImage3
        self.activityType = activityType
        self.maximumSignups = maximumSignups
        self.currentsignup = currentsignup
        
class MockOrganisation:
    def __init__(self, organisationId,organisationName,organisationFocus,organisationShortDescription,
                 organisationLongDescription,organisationImage1,organisationImage2,organisationImage3,
                 acceptQrDonations,complains, donations, paidToDate):
        self.organisationId = organisationId
        self.organisationName = organisationName
        self.organisationFocus = organisationFocus
        self.organisationShortDescription = organisationShortDescription
        self.organisationLongDescription = organisationLongDescription
        self.organisationImage1 = organisationImage1
        self.organisationImage2 = organisationImage2
        self.organisationImage3 = organisationImage3
        self.acceptQrDonations = acceptQrDonations
        self.complains = complains
        self.donations = donations
        self.paidToDate = paidToDate
        
class MockReportDetails:
    def __init__(self, organisation,organisationName,reports ,donations):
        self.organisation = organisation
        self.reports = reports
        self.organisationName = organisationName
        self.donations = donations

class TopContrib:
    def __init__(self, User, donationsum, orgs):
        self.User = User
        self.donationsum = donationsum
        self.orgs = orgs
        
def userLogin(request):
    organisationalUsers = Users.objects.filter(userType=2, isOrganisation=True, isApprovedOrganisation=True)
    organisationalUserIds = organisationalUsers.values_list('userId', flat=True)
    organisationalDetails = OrganisationDetails.objects.filter(organisationId__in=organisationalUserIds)
    activities = Activities.objects.all()    
    activtySignups = UserHasActivities.objects.filter(isSignup=True)  
    organisationalDonationDetails = UserHasOrganisation.objects.all()
    
    highestVals = [0, 0, 0]
    highestOrgs = [None,None,None]
    for item in organisationalDetails:
        donationsum = 0
        for item2 in organisationalDonationDetails:
            if item.organisationId == item2.organisation:
                donationsum += item2.donations
        print("donationsum")
        print(donationsum)
        if donationsum > highestVals[0]:
            highestVals[2] = highestVals[1]
            highestVals[1] = highestVals[0]
            highestVals[0] = donationsum
            highestOrgs[2] = highestOrgs[1]
            highestOrgs[1] = highestOrgs[0]
            highestOrgs[0] = item
        elif donationsum > highestVals[1]:
            highestVals[2] = highestVals[1]
            highestVals[1] = donationsum
            highestOrgs[2] = highestOrgs[1]
            highestOrgs[1] = item
        elif donationsum > highestVals[2]:
            highestVals[1] = donationsum
            highestOrgs[1] = item
    print("highestOrgs")
    print(len(highestOrgs))
        
    mock_activities = []

    for activity in activities:
        mock_activity = MockActivity(
            activityId=activity.activityId,
            organisationId=activity.organisationId,
            title=activity.title,
            description=activity.description,
            activityImage1=activity.activityImage1,
            activityImage2=activity.activityImage2,
            activityImage3=activity.activityImage3,
            activityType=activity.activityType,
            maximumSignups=activity.maximumSignups,
            currentsignup=activtySignups.filter(activity=activity).count()
        )
        mock_activities.append(mock_activity)
    sorted_activities = sorted(mock_activities, key=attrgetter('currentsignup'), reverse=True)
    top3Activities = sorted_activities[:3]

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Username: {username}, Password: {password}")  

        user = Users.objects.filter(username=username).first()

        print(f"User: {user}")

        if user is not None:
            login(request, user)
            liked = UserHasActivities.objects.filter(user=request.user, isLiked=True)
            mock_activitiesLikedindex = []

            for signup in liked:
                for item in mock_activities:
                    if item.activityId == signup.activity.activityId:
                        mock_activitiesLikedindex.append(item.activityId)

            userActivtySignups = UserHasActivities.objects.filter(user=request.user, isSignup=True)     
            mock_activitiesSignups = []

            for signup in userActivtySignups:
                for item in mock_activities:
                    if item.activityId == signup.activity.activityId:
                        mock_activitiesSignups.append(item.activityId)
            
            return render(request, 'Loginpage.html', {'userLoggedIn': user, 'organisations': highestOrgs, 'activities': top3Activities,'likedActivities':mock_activitiesLikedindex,
                                                'registeredActivities':mock_activitiesSignups})
        else:
            error_message = "Invalid credentials. Please try again."
            return render(request, 'Loginpage.html', {'errormsg': error_message, 'organisations':highestOrgs, 'activities':top3Activities})
    return render(request, 'Loginpage.html', {'organisations': highestOrgs, 'activities': top3Activities, 'activtySignups':activtySignups})

def userLogout(request):
    organisationalUsers = Users.objects.filter(userType=2, isOrganisation=True, isApprovedOrganisation=True)
    organisationalUserIds = organisationalUsers.values_list('userId', flat=True)
    organisationalDetails = OrganisationDetails.objects.filter(organisationId__in=organisationalUserIds)
    activities = Activities.objects.all()
    activtySignups = UserHasActivities.objects.filter(isSignup=True)  
    organisationalDonationDetails = UserHasOrganisation.objects.all()
    
    highestVals = [0, 0, 0]
    highestOrgs = [None,None,None]
    for item in organisationalDetails:
        donationsum = 0
        for item2 in organisationalDonationDetails:
            if item.organisationId == item2.organisation:
                donationsum += item2.donations
        print("donationsum")
        print(donationsum)
        if donationsum > highestVals[0]:
            highestVals[2] = highestVals[1]
            highestVals[1] = highestVals[0]
            highestVals[0] = donationsum
            highestOrgs[2] = highestOrgs[1]
            highestOrgs[1] = highestOrgs[0]
            highestOrgs[0] = item
        elif donationsum > highestVals[1]:
            highestVals[2] = highestVals[1]
            highestVals[1] = donationsum
            highestOrgs[2] = highestOrgs[1]
            highestOrgs[1] = item
        elif donationsum > highestVals[2]:
            highestVals[1] = donationsum
            highestOrgs[1] = item
    print("highestOrgs")
    print(len(highestOrgs))
    mock_activities = []

    for activity in activities:
        mock_activity = MockActivity(
            activityId=activity.activityId,
            organisationId=activity.organisationId,
            title=activity.title,
            description=activity.description,
            activityImage1=activity.activityImage1,
            activityImage2=activity.activityImage2,
            activityImage3=activity.activityImage3,
            activityType=activity.activityType,
            maximumSignups=activity.maximumSignups,
            currentsignup=activtySignups.filter(activity=activity).count()
        )
        mock_activities.append(mock_activity)
    sorted_activities = sorted(mock_activities, key=attrgetter('currentsignup'), reverse=True)
    top3Activities = sorted_activities[:3]
    logout(request)
    return render(request, 'Loginpage.html', {'organisations': highestOrgs, 'activities': top3Activities})

@login_required(login_url='login')
def organisationHome(request):
    print(f"User: {request.user}")
    
    org_item = OrganisationDetails.objects.filter(organisationId = request.user).first()
    userHasOrgItems = UserHasOrganisation.objects.filter(organisation=org_item.organisationId).all()
    complains = 0
    donations = 0
    for user_item in userHasOrgItems:
        if user_item.complain:
            complains += 1
        if user_item.donations:
            donations += user_item.donations
                
    organisationDetailsUpdated = MockOrganisation(
            organisationId=org_item.organisationId,
            organisationName=org_item.organisationName,
            organisationFocus=org_item.organisationFocus,
            organisationShortDescription=org_item.organisationShortDescription,
            organisationLongDescription=org_item.organisationLongDescription,
            organisationImage1=org_item.organisationImage1,
            organisationImage2=org_item.organisationImage2,
            organisationImage3=org_item.organisationImage3,
            acceptQrDonations=org_item.acceptQrDonations,
            complains=complains,
            donations=donations,
            paidToDate=org_item.paidToDate
        )

    return render(request, 'OrganisationHome.html', {'userLoggedIn': request.user, 'organisationDetails':organisationDetailsUpdated, 'fromOrg':True})

def signup(request):
    activities = Activities.objects.all()
    organisationalUsers = Users.objects.filter(userType=2, isOrganisation=True)
    organisationalUserIds = organisationalUsers.values_list('userId', flat=True)
    organisationalDetails = OrganisationDetails.objects.filter(organisationId__in=organisationalUserIds)
    organisationalDonationDetails = UserHasOrganisation.objects.all()
    
    highestVals = [0, 0, 0]
    highestOrgs = [None,None,None]
    for item in organisationalDetails:
        donationsum = 0
        for item2 in organisationalDonationDetails:
            if item.organisationId == item2.organisation:
                donationsum += item2.donations
        print("donationsum")
        print(donationsum)
        if donationsum > highestVals[0]:
            highestVals[2] = highestVals[1]
            highestVals[1] = highestVals[0]
            highestVals[0] = donationsum
            highestOrgs[2] = highestOrgs[1]
            highestOrgs[1] = highestOrgs[0]
            highestOrgs[0] = item
        elif donationsum > highestVals[1]:
            highestVals[2] = highestVals[1]
            highestVals[1] = donationsum
            highestOrgs[2] = highestOrgs[1]
            highestOrgs[1] = item
        elif donationsum > highestVals[2]:
            highestVals[1] = donationsum
            highestOrgs[1] = item
    print("highestOrgs")
    print(len(highestOrgs))
    activtySignups = UserHasActivities.objects.filter(isSignup=True)  

    mock_activities = []

    for activity in activities:
        mock_activity = MockActivity(
            activityId=activity.activityId,
            organisationId=activity.organisationId,
            title=activity.title,
            description=activity.description,
            activityImage1=activity.activityImage1,
            activityImage2=activity.activityImage2,
            activityImage3=activity.activityImage3,
            activityType=activity.activityType,
            maximumSignups=activity.maximumSignups,
            currentsignup=activtySignups.filter(activity=activity).count()
        )
        mock_activities.append(mock_activity)
    sorted_activities = sorted(mock_activities, key=attrgetter('currentsignup'), reverse=True)
    top3Activities = sorted_activities[:3]   
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)  
            user.email = form.cleaned_data['email']
            user.username = form.cleaned_data['username']
            user.contactNumber = form.cleaned_data['contactNumber']
            user.isOrganisation = form.cleaned_data.get('isOrganisation', False)
            user.userType = 2
            isOrgnaisation = form.cleaned_data.get('isOrganisation', False)
            
            if isOrgnaisation:
                user.isNewUser = True

            user.save()

            print("Form values:")
            print("Email:", form.cleaned_data['email'])
            print("Username:", form.cleaned_data['username'])
            print("Contact Number:", form.cleaned_data['contactNumber'])
            print("Is Organisation:", form.cleaned_data.get('isOrganisation', False))

            login(request, user)
            return render(request, 'Loginpage.html', {'userLoggedIn': user,  'organisations':highestOrgs,'activities': top3Activities})

        else:
            print("Form errors:", form.errors)
            return render(request, 'Loginpage.html', {'userLoggedIn':  {}, 'organisations':highestOrgs, 'activities':top3Activities, 'errormsg':form.errors})
    else:
        form = CustomUserCreationForm()

        return render(request, 'Loginpage.html', {'userLoggedIn':  {}, 'organisations':highestOrgs, 'activities':top3Activities})

def userView(request, user_param):
    
    user = Users.objects.filter(username = user_param).first()
    
    organisationDetails = OrganisationDetails.objects.filter(organisationId = user.userId).first()
    activities = Activities.objects.filter(organisationId = user.userId).all()
    activtySignups = UserHasActivities.objects.filter(isSignup=True)  

    mock_activities = []

    for activity in activities:
        mock_activity = MockActivity(
            activityId=activity.activityId,
            organisationId=activity.organisationId,
            title=activity.title,
            description=activity.description,
            activityImage1=activity.activityImage1,
            activityImage2=activity.activityImage2,
            activityImage3=activity.activityImage3,
            activityType=activity.activityType,
            maximumSignups=activity.maximumSignups,
            currentsignup=activtySignups.filter(activity=activity).count()
        )
        mock_activities.append(mock_activity)

    userHasOrgItems = UserHasOrganisation.objects.filter(organisation = user.userId)
    complains = 0
    donations = 0
    for item in userHasOrgItems:
        if item.complain:
            complains += 1
        if item.donations:
            donations += item.donations   
        
    
    
    organisationDetailsUpdated = MockOrganisation(
        organisationId = organisationDetails.organisationId,
        organisationName = organisationDetails.organisationName,
        organisationFocus = organisationDetails.organisationFocus,
        organisationShortDescription = organisationDetails.organisationShortDescription,
        organisationLongDescription = organisationDetails.organisationLongDescription,
        organisationImage1 = organisationDetails.organisationImage1,
        organisationImage2 = organisationDetails.organisationImage2,
        organisationImage3 = organisationDetails.organisationImage3,
        acceptQrDonations = organisationDetails.acceptQrDonations,
        complains = complains,
        donations = donations,
        paidToDate=organisationDetails.paidToDate
    )
        
    if request.user.is_authenticated:
        #check if user has already reported org before
        reported = False
        userOrg = UserHasOrganisation.objects.filter(organisation = user, user=request.user).first()
        if userOrg:
            if userOrg.complain:
                reported = True
        return render(request, 'UserOrganisationView.html', {'userLoggedIn': request.user, 
                                                            'userType': request.user.userType, 
                                                            'isApprovedOrganisation': user.isApprovedOrganisation,
                                                            'rejectionReason': user.rejectionReason,
                                                            'recentlyUpdated': user.hasBeenUpdated,
                                                            'alreadyReported': reported,
                                                            'organisationDetails':organisationDetailsUpdated, 
                                                            'activities':mock_activities,  'fromOrg':False})
    else:
        return render(request, 'UserOrganisationView.html', {'userLoggedIn': {}, 
                                                            'userType':0, 
                                                            'isApprovedOrganisation': user.isApprovedOrganisation,
                                                            'rejectionReason': user.rejectionReason,
                                                            'recentlyUpdated': user.hasBeenUpdated,
                                                            'organisationDetails':organisationDetailsUpdated, 
                                                            'activities':mock_activities,  'fromOrg':False})


def OrganisationEvents(request, user_param):
    user = Users.objects.filter(username = user_param).first()

    activities = Activities.objects.filter(organisationId = user.userId).all()
    activtySignups = UserHasActivities.objects.filter(isSignup=True)  

    mock_activities = []

    for activity in activities:
        mock_activity = MockActivity(
            activityId=activity.activityId,
            organisationId=activity.organisationId,
            title=activity.title,
            description=activity.description,
            activityImage1=activity.activityImage1,
            activityImage2=activity.activityImage2,
            activityImage3=activity.activityImage3,
            activityType=activity.activityType,
            maximumSignups=activity.maximumSignups,
            currentsignup=activtySignups.filter(activity=activity).count()
        )
        mock_activities.append(mock_activity)
    return render(request, 'OrganisationEventsPage.html', {'userLoggedIn': request.user, 'activities':mock_activities})

def redirectToAllEvents(request):

    activities = Activities.objects.all()
    activtySignups = UserHasActivities.objects.filter(isSignup=True)  

    mock_activities = []

    for activity in activities:
        mock_activity = MockActivity(
            activityId=activity.activityId,
            organisationId=activity.organisationId,
            title=activity.title,
            description=activity.description,
            activityImage1=activity.activityImage1,
            activityImage2=activity.activityImage2,
            activityImage3=activity.activityImage3,
            activityType=activity.activityType,
            maximumSignups=activity.maximumSignups,
            currentsignup=activtySignups.filter(activity=activity).count()
        )
        mock_activities.append(mock_activity)
    
    userActivtySignups = UserHasActivities.objects.filter(user=request.user, isSignup=True)     
    mock_activitiesSignups = []

    for signup in userActivtySignups:
        for item in mock_activities:
            if item.activityId == signup.activity.activityId:
                mock_activitiesSignups.append(item.activityId)

    print("mock_activitiesSignups")
    print(mock_activitiesSignups)
    
    userActivtyLiked = UserHasActivities.objects.filter(user=request.user, isLiked=True)     
    mock_activitiesLiked = []

    for signup in userActivtyLiked:
        for item in mock_activities:
            if item.activityId == signup.activity.activityId:
                mock_activitiesLiked.append(item.activityId)

    print(mock_activitiesLiked)
    
        
    return render(request, 'allEvents.html', {'userLoggedIn': request.user, 
                                              'activities':mock_activities,
                                              'likedActivities':mock_activitiesLiked,
                                              'registeredActivities':mock_activitiesSignups})

def redirectToAllOrganisations(request):
    organisationalUsers = Users.objects.filter(userType=2, isOrganisation=True)
    organisationalUserIds = organisationalUsers.values_list('userId', flat=True)
    organisationalDetails = OrganisationDetails.objects.filter(organisationId__in=organisationalUserIds)
    
    return render(request, 'allOrganisations.html', {'userLoggedIn': request.user, 'organisations':organisationalDetails})

def orgReview(request):
    approvedArganisationalUsers = Users.objects.filter(userType=2, isOrganisation=True, isApprovedOrganisation=True)
    organisationalUserIds = approvedArganisationalUsers.values_list('userId', flat=True)
    organisationalDetails = OrganisationDetails.objects.filter(organisationId__in=organisationalUserIds).all()
    
    unapprovedArganisationalUsers = Users.objects.filter(userType=2, isOrganisation=True, isApprovedOrganisation=False, hasBeenUpdated=True)
    unapprovedOrganisationalUserIds = unapprovedArganisationalUsers.values_list('userId', flat=True)
    unapprovedOrganisationalDetails = OrganisationDetails.objects.filter(organisationId__in=unapprovedOrganisationalUserIds).all()
    
    rejectedArganisationalUsers = Users.objects.filter(userType=2, isOrganisation=True, isApprovedOrganisation=False, hasBeenUpdated=False)
    rejectedOrganisationalUserIds = rejectedArganisationalUsers.values_list('userId', flat=True)
    rejectedOrganisationalDetails = OrganisationDetails.objects.filter(organisationId__in=rejectedOrganisationalUserIds).all()
  
    
    print("organisationalDetails") 
    print(organisationalDetails) 
    print("unapprovedOrganisationalDetails") 
    print(unapprovedOrganisationalDetails) 
    return render(request, 'orgReview.html', {'userLoggedIn': request.user, 
                                              'organisations':organisationalDetails, 
                                              'organisationsToReview':unapprovedOrganisationalDetails,
                                              'rejectedOrganisations':rejectedOrganisationalDetails})
    
    
def updateEventDetails(request):     
    if request.method == 'POST':
        activity_id_str = request.POST.get('activityId')
        activity_id = int(activity_id_str) if activity_id_str and activity_id_str.isdigit() else 0
        title = request.POST.get('activityTitle')
        activity_type = request.POST.get('activityType')
        description = request.POST.get('activityDescription')
        maximum_signups = request.POST.get('maximumSignups')
        activity_image1 = request.FILES.get('activityImage1')
        activity_image2 = request.FILES.get('activityImage2')
        activity_image3 = request.FILES.get('activityImage3')
        print(title)
        print(activity_image1)

        if activity_id != 0:
            activity = Activities.objects.filter(activityId=activity_id).first()
            print(activity)
            activity.title = title
            activity.activityType = activity_type
            activity.description = description
            activity.maximumSignups = maximum_signups

            if activity_image1:
                activity.activityImage1 = activity_image1
            if activity_image2:
                activity.activityImage2 = activity_image2
            if activity_image3:
                activity.activityImage3 = activity_image3

            activity.save()            
        else:
            print("NO Activity ID")            
            new = Activities.objects.create(                
                    organisationId = request.user,
                    title = title,
                    description = description,
                    activityImage1 = activity_image1,
                    activityImage2 = activity_image2,
                    activityImage3 = activity_image3,
                    activityType = activity_type,
                    maximumSignups = maximum_signups
                    )
            new.save()        
               
        
    user = Users.objects.filter(username = request.user).first()
    activities = Activities.objects.filter(organisationId = user.userId).all()
   
    return redirect('OrganisationEvents', user_param=request.user) 

def eventSignup(request):
    user = Users.objects.filter(username=request.user).first()
    
    if not user.isOrganisation:
        activity_id = request.POST.get('activityId')
        activity = Activities.objects.filter(activityId=activity_id).first()
    
        user_activity = UserHasActivities.objects.filter(user=user, activity=activity).first()

        if not user_activity:
            new = UserHasActivities.objects.create(user=user, activity=activity)
            new.save()

            user_activity = UserHasActivities.objects.filter(user=user, activity=activity).first()
            
        user_activity.isSignup = True
        user_activity.save()
        return JsonResponse({'success': True})
    else: 
        return HttpResponseBadRequest('Invalid request')  

def removeEvent(request):
    user = Users.objects.filter(username=request.user).first()
    
    if not user.isOrganisation:
        activity_id = request.POST.get('activityId')
        activity = Activities.objects.filter(activityId=activity_id).first()
    
        user_activity = UserHasActivities.objects.filter(user=user, activity=activity).first()

        if not user_activity:
            new = UserHasActivities.objects.create(user=user, activity=activity)
            new.save()

            user_activity = UserHasActivities.objects.filter(user=user, activity=activity).first()
            
        user_activity.isSignup = False
        user_activity.save()
        return JsonResponse({'success': True})
    else: 
        return HttpResponseBadRequest('Invalid request')  


def updateOrganisationDetails(request):     
    if request.method == 'POST':
        organisationName = request.POST.get('organisationName')
        organisationFocus = request.POST.get('organisationFocus')
        organisationShortDescription = request.POST.get('organisationShortDescription')
        organisationLongDescription = request.POST.get('organisationLongDescription')
        acceptqr = True if request.POST.get('acceptQrDonations') else False
        print("acceptqr")
        print(acceptqr)
        organisationImage1 = request.FILES.get('organisationImage1')
        organisationImage2 = request.FILES.get('organisationImage2')
        organisationImage3 = request.FILES.get('organisationImage3')

        organisation = OrganisationDetails.objects.filter(organisationName=organisationName).first()
        
        organisation.organisationName = organisationName
        organisation.organisationFocus = organisationFocus
        organisation.organisationShortDescription = organisationShortDescription
        organisation.organisationLongDescription = organisationLongDescription
        organisation.acceptQrDonations = acceptqr

        if organisationImage1:
            organisation.organisationImage1 = organisationImage1
        if organisationImage2:
            organisation.organisationImage2 = organisationImage2
        if organisationImage3:
            organisation.organisationImage3 = organisationImage3
        organisation.save()   
        
        user = Users.objects.filter(username=organisationName).first()
        user.isApprovedOrganisation = False
        user.hasBeenUpdated = True
        user.reviewDate = None
        user.save()           
        
    org_item = OrganisationDetails.objects.filter(organisationId = request.user).first()
    userHasOrgItems = UserHasOrganisation.objects.filter(organisation=org_item.organisationId).all()
    complains = 0
    donations = 0
    for user_item in userHasOrgItems:
        if user_item.complain:
            complains += 1
        if user_item.donations:
            donations += user_item.donations
                
    organisationDetailsUpdated = MockOrganisation(
            organisationId=org_item.organisationId,
            organisationName=org_item.organisationName,
            organisationFocus=org_item.organisationFocus,
            organisationShortDescription=org_item.organisationShortDescription,
            organisationLongDescription=org_item.organisationLongDescription,
            organisationImage1=org_item.organisationImage1,
            organisationImage2=org_item.organisationImage2,
            organisationImage3=org_item.organisationImage3,
            acceptQrDonations=org_item.acceptQrDonations,
            complains=complains,
            donations=donations,
            paidToDate=org_item.paidToDate
        )
   
    return render(request, 'OrganisationHome.html', {'userLoggedIn': request.user, 'organisationDetails':organisationDetailsUpdated, 'fromOrg':True})


def organisationApproval(request):     
    if request.method == 'POST':
        organisationName = request.POST.get('organisationId')
        
        organisation = Users.objects.filter(username=organisationName).first()
        organisation.isApprovedOrganisation = True
        organisation.rejectionReason = ""
        organisation.hasBeenUpdated = False
        organisation.reviewDate = datetime.now()
        organisation.save()             
        
    return JsonResponse({'success': True})

def organisationRejecton(request):     
    if request.method == 'POST':
        organisationName = request.POST.get('organisationId')
        rejectionReason = request.POST.get('rejectionReason')
        organisation = Users.objects.filter(username=organisationName).first()
        organisation.isApprovedOrganisation = False
        organisation.rejectionReason = rejectionReason
        organisation.hasBeenUpdated = False
        organisation.reviewDate = datetime.now()
        organisation.save()             
        
    return JsonResponse({'success': True})

def reportOrg(request):     
    if request.method == 'POST':
        organisationName = request.POST.get('organisationId')
        orgitem = Users.objects.filter(username = organisationName).first()
        
        userhasorgitem = UserHasOrganisation.objects.filter(organisation=orgitem,user=request.user).first()
        print(userhasorgitem)
        if userhasorgitem:            
            userhasorgitem.complain = True
            userhasorgitem.save()
            
        else:
            new = UserHasOrganisation.objects.create(organisation=orgitem, user=request.user, complain=True)
            new.save()
        
    return JsonResponse({'success': True})

def Vigilance(request):
    approvedOrganisationalUsers = Users.objects.filter(userType=2, isOrganisation=True, isApprovedOrganisation=True)
    organisationalUserIds = approvedOrganisationalUsers.values_list('userId', flat=True)
    organisationalDetails = OrganisationDetails.objects.filter(organisationId__in=organisationalUserIds).all()

    organisationDetailsUpdatedlist = []

    for org_item in organisationalDetails:
        userHasOrgItems = UserHasOrganisation.objects.filter(organisation=org_item.organisationId).all()
        complains = 0
        donations = 0

        for user_item in userHasOrgItems:
            if user_item.complain:
                complains += 1
            if user_item.donations:
                donations += user_item.donations

        organisationDetailsUpdated = MockOrganisation(
            organisationId=org_item.organisationId,
            organisationName=org_item.organisationName,
            organisationFocus=org_item.organisationFocus,
            organisationShortDescription=org_item.organisationShortDescription,
            organisationLongDescription=org_item.organisationLongDescription,
            organisationImage1=org_item.organisationImage1,
            organisationImage2=org_item.organisationImage2,
            organisationImage3=org_item.organisationImage3,
            acceptQrDonations=org_item.acceptQrDonations,
            paidToDate=org_item.paidToDate,
            complains=complains,
            donations=donations
        )
        organisationDetailsUpdatedlist.append(organisationDetailsUpdated)

    organisationDetailsUpdatedlist.sort(key=lambda x: x.donations, reverse=True)

    return render(request, 'orgVigilance.html', {'userLoggedIn': request.user,
                                                  'organisations': organisationDetailsUpdatedlist,
                                                })
    
    
def myProfile(request):
    return render(request, 'profilePage.html', {'userLoggedIn': request.user})


def updateMyProfile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        contact = request.POST.get('contactNumber')
        orgitem = Users.objects.filter(username = username).first()
        orgitem.email = email
        orgitem.contactNumber = contact
        orgitem.save()
        
    return JsonResponse({'success': True})

def myActivities(request):
    activities = Activities.objects.all()
    activtySignups = UserHasActivities.objects.filter(isSignup=True)  

    mock_activities = []
    mock_activitiesSignUp = []

    for activity in activities:
        mock_activity = MockActivity(
            activityId=activity.activityId,
            organisationId=activity.organisationId,
            title=activity.title,
            description=activity.description,
            activityImage1=activity.activityImage1,
            activityImage2=activity.activityImage2,
            activityImage3=activity.activityImage3,
            activityType=activity.activityType,
            maximumSignups=activity.maximumSignups,
            currentsignup=activtySignups.filter(activity=activity).count()
        )
        mock_activities.append(mock_activity)
        
    meActivitySignups = UserHasActivities.objects.filter(user=request.user, isSignup=True)
    mock_activitiesSignUp = []
    mock_activitiesSignUpIndex = []
    for signup in meActivitySignups:
        for item in mock_activities:
            if item.activityId == signup.activity.activityId:
                mock_activitiesSignUp.append(item)
                mock_activitiesSignUpIndex.append(item.activityId)
    print(mock_activitiesSignUp)
        
    return render(request, 'userEvents.html', {'userLoggedIn': request.user, 
                                               'activities':mock_activitiesSignUp, 
                                               'likedActivities': [],
                                               'registeredActivities':mock_activitiesSignUpIndex,
                                               'isSignup':True})

def LikedActivities(request):
    activities = Activities.objects.all()
    activtySignups = UserHasActivities.objects.filter(isSignup=True)  

    mock_activities = []
    mock_activitiesSignUp = []

    for activity in activities:
        mock_activity = MockActivity(
            activityId=activity.activityId,
            organisationId=activity.organisationId,
            title=activity.title,
            description=activity.description,
            activityImage1=activity.activityImage1,
            activityImage2=activity.activityImage2,
            activityImage3=activity.activityImage3,
            activityType=activity.activityType,
            maximumSignups=activity.maximumSignups,
            currentsignup=activtySignups.filter(activity=activity).count()
        )
        mock_activities.append(mock_activity)
        
    liked = UserHasActivities.objects.filter(user=request.user, isSignup=False, isLiked=True)
    mock_activitiesLiked = []
    mock_activitiesLikedindex = []

    for signup in liked:
        for item in mock_activities:
            if item.activityId == signup.activity.activityId:
                mock_activitiesLiked.append(item)
                mock_activitiesLikedindex.append(item.activityId)

    print(mock_activitiesLiked)
        
    return render(request, 'userEvents.html', {'userLoggedIn': request.user, 
                                               'activities':mock_activitiesLiked,
                                               'likedActivities':mock_activitiesLikedindex,
                                               'registeredActivities':[],
                                                'isSignup':False})


def eventLike(request):
    user = Users.objects.filter(username=request.user).first()
    
    if not user.isOrganisation:
        activity_id = request.POST.get('activityId')
        activity = Activities.objects.filter(activityId=activity_id).first()
    
        user_activity = UserHasActivities.objects.filter(user=user, activity=activity).first()

        if not user_activity:
            new = UserHasActivities.objects.create(user=user, activity=activity)
            new.save()

            user_activity = UserHasActivities.objects.filter(user=user, activity=activity).first()
            
        user_activity.isLiked = True
        user_activity.save()
        return JsonResponse({'success': True})
    else: 
        return HttpResponseBadRequest('Invalid request')  

def eventUnlike(request):
    user = Users.objects.filter(username=request.user).first()
    
    if not user.isOrganisation:
        activity_id = request.POST.get('activityId')
        activity = Activities.objects.filter(activityId=activity_id).first()
    
        user_activity = UserHasActivities.objects.filter(user=user, activity=activity).first()

        if not user_activity:
            new = UserHasActivities.objects.create(user=user, activity=activity)
            new.save()

            user_activity = UserHasActivities.objects.filter(user=user, activity=activity).first()
            
        user_activity.isLiked = False
        user_activity.save()
        return JsonResponse({'success': True})
    else: 
        return HttpResponseBadRequest('Invalid request')  
    
def addDonationAmount(request):
    if request.method == 'POST':
        organisationName = request.POST.get('organisationDetails')
        donationAmount = request.POST.get('donationAmount')
        print(organisationName)
        print(donationAmount)
        orgitem = Users.objects.filter(username = organisationName).first()
        
        userhasorgitem = UserHasOrganisation.objects.filter(organisation=orgitem,user=request.user).first()
        print(userhasorgitem)
        if userhasorgitem:            
            userhasorgitem.donations = userhasorgitem.donations + Decimal(donationAmount)
            userhasorgitem.save()
            
        else:
            new = UserHasOrganisation.objects.create(organisation=orgitem, user=request.user, complain=False, donations=donationAmount)
            new.save()
        
    return JsonResponse({'success': True})

def addPayout(request):
    if request.method == 'POST':
        organisationName = request.POST.get('donationOrganisationId')
        donationValue = request.POST.get('donationValue')
        print(organisationName)
        print(donationValue)
        orgitem = Users.objects.filter(username = organisationName).first()
        orgdetails = OrganisationDetails.objects.filter(organisationId = orgitem).first()
        orgdetails.paidToDate += Decimal(donationValue)
        orgdetails.save()
        
    approvedOrganisationalUsers = Users.objects.filter(userType=2, isOrganisation=True, isApprovedOrganisation=True)
    organisationalUserIds = approvedOrganisationalUsers.values_list('userId', flat=True)
    organisationalDetails = OrganisationDetails.objects.filter(organisationId__in=organisationalUserIds).all()

    organisationDetailsUpdatedlist = []

    for org_item in organisationalDetails:
        userHasOrgItems = UserHasOrganisation.objects.filter(organisation=org_item.organisationId).all()
        complains = 0
        donations = 0

        for user_item in userHasOrgItems:
            if user_item.complain:
                complains += 1
            if user_item.donations:
                donations += user_item.donations

        organisationDetailsUpdated = MockOrganisation(
            organisationId=org_item.organisationId,
            organisationName=org_item.organisationName,
            organisationFocus=org_item.organisationFocus,
            organisationShortDescription=org_item.organisationShortDescription,
            organisationLongDescription=org_item.organisationLongDescription,
            organisationImage1=org_item.organisationImage1,
            organisationImage2=org_item.organisationImage2,
            organisationImage3=org_item.organisationImage3,
            acceptQrDonations=org_item.acceptQrDonations,
            paidToDate=org_item.paidToDate,
            complains=complains,
            donations=donations
        )
        organisationDetailsUpdatedlist.append(organisationDetailsUpdated)

    organisationDetailsUpdatedlist.sort(key=lambda x: x.donations, reverse=True)

    return render(request, 'orgVigilance.html', {'userLoggedIn': request.user,
                                                  'organisations': organisationDetailsUpdatedlist,
                                                })

def createDetails(request):
    print("OK")
    if request.method == 'POST':
        orgUser = request.user
        organisationName = request.POST.get('organisationName')
        organisationFocus = request.POST.get('organisationFocus')
        organisationShortDescription = request.POST.get('organisationShortDescription')
        organisationLongDescription = request.POST.get('organisationLongDescription')
        acceptqr = True if request.POST.get('acceptQrDonations') else False
        organisationImage1 = request.FILES.get('organisationImage1')
        organisationImage2 = request.FILES.get('organisationImage2')
        organisationImage3 = request.FILES.get('organisationImage3')
        print(request.user.userId)
        print(request.user.username)
        print(organisationImage1)
        print(organisationImage2)

        new = OrganisationDetails.objects.create(organisationId=request.user, 
                                                  organisationName=request.user.username, 
                                                  organisationFocus=organisationFocus, 
                                                  organisationShortDescription=organisationShortDescription,
                                                  organisationLongDescription = organisationLongDescription,
                                                  organisationImage1=organisationImage1,
                                                  organisationImage2= organisationImage2,
                                                  organisationImage3= organisationImage3,
                                                  acceptQrDonations= acceptqr)
        new.save()
        
        user = Users.objects.filter(userId = request.user.userId).first()
        user.isApprovedOrganisation = False
        user.hasBeenUpdated = True
        user.isNewUser = False
        user.save()
        
    org_item = OrganisationDetails.objects.filter(organisationId = request.user).first()
    userHasOrgItems = UserHasOrganisation.objects.filter(organisation=org_item.organisationId).all()
    complains = 0
    donations = 0
    for user_item in userHasOrgItems:
        if user_item.complain:
            complains += 1
        if user_item.donations:
            donations += user_item.donations
                
    organisationDetailsUpdated = MockOrganisation(
            organisationId=org_item.organisationId,
            organisationName=org_item.organisationName,
            organisationFocus=org_item.organisationFocus,
            organisationShortDescription=org_item.organisationShortDescription,
            organisationLongDescription=org_item.organisationLongDescription,
            organisationImage1=org_item.organisationImage1,
            organisationImage2=org_item.organisationImage2,
            organisationImage3=org_item.organisationImage3,
            acceptQrDonations=org_item.acceptQrDonations,
            complains=complains,
            donations=donations,
            paidToDate=org_item.paidToDate
        )
    
    return render(request, 'OrganisationHome.html', {'userLoggedIn': request.user, 'organisationDetails':organisationDetailsUpdated, 'fromOrg':True})

@login_required(login_url='login')
def topContributors(request):
    if request.user.userType == 1:
        print("TYPE Admin")
        donationusers = UserHasOrganisation.objects.all()
        results = []
        for item in donationusers:
            user_exists = False

            for result in results:
                if result.User == item.user:
                    result.donationsum+=item.donations
                    result.orgs.append({'org': item.organisation, 'donation': item.donations})
                    user_exists = True
            if not user_exists: 
                
                result = TopContrib(
                        User= item.user,
                        donationsum=item.donations,    
                        orgs=[{'org': item.organisation, 'donation': item.donations}],  # Create a new list of dictionaries
                )
                results.append(result)
        
        
        sorted_users=sorted(results, key=attrgetter('donationsum'), reverse=True)
        topDonors = sorted_users[:10]
        
        return render(request, 'TopContrib.html', {'userLoggedIn': request.user, 'results':topDonors})

    elif request.user.userType == 2 and request.user.isOrganisation: 
        print("TYPE NOTADMIN ") 
        donationusers = UserHasOrganisation.objects.filter(organisation = request.user)
        sorted_users=sorted(donationusers, key=attrgetter('donations'), reverse=True)
        topDonors = sorted_users[:10]
        results = []
        for item in topDonors:
            result = TopContrib(
                User= item.user,
                donationsum=item.donations,
                orgs=[]
            )
            results.append(result)
        return render(request, 'TopContrib.html', {'userLoggedIn': request.user, 'results':results})
    else:
        return render(request, 'TopContrib.html', {'userLoggedIn': request.user, 'results':[]})
