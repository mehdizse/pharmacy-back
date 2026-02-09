from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden


def custom_404(request, exception):
    """Page 404 personnalisée"""
    return render(request, 'errors/404.html', status=404)


def custom_500(request):
    """Page 500 personnalisée"""
    return render(request, 'errors/500.html', status=500)


def custom_403(request, exception):
    """Page 403 personnalisée"""
    return render(request, 'errors/403.html', status=403)
