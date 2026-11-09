from flight_info.serializer import HavaalanlariSerializer, UcuslarSerializer, UserSerializer
from flight_info.models import Havaalanlari, Ucuslar, Customer
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.dateparse import parse_date
from decimal import Decimal, InvalidOperation

# Create your views here.

class Register(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = Customer.objects.filter(email=email).first()
        if user is None:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_404_NOT_FOUND
            )
        if not user.check_password(password):
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_404_NOT_FOUND
            )
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )
    
class HavaalaniViewset(viewsets.ModelViewSet):
    serializer_class = HavaalanlariSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = []
        return super().get_permissions()

    def get_queryset(self):
        queryset = Havaalanlari.objects.all()
        code = self.request.GET.get('code')
        if code: 
            queryset = queryset.filter(code__icontains=code)
        return queryset

class UcuslarViewset(viewsets.ModelViewSet):
    """Flights. Anyone can search; creating, editing and deleting need a JWT.

    Search filters (all optional, combinable):
      ?from=IST          departure airport code
      ?to=ESB            arrival airport code
      ?date=2026-12-01   departure date
      ?max_price=500     upper price limit
    Results are ordered by departure time.
    """
    serializer_class = UcuslarSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = []
        return super().get_permissions()

    def get_queryset(self):
        queryset = Ucuslar.objects.select_related('kalkis_havaalani', 'varis_havaalani').order_by('kalkis_zamani')
        params = self.request.query_params
        if params.get('from'):
            queryset = queryset.filter(kalkis_havaalani__code__iexact=params['from'])
        if params.get('to'):
            queryset = queryset.filter(varis_havaalani__code__iexact=params['to'])
        if params.get('date'):
            day = parse_date(params['date'])
            if day is None:
                raise ValidationError({'date': 'Use the YYYY-MM-DD format.'})
            queryset = queryset.filter(kalkis_zamani__date=day)
        if params.get('max_price'):
            try:
                queryset = queryset.filter(fiyat__lte=Decimal(params['max_price']))
            except InvalidOperation:
                raise ValidationError({'max_price': 'Must be a number.'})
        return queryset
