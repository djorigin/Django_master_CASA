from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response


def home(request):
    return render(request, "core/index.html")


@api_view(["GET"])
def client_greeting(request):
    return Response({"message": "Hello from Django API!"})


# Create your views here.
