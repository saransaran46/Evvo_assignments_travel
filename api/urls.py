from django.urls import path
from .apis import RegisterUserView, LoginView, LogoutView, TravelRequestListCreateView, AdminTravelRequestListView, AdminTravelRequestDetailView, AdminApproveRejectView


urlpatterns = [
    path('api/register/', RegisterUserView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/travel-requests/', TravelRequestListCreateView.as_view(), name='travel_requests'),
    path('api/admin/travel-requests/', AdminTravelRequestListView.as_view(), name='admin_travel_requests'),
    path('api/admin/travel-requests/<int:pk>/', AdminTravelRequestDetailView.as_view(), name='admin_travel_request_detail'),
    path('api/admin/travel-requests/<int:pk>/approve-reject/', AdminApproveRejectView.as_view(), name='admin_travel_approve_reject'),
]
