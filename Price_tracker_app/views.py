import ast
from datetime import datetime
import re
import time
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.contrib import messages

from Price_tracker_app.amazon_traker import AmazonAPI
from Price_tracker_app.form import login_form, FeedbackForm
from Price_tracker_app.models import Product, Report

def home(request):
    return render(request, 'home.html')

def results(request):
    if request.method == 'POST':
        name = request.POST.get('productName', False)
        filter = request.POST.get('filter', False)
        number = request.POST.get('number',  False)
        if filter:
            filter = re.findall(r'[0-9]+', filter)
        else:
            filter = ['0','0']
        base_url = 'https://www.amazon.es/'
        currency = '€'
        amazon = AmazonAPI(name, filter, base_url, currency, int(number))
        data = amazon.run()
        if str(request.user) != 'AnonymousUser':
            save_data(name, data, request.user)
        print('all ok')
        return render(request, 'results.html', {'data':data})
    return render(request, 'home.html')


def save_data(name, data, user):
    title = name + " " + str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    report = Report.objects.create(title = title, user = user)
    report.save()
    for d in data:
        product = Product.objects.create(data = str(d), report = report)
        product.save()


def login_view(request):    
    if request.method == 'POST':
        form = login_form(request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['username'], password = request.POST['password'])            
            if user is not None:
                login(request, user)
                return home(request)
    else:
        form = login_form()
    return render(request, 'login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username = user.username, password = raw_password)
            if user is not None:
                login(request, user)
                return render(request, 'home.html')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return home(request)


def history(request):
    report_list = Report.objects.filter(user = request.user)
    if request.method == 'POST' and request.POST.get('report_name'):
        product_list = Product.objects.filter(report = request.POST.get('report_name', False))
        print(product_list)
        data = []
        for p in product_list:
            data.append(ast.literal_eval(p.data))
        print(data)
        return render(request, "results.html", {"data": data})
    elif request.method == 'POST':
        print("deleting")
        product_list = Report.objects.filter(id = request.POST.get('delete', False)).delete()
    return render(request, 'history.html', {'report_list': report_list})


def feedback(request):
    if request.method == 'POST':
        f = FeedbackForm(request.POST)
        if f.is_valid():
            f.save()
            messages.add_message(request, messages.INFO, 'Feedback Submitted.')
            return render(request, 'feedback.html', {'form': f})
    else:
        f = FeedbackForm()
    return render(request, 'feedback.html', {'form': f})