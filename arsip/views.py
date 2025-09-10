from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

import arsip
from arsip.models import Arsip


# Create your views here.

def is_admin(user):
    return user.is_staff

@login_required(login_url="/login/")
def arsip_list(request):
    query_date = request.GET.get('nota_date')
    queryset = Arsip.objects.all().order_by('-nota_date')

    search_name = request.GET.get('search_name')
    search_date = request.GET.get('nota_date')

    if search_name:
        queryset = queryset.filter(Q(nota_cust_name__icontains=search_name))

    if search_date:
        queryset = queryset.filter(nota_date=search_date)

    paginator = Paginator(queryset, 3)
    page_num = request.GET.get('page', 1)
    arsip_page = paginator.get_page(page_num)

    #this is to preserve filter for pagination links
    params = request.GET.copy()
    params.pop('page', None)
    querystring = params.urlencode()

    context = {
        'arsip_page': arsip_page,
        'search_name': search_name,
        'search_date': search_date,
        'querystring': querystring
    }

    return render(request, 'arsip/arsip_main.html', context)

@login_required(login_url="/login/")
def create_arsip_view(request):
    if request.method == 'POST':
        data = request.POST
        upload_date = data.get('upload_date')
        # nota_previous_id = data.get('nota_previous_id') buat baru jd no need
        nota_receipt_id = data.get('nota_receipt_id') # nomor struk / faktur
        nota_customer_name = data.get('nota_customer_name')
        nota_date = data.get('nota_date')
        nota_image = request.FILES.get('nota_image')
        nota_notes = data.get('nota_notes')
        # ganti_nota = data.get('ganti_nota') no need

        Arsip.objects.create(
            userUploader_id=request.user.id,
            nota_receipt_id=nota_receipt_id,
            nota_cust_name=nota_customer_name,
            nota_date=nota_date,
            nota_image_file=nota_image,
            nota_notes=nota_notes,
        )
    return render(request, 'arsip/create_arsip.html', { 'arsip': arsip})

def arsip_detail(request, id):
    arsip = Arsip.objects.get(id=id)
    return render(request, 'arsip/arsip_detail.html', {'arsip': arsip})