from rest_framework import serializers
from .models import User, Event

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # Specify the model that this serializer is associated with
        fields = ['email', 'password', 'role']  # Define the fields to include in the serializer
        extra_kwargs = {
            'password': {'write_only': True}  # Ensure that the password is write-only for security
        }

    def create(self, validated_data):
        """
        Create a new user instance using the validated data.
        The username is set to the user's email for consistency.
        """
        validated_data['username'] = validated_data['email']  # Set username to email for consistency
        
        # Create a new user with the provided data
        user = User.objects.create_user(
            username=validated_data['username'],  # Set username
            email=validated_data['email'],  # Set email
            password=validated_data['password'],  # Set password
            role=validated_data['role']  # Set user role (e.g., Admin, User)
        )
                
        user.save()  # Save the new user instance to the database
        return user  # Return the created user instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # Specify the model for serialization
        fields = ['id', 'username', 'email', 'role']  # Define fields to include in the serialized data


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event  # Specify the Event model for serialization
        fields = ['id', 'name', 'date', 'total_tickets', 'ticket_sold']  # Define fields for the Event
        read_only_fields = ['id', 'date', 'ticket_sold']  # Set certain fields as read-only

    def create(self, validated_data):
        """
        Create a new event instance using the validated data.
        """
        # Create a new Event instance with the provided data
        event = Event(
            name=validated_data['name'],  # Set the event name
            total_tickets=validated_data['total_tickets']  # Set the total number of tickets
        )
        event.save()  # Save the new event instance to the database
        return event  # Return the created event instance


class AllEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event  # Specify the Event model for serialization
        fields = ['id', 'name', 'date', 'total_tickets', 'ticket_sold']  # Define fields to include in the serialized data
