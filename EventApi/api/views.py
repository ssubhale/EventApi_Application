from django.shortcuts import render
from django.http import JsonResponse
from api.models import Event, Ticket
from rest_framework import status as http_status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from api.serializers import SignUpSerializer, UserSerializer, AllEventSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from api.token import auth_api_func


@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def signup_user(request):
    """
    API view to handle user signup.

    This view accepts user registration data, validates it using the
    SignUpSerializer, and creates a new user if the data is valid.
    """
    try:
        # Initialize the SignUpSerializer with the request data
        serializer = SignUpSerializer(data=request.data)

        # Validate the provided data
        if not serializer.is_valid():
            # Print errors for debugging if validation fails
            print("serializer.errors : ", serializer.errors)

        # Proceed if the data is valid
        if serializer.is_valid():
            # Save the new user to the database
            serializer.save()
            # Return success message upon successful registration
            return JsonResponse({'msg': 'success'}, status=http_status.HTTP_200_OK)
        
        # If validation fails, return error details
        return JsonResponse({'msg': 'failed', 'error': serializer.errors}, status=http_status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Handle exceptions that may occur during the signup process
        return JsonResponse({'error': str(e)}, status=http_status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def sign_in_user(request):
    """
    API view to authenticate a user and return JWT tokens.

    This view checks the provided credentials (email and password),
    authenticates the user, and generates access and refresh tokens if valid.
    """
    try:
        # Retrieve the email and password from the request data
        email = request.data.get('username')
        password = request.data.get('password')

        # Authenticate the user using the provided credentials
        user = authenticate(request, email=email, password=password)
        
        # Check if the user is successfully authenticated
        if user is not None:
            # Log in the user
            login(request, user)

            # Generate refresh and access tokens for the authenticated user
            refresh = RefreshToken.for_user(user)

            # Serialize user data to include in the response
            user_data = UserSerializer(user).data

            # Return the user data along with access and refresh tokens
            return JsonResponse({
                'user': user_data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),  # This provides the refresh token
            }, status=http_status.HTTP_200_OK)
        else:
            # If authentication fails, return an error message
            return JsonResponse({'error': 'Invalid Credentials'}, status=http_status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        # handle exception during Authentication
        return JsonResponse({'error': f"{e}"}, status=http_status.HTTP_404_NOT_FOUND)
    


@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def create_event(request):
    """
    API view to create a new event.

    This view checks the user's authentication status, verifies their role,
    and creates a new event entry in the database if the user has the proper permissions.
    """
    # Check if the user is authenticated using a custom authentication function
    is_authenticated, auth_response = auth_api_func(request)
    
    # If the user is not authenticated, return an appropriate error response
    if not is_authenticated:
        auth_status = auth_response
        if auth_status == http_status.HTTP_401_UNAUTHORIZED:
            return JsonResponse({"errors": "Unauthenticated or token expired"}, status=auth_status)
        return JsonResponse({"errors": "Authentication token not found"}, status=auth_status)

    # Extract the user's role from the authentication response
    user_role = auth_response[1]
    print("user_role : ", user_role)

    # Check if the user has admin permissions
    if user_role != 'Admin':
        return JsonResponse({'error': 'Permissions not allowed'}, status=http_status.HTTP_403_FORBIDDEN)

    try:
        # Get event details from the request data
        name = request.data.get('event_name')
        date = request.data.get('event_date')
        total_tickets = request.data.get('total_tickets')

        # Create a new Event object and save it to the database
        event = Event(
            name=name,
            date=date,
            total_tickets=total_tickets
        )
        event.save()

        # Return a success response
        return JsonResponse({'msg': 'Event created successfully'}, status=http_status.HTTP_201_CREATED)

    except Exception as e:
        # Handle any exceptions that occur during event creation
        return JsonResponse({'error': str(e)}, status=http_status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def get_events(request):
    """
    API view to retrieve all events from the database.

    This view checks the user's authentication status, retrieves all
    events, serializes them, and returns the event data in JSON format.
    """
    # Check if the user is authenticated using a custom authentication function
    is_authenticated, auth_response = auth_api_func(request)

    # If the user is not authenticated, return an appropriate error response
    if not is_authenticated:
        auth_status = auth_response
        if auth_status == http_status.HTTP_401_UNAUTHORIZED:
            return JsonResponse({"errors": "Unauthenticated or token expired"}, status=auth_status)
        else:
            return JsonResponse({"errors": "Authentication token not found"}, status=auth_status)

    try:
        # Retrieve all event objects from the database
        events = Event.objects.all()
        
        # Serialize the events using AllEventSerializer
        serializer = AllEventSerializer(events, many=True, context={'request': request})
        
        # Return the serialized event data in JSON format
        return JsonResponse({'events': serializer.data}, status=http_status.HTTP_200_OK)

    except Exception as e:
        # Handle any exceptions that occur during the event retrieval or serialization
        return JsonResponse({'errors': str(e)}, status=http_status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@csrf_exempt
@permission_classes([IsAuthenticated])
def purchase_tickets(request,id):
    """
    API view to handle ticket purchases for a specific event.

    This view checks the quantity requested against available tickets,
    updates the event's ticket sold count, and creates a Ticket entry
    in the database if the purchase is valid.
    """
    # Authentication and authorization logic
    is_authenticated, auth_response = auth_api_func(request)
    
    # Check if the user is authenticated
    if not is_authenticated:
        auth_status = auth_response
        if auth_status == http_status.HTTP_401_UNAUTHORIZED:
            return JsonResponse({"errors": "Unauthenticated or token expired"}, status=auth_status)
        else:
            return JsonResponse({"errors": "Authentication token not found"}, status=auth_status)

    # Extract user role from the authentication response
    user_role = auth_response[1]

    # Check if the user has the necessary role to purchase tickets
    if user_role != 'User':
        return JsonResponse({'error': 'Permissions not allowed'}, status=http_status.HTTP_400_BAD_REQUEST)
    
    try:
        # Extract the quantity of tickets to purchase from the request data
        quantity = request.data.get('quantity')
        if not quantity or quantity <= 0:
            return JsonResponse({'error': 'Invalid quantity'}, status=http_status.HTTP_400_BAD_REQUEST)

        # Fetch the event object by ID
        event = Event.objects.filter(id=id).first()
        if not event:
            return JsonResponse({'error': 'Event not found'}, status=http_status.HTTP_404_NOT_FOUND)

        # Check if there are enough available tickets
        if event.ticket_sold + quantity > event.total_tickets:
            available_tickets = event.total_tickets - event.ticket_sold
            return JsonResponse({'error': 'Not enough tickets available','comment': f'Only {available_tickets} tickets available' }, status=http_status.HTTP_400_BAD_REQUEST)

        # Create a new Ticket entry in the database
        ticket = Ticket.objects.create(
            user=request.user,
            event=event,
            quantity=quantity
        )

        # Update ticket_sold in Event
        event.ticket_sold += quantity
        event.save()

        # return appropriate response to the user
        return JsonResponse({'msg': 'success','comment': f'Successfully purchased {quantity} tickets'}, status=http_status.HTTP_200_OK)

    except Exception as e:
        # Handle any exceptions that occur during the process
        return JsonResponse({'error': f"{e}"}, status=http_status.HTTP_400_BAD_REQUEST)

