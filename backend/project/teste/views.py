from django.shortcuts import render

from django.http import JsonResponse

def minha_view(request):
    return JsonResponse({"mensagem": "Olá do Django!"})