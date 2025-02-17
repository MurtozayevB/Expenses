from random import randint

from django.core.cache import cache
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView, UpdateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.status import HTTP_403_FORBIDDEN
from rest_framework.views import APIView

from .models import Expense, Category, User
from .serializers import RegisterSerializer, ExpensesCategorySerializer, CategorySerializer, ForgotPasswordSerializer, \
    ForgotPasswordCheckSerializer, PasswordResetSerializer, RegisterCheckSerializer
from .tasks import send_email


@extend_schema(tags=['auth'], request=PasswordResetSerializer)
class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": 200, "message": "Parol yangilandi!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['auth'], request=ForgotPasswordSerializer)
class ForgotPasswordAPIView(APIView):
    def post(self, request):
        data = request.data
        s = ForgotPasswordSerializer(data=data)
        if s.is_valid():
            email = s.validated_data.get('email')
            code = randint(10000, 99999)
            print(code)
            send_email.delay(to_send=email, code=code)
            response = JsonResponse({"status": 200, "message": "Code send to your email!", "email": email}, status=HTTP_200_OK)
            cache.set(email, code, timeout=300)
            return response
        return JsonResponse(s.errors, status=HTTP_400_BAD_REQUEST)


@extend_schema(tags=['auth'], request=ForgotPasswordCheckSerializer)
class ForgotPasswordCheckAPIView(APIView):
    def post(self, request):
        data = request.data.copy()
        email = data.get('email')
        verify_code = cache.get(email)
        if not verify_code:
            return JsonResponse({"error": "Code expired!"}, status=HTTP_400_BAD_REQUEST)
        data['verify_code'] = verify_code
        s = ForgotPasswordCheckSerializer(data=data)
        if s.is_valid():
            return JsonResponse({"status": 200, "message": "Correct code!", "email": email}, status=HTTP_200_OK)
        return JsonResponse(s.errors, status=HTTP_400_BAD_REQUEST)


@extend_schema(tags=['auth'], request=RegisterSerializer)
class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        user = User.objects.filter(email=request.data.get("email")).first()
        if serializer.is_valid() or (user and not user.is_active):
            if not user:
                u = serializer.save()
                u.is_active = False
                u.save()
            random_code = randint(10000, 99999)
            email = request.data.get("email")
            send_email.delay(email, random_code)
            response = JsonResponse({
                "status": 200,
                "message": "Tasdiqlash kodi jo'natildi!",
                "data": None
            }, status=HTTP_200_OK)
            cache.set(email, str(random_code), timeout=300)
            return response
        elif user and user.is_active:
            return JsonResponse({"status": 400, "message": "Email oldin ro'yxatdan o'tgan !"}, status=HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@extend_schema(tags=['auth'], request=RegisterCheckSerializer)
class RegisterCheckAPIView(APIView):
    def post(self, request):
        data = request.data.copy()
        verify_code = cache.get(data.get('email'))
        print(verify_code)
        print(data.get('code'))
        if not verify_code:
            return JsonResponse({"error": "Code expired!"}, status=HTTP_400_BAD_REQUEST)
        data['verify_code'] = verify_code
        s = RegisterCheckSerializer(data=data)
        if s.is_valid():
            User.objects.filter(email=data.get('email')).update(is_active=True)
            return JsonResponse({"status": 200, "message": "Registered!"}, status=HTTP_200_OK)
        return JsonResponse(s.errors, status=HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Expenses'], request=ExpensesCategorySerializer)
class ExpenseCreateApiView(CreateAPIView):
    serializer_class = ExpensesCategorySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exeption=True)
        instance = serializer.save(user=request.user)
        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

@extend_schema(tags=['Expenses'], responses=ExpensesCategorySerializer)
class ExpenseDeleteApiView(DestroyAPIView):
    serializer_class = ExpensesCategorySerializer
    lookup_field = 'pk'
    queryset = Expense.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['delete']

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        if instance.user !=user:
            return Response({"detail":"You do not have permission to delete this expense"}, status=HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        self.perform_destroy(instance)
        return Response(serializer.data, status=HTTP_200_OK)

@extend_schema(tags=['Expenses'], responses=ExpensesCategorySerializer)
class ExpenseUpdateApiView(UpdateAPIView):
    serializer_class = ExpensesCategorySerializer
    lookup_field = 'pk'
    queryset = Expense.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['put','patch']

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial',False)
        user = self.request.user
        instance =self.get_object()
        if instance.user !=user:
            return Response({"detail": "You do not have permission to delete this expense"},
                            status=HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exeption=True)
        self.perform_update(serializer)
        return Response(self.get_serializer(instance).data , status=HTTP_200_OK)

@extend_schema(tags=['Expenses'])
class ExpenseDetailApiView(RetrieveAPIView):
    serializer_class = ExpensesCategorySerializer
    lookup_field = 'pk'
    queryset = Expense.objects.all()
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()

        if instance.user !=user:
            return Response({'detail':"You do not have permission to view this expenses"}, status=HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)



@extend_schema(tags=['Expenses'], responses=ExpensesCategorySerializer)
class ExpenseListApiView(ListAPIView):
    serializer_class = ExpensesCategorySerializer
    queryset = Expense.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']


    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response = {
            "status": 200,
            "expenses": serializer.data
        }

        return Response(response)

@extend_schema(tags=['Expenses'])
class BalanceApiView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        amounts = Expense.objects.filter(user=self.request.user)
        total = sum(amounts.values_list('amount', flat=True))
        income_sum = sum(amounts.filter(type='income').values_list('amount',flat=True))
        expense_sum = sum(amounts.filter(type='expense').values_list('amount',flat=True))

        response = {
            "status": 200,
            'total':total,
            'income':income_sum,
            'expense':expense_sum
        }
        return Response(response, status=HTTP_200_OK)

@extend_schema(tags=['Category'], responses=CategorySerializer)
class CategoryTypeListApiView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    http_method_names = ['get']
    lookup_field = 'type'

    def get_queryset(self):
        type = self.kwargs['type']
        return Category.objects.filter(type=type)



# ===================================ADMIN==============
@extend_schema(tags=['Admin'], responses=CategorySerializer)
class CategoryListApiView(ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()



@extend_schema(tags=['Admin'], responses=CategorySerializer)
class CategoryUpdateApiView(UpdateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    lookup_field = 'pk'


@extend_schema(tags=['Admin'], responses=CategorySerializer)
class CategoryDeleteApiView(DestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    lookup_field = 'pk'



