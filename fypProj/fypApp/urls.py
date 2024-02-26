from django.urls import include, path
from rest_framework import routers
from . import views
from .views import userLogin, userLogout, signup

router = routers.DefaultRouter()
router.register(r'users',views.UsersViewSet)


urlpatterns = [
    path('home/', views.index, name= 'index'),
    path('organisationHome/', views.organisationHome, name= 'organisationHome'),
    path('orgReview/', views.orgReview, name= 'orgReview'),
    path('redirectToAllEvents/', views.redirectToAllEvents, name= 'redirectToAllEvents'),
    path('redirectToAllOrganisations/', views.redirectToAllOrganisations, name= 'redirectToAllOrganisations'),
    path('userView/<str:user_param>/', views.userView, name='userView'),
    path('updateEventDetails/', views.updateEventDetails, name='updateEventDetails'),    
    path('updateOrganisationDetails/', views.updateOrganisationDetails, name='updateOrganisationDetails'),
    path('organisation/<str:user_param>/', views.userView, name='organisation'),
    path('OrganisationEvents/<str:user_param>/', views.OrganisationEvents, name='OrganisationEvents'),
    path('organisationApproval/', views.organisationApproval, name='organisationApproval'),
    path('organisationRejecton/', views.organisationRejecton, name='organisationRejecton'),
    path('eventSignup/', views.eventSignup, name='eventSignup'),
    path('removeEvent/', views.removeEvent, name='removeEvent'),
    path('reportOrg/', views.reportOrg, name='reportOrg'),
    path('Vigilance/', views.Vigilance, name='Vigilance'),
    path('myProfile/', views.myProfile, name='myProfile'),
    path('updateMyProfile/', views.updateMyProfile, name='updateMyProfile'),
    path('myActivities/', views.myActivities, name='myActivities'),
    path('LikedActivities/', views.LikedActivities, name='LikedActivities'),    
    path('eventLike/', views.eventLike, name='eventLike'), 
    path('eventUnlike/', views.eventUnlike, name='eventUnlike'),
    path('addDonationAmount/', views.addDonationAmount, name='addDonationAmount'),
    path('addPayout/', views.addPayout, name='addPayout'),
    path('topContributors/', views.topContributors, name='topContributors'),
    path('', include(router.urls)),
    path('login/', userLogin, name='login'),
    path('logout/', userLogout, name='logout'), 
    path('signup/', signup, name='signup'),
    path('createDetails/', views.createDetails, name='createDetails'),
    path('api-auth/',include('rest_framework.urls', namespace='rest_framework'))
]