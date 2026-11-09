from rest_framework import serializers
from flight_info.models import Customer, Havaalanlari, Ucuslar

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'phone']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}
        
    def create(self, validated_data):
        user = Customer.objects.create_user(**validated_data)
        return user

class HavaalanlariSerializer(serializers.ModelSerializer):
    class Meta:
        model = Havaalanlari
        fields = ['id', 'sehir', 'code']  # Added code field

class UcuslarSerializer(serializers.ModelSerializer):
    kalkis_havaalani = serializers.SlugRelatedField(
        queryset=Havaalanlari.objects.all(),
        slug_field='code'
    )
    varis_havaalani = serializers.SlugRelatedField(
        queryset=Havaalanlari.objects.all(),
        slug_field='code'
    )
    
    class Meta: 
        model = Ucuslar
        fields = ['id', 'kalkis_havaalani', 'varis_havaalani', 'kalkis_zamani', 'inis_zamani', 'fiyat']
    
    def validate(self, data):
        # On partial updates, fall back to the stored values for fields that were not sent.
        get = lambda field: data.get(field, getattr(self.instance, field, None))
        if get('kalkis_havaalani') is not None and get('kalkis_havaalani') == get('varis_havaalani'):
            raise serializers.ValidationError("Departure and arrival airports must be different.")
        if get('kalkis_zamani') and get('inis_zamani') and get('inis_zamani') <= get('kalkis_zamani'):
            raise serializers.ValidationError("Arrival time must be after departure time.")
        return data
