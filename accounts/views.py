from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import JsonResponse

def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already taken"}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already registered"}, status=400)
        if password != confirm_password:
            return JsonResponse({"error": "Passwords do not match"}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = full_name
        user.save()
        login(request, user)  # Auto-login after registration
        return redirect("chat")

    return render(request, "register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("chat")
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=400)
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('/login?session_expired=1')
