from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, TravelRequest
from datetime import datetime




# User Registration API
class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

# User Login API
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Both username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin
            }
        }, status=status.HTTP_200_OK)

# User Logout API
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# Travel Request API (User)
class TravelRequestListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        requests = TravelRequest.objects.filter(user=request.user).values()
        return Response(requests, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data

        # Extract required fields
        project_name = data.get('project_name')
        purpose_travel = data.get('purpose_travel')
        travel_start_date = data.get('travel_start_date')
        travel_mode = data.get('travel_mode')
        ticket_booking_mode = data.get('ticket_booking_mode')
        travel_start_loc = data.get('travel_start_loc')
        travel_end_loc = data.get('travel_end_loc')

        # Validate required fields
        if not all([project_name, purpose_travel, travel_start_date, travel_mode, ticket_booking_mode, travel_start_loc, travel_end_loc]):
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate date format
        try:
            travel_start_date = datetime.strptime(travel_start_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        # Create and save the travel request
        travel_request = TravelRequest.objects.create(
            user=request.user,
            project_name=project_name,
            purpose_travel=purpose_travel,
            travel_start_date=travel_start_date,
            travel_mode=travel_mode,
            ticket_booking_mode=ticket_booking_mode,
            travel_start_loc=travel_start_loc,
            travel_end_loc=travel_end_loc
        )

        return Response({'message': 'Travel request submitted successfully', 'id': travel_request.id}, status=status.HTTP_201_CREATED)






# 1️⃣ API: List All Travel Requests (Admin)
class AdminTravelRequestListView(APIView):
    """
    API to display all created travel requests in a table format.
    Only Admins can access this.
    """
    permission_classes = [permissions.IsAdminUser]  # Only admin users can access

    def get(self, request):
        travel_requests = TravelRequest.objects.all().values()
        return Response(travel_requests, status=status.HTTP_200_OK)


# 2️⃣ API: Get Travel Request Details (Admin)
class AdminTravelRequestDetailView(APIView):
    """
    API to view details of a specific travel request.
    Only Admins can access this.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk):
        travel_request = get_object_or_404(TravelRequest, pk=pk)
        data = {
            "id": travel_request.id,
            "user": travel_request.user.username,
            "project_name": travel_request.project_name,
            "purpose_travel": travel_request.purpose_travel,
            "travel_start_date": travel_request.travel_start_date,
            "travel_mode": travel_request.travel_mode,
            "ticket_booking_mode": travel_request.ticket_booking_mode,
            "travel_start_loc": travel_request.travel_start_loc,
            "travel_end_loc": travel_request.travel_end_loc,
            "status": travel_request.status,
        }
        return Response(data, status=status.HTTP_200_OK)


# 3️⃣ API: Approve/Reject Travel Request (Admin)
class AdminApproveRejectView(APIView):
    """
    API for Admin to approve or reject a travel request.
    Only Admin users can perform this action.
    """
    permission_classes = [permissions.IsAdminUser]  # Only admins can approve/reject

    def patch(self, request, pk):
        """
        Update the status of a travel request.

        Expected Payload:
        {
            "status": "approved" or "rejected"
        }
        """

        # Fetch the travel request instance
        travel_request = get_object_or_404(TravelRequest, pk=pk)

        # Extract new status from request data
        new_status = request.data.get('status')

        # Check if the status is valid
        if new_status not in ['approved', 'rejected']:
            return Response({'error': 'Invalid status. Choose either "approved" or "rejected".'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if the request is already in the same status
        if travel_request.status == new_status:
            return Response({'message': f'Travel request is already {new_status}.'},
                            status=status.HTTP_200_OK)

        # Update the status
        travel_request.status = new_status
        travel_request.save()

        # Log action (In a real-world app, this can be stored in an audit table)
        print(f"Admin {request.user.username} has {new_status} travel request ID {pk}")

        # Notify user (In a real-world app, this can trigger an email or push notification)
        # Example: send_email_notification(travel_request.user.email, new_status)

        return Response({'message': f'Travel request has been {new_status} successfully.'},
                        status=status.HTTP_200_OK)

