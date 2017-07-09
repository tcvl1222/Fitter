from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse, HttpResponseRedirect
from .models import Person, TopClothes, BottomClothes, ClothesNick
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory, BaseFormSet
import readAndSave
from .forms import PersonForm, TopClothesForm, BottomClothesForm
from .anticipate_size import int_find_good_data, guess_int_by_question


def index(request):
    # reverse 는 url 하드코딩 피할수 있도록 해줌
    return render(request, 'fitterKakao/index.html')


def size_list_to_dict(suggested_size):
    param_list = ['shoulder', 'chest', 'arm', 'waist',
                  'bottom_waist', 'crotch', 'thigh', 'length', 'hem', 'hip',
                  'crotch_height', 'middle_thigh', 'knee', 'calf', 'nipple']

    each_par_dict = {}
    for i, size in enumerate(suggested_size):
        each_par_dict[param_list[i]] = size
    return each_par_dict


@login_required
def suppose_size(request, kinds, tag_num):
    try:
        """개인의 데이터"""
        person = Person.objects.filter(name=request.user)
        # 나중에 이거 [0]하는 부분 바꿔야함!
        person_info_dict = person.values('sex', 'height', 'weight', 'shoulder_a', 'chest_a', 'sleeve_a', 'waist_a',
                                         'hip_a', 'crotch_a', 'length_a', 'thigh_a', 'hem_a')[0]  # queryset
        # 키는 1770 이런 형식으로 되어있으므로 10 곱해야함
        user_sex = person_info_dict['sex']
        user_height, user_weight = person_info_dict['height'] * 10, person_info_dict['weight']

        # ['shoulder', 'chest', 'arm', 'waist'
        # 'bottom_waist', 'crotch', 'thigh', 'length', 'hem', 'hip',
        # 'crotch_height', 'middle_thigh', 'knee', 'calf'] 순서
        question = []
        for answer in ['shoulder_a', 'chest_a', 'sleeve_a', 'waist_a',
                       'waist_a', 'crotch_a', 'thigh_a', 'length_a', 'hem_a', 'hip_a',
                       'length_a', 'thigh_a', '', '', 'chest_a']:
            if len(answer) == 0:
                question.append(1)
            else:
                question.append(person_info_dict[answer])

        # readAndSave 파일 없는거니까 조심 - 데이터도 나중에 DB로 넣는걸로 해보자
        # 데이터 파일 읽어오기
        file_path = os.path.join(settings.STATIC_ROOT, 'json/whole_hw_filtered_survey.json')
        hw_filtered_sizes = readAndSave.read_json(file_path, 'utf8')

        # 성별로 꺼내기
        shw_filtered_sizes = hw_filtered_sizes[str(user_sex)]
        # 괜찮은 사이즈를 찾고 글자 데이터를 숫자로 바꾸기
        hw_filtered_size_nums = int_find_good_data(user_height, user_weight, shw_filtered_sizes)

        # 몸 부위별로 모으기
        size_each_parameter = [[one_person[parameter]
                                for one_person in hw_filtered_size_nums]
                               for parameter in range(len(hw_filtered_size_nums[0]))]  # 변수개수만큼 돌리기

        """예상 사이즈 추천하고 실측 데이터로 바꾸기"""
        suggested_size = guess_int_by_question(question, size_each_parameter)
        suggested_size = size_list_to_dict(suggested_size)

        if kinds == 'top':
            clothes = TopClothes.objects.filter(pk=tag_num)  # POST 한 정보만 보게?(일단 그냥 하나만 보게 하자)

        elif kinds == 'bot':
            clothes = BottomClothes.objects.filter(pk=tag_num)  # POST 한 정보만 보게?(일단 그냥 하나만 보게 하자)

    except TopClothes.DoesNotExist or BottomClothes.DoesNotExist:
        raise Http404("Data does not exist")

    return render(request, 'fitterKakao/result.html', {'types' : kinds,
                                                       'clothes': clothes,
                                                       'person': person,
                                                       'suggest_size': suggested_size, })


@login_required
def check_data(request):
    try:
        person = Person.objects.get(name=request.user)
        return render(request, 'fitterKakao/update_p.html', {'person': person, })
    except Person.DoesNotExist:
        return redirect('fitterKakao:post_new')


@login_required
def post_new(request):
    if request.method == "POST": #이미 보낸거라면
        person_form = PersonForm(request.POST)
        if person_form.is_valid(): # 저장된 form 형식이 잘 맞는지
            person = person_form.save(commit=False) # False 바로 저장하지는 마
            person.name = request.user
            person.save()
            return redirect('fitterKakao:choose_clothes')
    else:
        person_form = PersonForm()

    return render(request, 'fitterKakao/post_new.html', {'person_form': person_form,})


@login_required
def post_edit(request, pk):
    existing_data = Person.objects.get(pk=pk)
    if request.method == "POST":  # 이미 보낸거라면
        person_form = PersonForm(request.POST, instance=existing_data)
        if person_form.is_valid(): # 저장된 form 형식이 잘 맞는지
            person = person_form.save(commit=False) # False 바로 저장하지는 마
            person.name = request.user
            person.save()
            return redirect('fitterKakao:choose_clothes')
    else:
        person_form = PersonForm(instance=existing_data)

    return render(request, 'fitterKakao/post_new.html', {'person_form': person_form, })


@login_required
def add_clothes(request, kinds):
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False
    top_clothes_formset = formset_factory(TopClothesForm, max_num=3,
                                     formset=RequiredFormSet)
    bottom_clothes_formset = formset_factory(TopClothesForm, max_num=3,
                                        formset=RequiredFormSet)

    if request.method == "POST":
        if kinds == 'top':
            clothes_form = TopClothesForm(request.POST)
            clothes_formset = top_clothes_formset(request.POST)

        elif kinds == 'bot':
            clothes_form = BottomClothesForm(request.POST)
            clothes_formset = bottom_clothes_formset(request.POST)

        if clothes_form.is_valid() and clothes_formset.is_valid():
            # 하나라면
            clothes = clothes_form.save(commit=False)
            clothes.name = request.user
            clothes.nick = request.POST['clothes_name']
            clothes.save()
            #ClothesNick.objects.create(nick=request.POST['clothes_name'])
            for form in clothes_formset.forms:
                clothes = form.save(commit=False)
                print(clothes)
                clothes.name = request.user
                clothes.save()

            return redirect('fitterKakao:choose_clothes')
    else:
        if kinds == 'top':
            clothes_form = TopClothesForm()
            clothes_formset = top_clothes_formset()
        elif kinds == 'bot':
            clothes_form = BottomClothesForm()
            clothes_formset = top_clothes_formset()

    return render(request, 'fitterKakao/add_clothes.html', {'clothes_form': clothes_form,
                                                            'clothes_formset': clothes_formset, })


@login_required
def choose_clothes(request):
    top_clothes = TopClothes.objects.filter(name=request.user)
    bottom_clothes = BottomClothes.objects.filter(name=request.user)

    return render(request, 'fitterKakao/clothes.html', {'top_clothes': top_clothes,
                                                        'bottom_clothes': bottom_clothes, })



