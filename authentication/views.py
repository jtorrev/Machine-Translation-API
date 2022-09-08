from django.shortcuts import render
# Create your views here.
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework.permissions import AllowAny
from django.contrib.auth import login as django_login, logout as django_logout
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.contrib.auth import authenticate
from django.db import transaction
from authentication.roles import ROLES
from authentication.models import MTUser, UserSerializer


@api_view(['POST'])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            if not user.is_active:
                return JsonResponse({
                    "status": "error",
                    "code": status.HTTP_404_NOT_FOUND,
                    "message": "User is deactivated",
                    "data": {}
                }, safe=False,
                    status=status.HTTP_404_NOT_FOUND)
            django_login(request=request, user=user)
            token, created = Token.objects.get_or_create(user=user)
            user_belongs_to = user.groups.values_list('name', flat=True)
            # If it is not ADMINISTRATOR
            # if 'ADMINISTRATOR' not in user_belongs_to:
            response = Response({
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "success",
                "data": {
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": list(user_belongs_to),
                    "token": token.key,
                },
                "token": "Token {}".format(token.key),
                "errorCode": 200
            }, status=status.HTTP_200_OK)
            return response
        else:
            return JsonResponse({
                "status": "error",
                "code": status.HTTP_401_UNAUTHORIZED,
                "message": "Unable to login with given credentials",
                "data": {}
            }, safe=False, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return JsonResponse({
            "status": "error",
            "code": status.HTTP_401_UNAUTHORIZED,
            "message": "You most provide a username and password",
            "data": {}
        }, safe=False, status=status.HTTP_401_UNAUTHORIZED)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def logout(request):
    user = request.user
    if user:
        try:
            # user.auth_token.delete()
            django_logout(request)
            return Response({
                "status": "success",
                "message": "Successfully logout",
                "code": status.HTTP_200_OK,
                "data": {}
            }, status=status.HTTP_200_OK)
        except Exception:
            return JsonResponse({
                "status": "error",
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "Something went wrong",
                "data": {}}, safe=False, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({
            "status": "error",
            "code": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid credentials were provided",
            "data": {}
        }, safe=False,
            status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def change_password(request):
    password = request.data.get("password")
    if password:
        user = request.user
        try:
            user.set_password(password)
            user.save()
            return JsonResponse({
                "status": "success",
                "message": "Password was successfully updated",
                "code": status.HTTP_200_OK,
                "data": {}
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": "Password was not changed",
                "code": status.HTTP_400_BAD_REQUEST,
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({
            "status": "error",
            "message": "Password mus be included",
            "code": status.HTTP_400_BAD_REQUEST,
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_users(request):
    user = request.user
    try:
        global_rol = user.groups.all()[0].name
        if global_rol == 'ADMINISTRATOR':
            objects = MTUser.objects.all().order_by('username')
            serialized_objects = UserSerializer(objects, many=True)
            return JsonResponse({
                "status": "success",
                "message": "",
                "code": status.HTTP_200_OK,
                "data": serialized_objects.data
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                "status": "error",
                "code": status.HTTP_401_UNAUTHORIZED,
                "message": "Unable to list users with given credentials",
                "data": {}
            }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": e,
            "code": status.HTTP_400_BAD_REQUEST,
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_user(request):
    user = request.user
    global_rol = user.groups.all()[0].name
    if user.is_superuser or global_rol == 'ADMINISTRATOR':
        email = request.data.get("email")
        username = request.data.get("username")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        password = request.data.get("password")
        is_admin = False  # request.data.get("admin")
        # role = request.data.get("role")
        if username and \
                password and \
                first_name and \
                last_name and \
                email:
            username_query_set = MTUser.objects.filter(Q(username=username) | Q(email=email))
            if not username_query_set:
                with transaction.atomic():
                    if is_admin is True:
                        s_user = MTUser.objects.create_superuser(username=username, email=email, password=password,
                                                                 first_name=first_name, last_name=last_name)
                        ROLES.set_role(s_user, "ADMINISTRATOR")
                    else:
                        s_user = MTUser.objects.create_user(username=username, email=email, password=password,
                                                            first_name=first_name, last_name=last_name)
                        ROLES.set_role(s_user, "USER")
                    serialized_user = UserSerializer(s_user, many=False)
                    return JsonResponse({
                        "status": "success",
                        "message": "",
                        "code": status.HTTP_200_OK,
                        "data": serialized_user.data
                    }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "The email and username fields have to be uniques",
                    "code": status.HTTP_400_BAD_REQUEST,
                    "data": {}
                }, status=status.HTTP_400_BAD_REQUEST)

        else:
            return JsonResponse({
                "status": "error",
                "message": "You most provide a valid user information",
                "code": status.HTTP_400_BAD_REQUEST,
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({
            "status": "error",
            "message": "This user has not permissions to performs this operation",
            "code": status.HTTP_400_BAD_REQUEST,
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_user(request):
    user = request.user
    try:
        target = request.data
        global_rol = user.groups.all()[0].name
        if global_rol == 'ADMINISTRATOR' or user.username == target['username']:
            user_instance = MTUser.objects.get(username=target['username'])
            if user_instance:
                # if target['role'] is not None:
                #     user_instance.groups.clear()
                #     ROLES.set_role(user_instance, target['role'])
                user_instance.first_name = target['first_name']
                user_instance.last_name = target['last_name']
                user_instance.set_password(target['password'])
                user_instance.email = target['email']
                user_instance.save()
                serialized_user = UserSerializer(user_instance, many=False)
                return JsonResponse({
                    "status": "success",
                    "message": "",
                    "code": status.HTTP_200_OK,
                    "data": serialized_user.data
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "An error occurred",
                    "code": status.HTTP_400_BAD_REQUEST,
                    "data": {}
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({
                "status": "error",
                "message": "You could not perform this operation",
                "code": status.HTTP_400_BAD_REQUEST,
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": e,
            "code": status.HTTP_400_BAD_REQUEST,
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def delete_user(request):
    try:
        user = request.user
        target = request.data
        global_rol = user.groups.all()[0].name
        if global_rol == 'ADMINISTRATOR' and user.username != target['username']:
            user_to_delete = MTUser.objects.get(username=target['username'])
            if not user_to_delete:
                return JsonResponse({
                    "status": "error",
                    "message": "The given username do not belongs to any user",
                    "code": status.HTTP_400_BAD_REQUEST,
                    "data": {}
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                user_to_delete.delete()
                return JsonResponse({
                    "status": "success",
                    "message": "",
                    "code": status.HTTP_200_OK,
                    "data": {}
                }, status=status.HTTP_200_OK)

        else:
            return JsonResponse({
                "status": "error",
                "message": "You could not perform this operation",
                "code": status.HTTP_400_BAD_REQUEST,
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": e,
            "code": status.HTTP_400_BAD_REQUEST,
            "data": {}
        }, status=status.HTTP_400_BAD_REQUEST)

#
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# @api_view(['GET'])
# def roles_view(request):
#     user = request.user
#     if user.is_superuser:
#         roles = list(ROLES.APP_ROLES.keys())
#         return JsonResponse({'roles': '{}'.format(roles)}, safe=False,
#                             status=status.HTTP_200_OK)
#     else:
#         msg = 'You could not perform this operation'
#         return JsonResponse({'error': '{}'.format(msg)}, safe=False,
#                             status=status.HTTP_400_BAD_REQUEST)
#
#
#
#
