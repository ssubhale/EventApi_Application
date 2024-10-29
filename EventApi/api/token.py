import jwt
from django.conf import settings
from rest_framework import status
from api.models import User


def check_user(user_id):
    user_obj = User.objects.filter(id=user_id).first()
    if user_obj:
        return user_obj.role
    else:
        return None


def extract_token(authorization_header):
    if not authorization_header:
        return None
    parts = authorization_header.split()

    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    return parts[1]

def auth_api_func(request):
    access_token = request.META.get('HTTP_AUTHORIZATION')
    token = extract_token(access_token)
    
    if not token:
        return False, status.HTTP_400_BAD_REQUEST
    
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
       
        user_role = check_user(decoded['user_id'])
        
        if user_role:
            return True, (status.HTTP_200_OK, user_role)
        else:
            return False, status.HTTP_401_UNAUTHORIZED
        
    
    except jwt.ExpiredSignatureError:
        return False, status.HTTP_401_UNAUTHORIZED
    
    except jwt.InvalidTokenError:
        return False, status.HTTP_401_UNAUTHORIZED
