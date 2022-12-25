import datetime
from django.shortcuts import redirect, render
import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from lmsApp import models, forms
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required

def context_data(request):
    fullpath = request.get_full_path()
    abs_uri = request.build_absolute_uri()
    abs_uri = abs_uri.split(fullpath)[0]
    context = {
        'system_host' : abs_uri,
        'page_name' : '',
        'page_title' : '',
        'system_name' : 'Perpustakaan',
        'topbar' : True,
        'footer' : True,
    }

    return context
    
def userregister(request):
    context = context_data(request)
    context['topbar'] = False
    context['footer'] = False
    context['page_title'] = "User Registration"
    if request.user.is_authenticated:
        return redirect("home-page")
    return render(request, 'register.html', context)

def save_register(request):
    resp={'status':'failed', 'msg':''}
    if not request.method == 'POST':
        resp['msg'] = "Tidak ada data yang dikirim pada permintaan ini"
    else:
        form = forms.SaveUser(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Akun Anda telah berhasil dibuat")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if resp['msg'] != '':
                        resp['msg'] += str('<br />')
                    resp['msg'] += str(f"[{field.name}] {error}.")
            
    return HttpResponse(json.dumps(resp), content_type="application/json")


def update_profile(request):
    context = context_data(request)
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id = request.user.id)
    if not request.method == 'POST':
        form = forms.UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = forms.UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil telah diperbarui")
            return redirect("profile-page")
        else:
            context['form'] = form
            
    return render(request, 'manage_profile.html',context)


def update_password(request):
    context =context_data(request)
    context['page_title'] = "Perbaharui Password"
    if request.method == 'POST':
        form = forms.UpdatePasswords(user = request.user, data= request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Kata Sandi Akun Anda telah berhasil diperbarui")
            update_session_auth_hash(request, form.user)
            return redirect("profile-page")
        else:
            context['form'] = form
    else:
        form = forms.UpdatePasswords(request.POST)
        context['form'] = form
    return render(request,'update_password.html',context)

# Create your views here.
def login_page(request):
    context = context_data(request)
    context['topbar'] = False
    context['footer'] = False
    context['page_name'] = 'login'
    context['page_title'] = 'Login'
    return render(request, 'login.html', context)

def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Username atau kata sandi salah"
        else:
            resp['msg'] = "Username atau kata sandi salah"
    return HttpResponse(json.dumps(resp),content_type='application/json')


def home(request):
    context = context_data(request)
    context['page'] = 'home'
    context['page_title'] = 'Home'
    context['categories'] = models.Category.objects.filter(delete_flag = 0, status = 1).all().count()
    context['sub_categories'] = models.SubCategory.objects.filter(delete_flag = 0, status = 1).all().count()
    context['students'] = models.Students.objects.filter(delete_flag = 0, status = 1).all().count()
    context['books'] = models.Students.objects.filter(delete_flag = 0, status = 1).all().count()
    context['pending'] = models.Borrow.objects.filter(status = 1).all().count()
    context['pending'] = models.Borrow.objects.filter(status = 1).all().count()
    context['transactions'] = models.Borrow.objects.all().count()

    return render(request, 'home.html', context)

def logout_user(request):
    logout(request)
    return redirect('login-page')
    

def profile(request):
    context = context_data(request)
    context['page'] = 'profile'
    context['page_title'] = "Profil"
    return render(request,'profile.html', context)


def users(request):
    context = context_data(request)
    context['page'] = 'users'
    context['page_title'] = "Petugas"
    context['users'] = User.objects.exclude(pk=request.user.pk).filter(is_superuser = False).all()
    return render(request, 'users.html', context)


def save_user(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            user = User.objects.get(id = post['id'])
            form = forms.UpdateUser(request.POST, instance=user)
        else:
            form = forms.SaveUser(request.POST) 

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Telah Berhasil di simpan.")
            else:
                messages.success(request, "Telah Berhasil Diperbaharui.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "Tidak ada data yang dikirim atas permintaant"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def manage_user(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_user'
    context['page_title'] = 'Manage User'
    if pk is None:
        context['user'] = {}
    else:
        context['user'] = User.objects.get(id=pk)
    
    return render(request, 'manage_user.html', context)


def delete_user(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'User ID Gagal'
    else:
        try:
            User.objects.filter(pk = pk).delete()
            messages.success(request, "Pengguna telah berhasil dihapus.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Gagal Menghapus"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def category(request):
    context = context_data(request)
    context['page'] = 'category'
    context['page_title'] = "Data Kategori"
    context['category'] = models.Category.objects.filter(delete_flag = 0).all()
    return render(request, 'category.html', context)


def save_category(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            category = models.Category.objects.get(id = post['id'])
            form = forms.SaveCategory(request.POST, instance=category)
        else:
            form = forms.SaveCategory(request.POST) 

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Kategori telah berhasil disimpan.")
            else:
                messages.success(request, "Kategori telah berhasil diperbarui.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "Tidak ada data yang dikirim atas permintaan"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def view_category(request, pk = None):
    context = context_data(request)
    context['page'] = 'view_category'
    context['page_title'] = 'View Category'
    if pk is None:
        context['category'] = {}
    else:
        context['category'] = models.Category.objects.get(id=pk)
    
    return render(request, 'view_category.html', context)


def manage_category(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_category'
    context['page_title'] = 'Manage Category'
    if pk is None:
        context['category'] = {}
    else:
        context['category'] = models.Category.objects.get(id=pk)
    
    return render(request, 'manage_category.html', context)


def delete_category(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'ID kategori tidak valid'
    else:
        try:
            models.Category.objects.filter(pk = pk).update(delete_flag = 1)
            messages.success(request, "Kategori telah berhasil dihapus.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Menghapus Kategori Gagal"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def sub_category(request):
    context = context_data(request)
    context['page'] = 'sub_category'
    context['page_title'] = "Genre"
    context['sub_category'] = models.SubCategory.objects.filter(delete_flag = 0).all()
    return render(request, 'sub_category.html', context)


def save_sub_category(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            sub_category = models.SubCategory.objects.get(id = post['id'])
            form = forms.SaveSubCategory(request.POST, instance=sub_category)
        else:
            form = forms.SaveSubCategory(request.POST) 

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Rekap Buku berhasil disimpan.")
            else:
                messages.success(request, "Rekap Buku telah berhasil diperbarui.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def view_sub_category(request, pk = None):
    context = context_data(request)
    context['page'] = "'view_sub_category'"
    context['page_title'] = 'View Sub Category'
    if pk is None:
        context['sub_category'] = {}
    else:
        context['sub_category'] = models.SubCategory.objects.get(id=pk)
    
    return render(request, 'view_sub_category.html', context)


def manage_sub_category(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_sub_category'
    context['page_title'] = "Genre"
    if pk is None:
        context['sub_category'] = {}
    else:
        context['sub_category'] = models.SubCategory.objects.get(id=pk)
    context['categories'] = models.Category.objects.filter(delete_flag = 0, status = 1).all()
    return render(request, 'manage_sub_category.html', context)


def delete_sub_category(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Gagal'
    else:
        try:
            models.SubCategory.objects.filter(pk = pk).update(delete_flag = 1)
            messages.success(request, "Kategori telah berhasil dihapus.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Menghapus genre Gagal"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def books(request):
    context = context_data(request)
    context['page'] = 'book'
    context['page_title'] = "Data Buku"
    context['books'] = models.Books.objects.filter(delete_flag = 0).all()
    return render(request, 'books.html', context)


def save_book(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            book = models.Books.objects.get(id = post['id'])
            form = forms.SaveBook(request.POST, instance=book)
        else:
            form = forms.SaveBook(request.POST) 

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Buku telah berhasil disimpan.")
            else:
                messages.success(request, "Buku telah berhasil diperbarui.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "Tidak ada data yang dikirim atas permintaan"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def view_book(request, pk = None):
    context = context_data(request)
    context['page'] = 'view_book'
    context['page_title'] = 'View Book'
    if pk is None:
        context['book'] = {}
    else:
        context['book'] = models.Books.objects.get(id=pk)
    
    return render(request, 'view_book.html', context)


def manage_book(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_book'
    context['page_title'] = 'Manage Book'
    if pk is None:
        context['book'] = {}
    else:
        context['book'] = models.Books.objects.get(id=pk)
    context['sub_categories'] = models.SubCategory.objects.filter(delete_flag = 0, status = 1).all()
    return render(request, 'manage_book.html', context)


def delete_book(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Book ID is invalid'
    else:
        try:
            models.Books.objects.filter(pk = pk).update(delete_flag = 1)
            messages.success(request, "Book has been deleted successfully.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Deleting Book Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def students(request):
    context = context_data(request)
    context['page'] = 'student'
    context['page_title'] = "Data Mahasiswa"
    context['students'] = models.Students.objects.filter(delete_flag = 0).all()
    return render(request, 'students.html', context)


def save_student(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            student = models.Students.objects.get(id = post['id'])
            form = forms.SaveStudent(request.POST, instance=student)
        else:
            form = forms.SaveStudent(request.POST) 

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Mahasiswa telah berhasil disimpan.")
            else:
                messages.success(request, "Mahasiswa telah berhasil diperbarui.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "Tidak ada data yang dikirim atas permintaan"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def view_student(request, pk = None):
    context = context_data(request)
    context['page'] = 'view_student'
    context['page_title'] = 'View Student'
    if pk is None:
        context['student'] = {}
    else:
        context['student'] = models.Students.objects.get(id=pk)
    
    return render(request, 'view_student.html', context)


def manage_student(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_student'
    context['page_title'] = 'Manage Student'
    if pk is None:
        context['student'] = {}
    else:
        context['student'] = models.Students.objects.get(id=pk)
    context['sub_categories'] = models.SubCategory.objects.filter(delete_flag = 0, status = 1).all()
    return render(request, 'manage_student.html', context)


def delete_student(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Student ID is invalid'
    else:
        try:
            models.Students.objects.filter(pk = pk).update(delete_flag = 1)
            messages.success(request, "Mahasiswa telah berhasil dihapus.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Gagal Menghapus Mahasiswa"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def borrows(request):
    context = context_data(request)
    context['page'] = 'borrow'
    context['page_title'] = "Daftar  Peminjaman"
    context['borrows'] = models.Borrow.objects.order_by('status').all()
    return render(request, 'borrows.html', context)


def save_borrow(request):
    resp = { 'status': 'failed', 'msg' : '' }
    if request.method == 'POST':
        post = request.POST
        if not post['id'] == '':
            borrow = models.Borrow.objects.get(id = post['id'])
            form = forms.SaveBorrow(request.POST, instance=borrow)
        else:
            form = forms.SaveBorrow(request.POST) 

        if form.is_valid():
            form.save()
            if post['id'] == '':
                messages.success(request, "Transaksi Peminjaman telah berhasil disimpan.")
            else:
                messages.success(request, "Transaksi Peminjaman telah berhasil diperbarui.")
            resp['status'] = 'success'
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br/>')
                    resp['msg'] += str(f'[{field.name}] {error}')
    else:
         resp['msg'] = "Tidak ada data yang dikirim atas permintaan"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def view_borrow(request, pk = None):
    context = context_data(request)
    context['page'] = 'view_borrow'
    context['page_title'] = 'View Transaction Details'
    if pk is None:
        context['borrow'] = {}
    else:
        context['borrow'] = models.Borrow.objects.get(id=pk)
    
    return render(request, 'view_borrow.html', context)


def manage_borrow(request, pk = None):
    context = context_data(request)
    context['page'] = 'manage_borrow'
    context['page_title'] = 'Manage Transaction Details'
    if pk is None:
        context['borrow'] = {}
    else:
        context['borrow'] = models.Borrow.objects.get(id=pk)
    context['students'] = models.Students.objects.filter(delete_flag = 0, status = 1).all()
    context['books'] = models.Books.objects.filter(delete_flag = 0, status = 1).all()
    return render(request, 'manage_borrow.html', context)


def delete_borrow(request, pk = None):
    resp = { 'status' : 'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Transaction ID is invalid'
    else:
        try:
            models.Borrow.objects.filter(pk = pk).delete()
            messages.success(request, "Transaksi berhasil dihapus.")
            resp['status'] = 'success'
        except:
            resp['msg'] = "Menghapus Transaksi Gagal"

    return HttpResponse(json.dumps(resp), content_type="application/json")
