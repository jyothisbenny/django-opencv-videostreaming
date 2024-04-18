from rest_framework import serializers
from .models import User, Video, Machine, ProductionLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class VideoSerializer(serializers.ModelSerializer):
    owner_data = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Video
        fields = '__all__'
        extra_kwargs = {'name': {'required': True}, 'url': {'required': True}}

    def validate(self, data):
        user = self.context.get('request').user
        data['owner'] = user
        if self.instance and self.instance.owner != user:
            raise serializers.ValidationError({'detail': 'You are not allowed to do this action!'})
        return data

    @staticmethod
    def get_owner_data(obj):
        return UserSerializer(obj.owner).data if obj.owner else None


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = '__all__'
        extra_kwargs = {'machine_name': {'required': True}, 'machine_serial_no': {'required': True}}


class ProductionLogSerializer(serializers.ModelSerializer):
    oee = serializers.SerializerMethodField(required=False)

    class Meta:
        model = ProductionLog
        fields = '__all__'
        extra_kwargs = {'machine': {'required': True}, 'cycle_no': {'write_only': True}, 'cycle_no': {'write_only': True}}

    @staticmethod
    def get_oee(obj):

        return 0
