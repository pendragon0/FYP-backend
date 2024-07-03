# scanner/serializers.py
from rest_framework import serializers

class CBCReportSerializer(serializers.Serializer):
    HB = serializers.CharField(max_length=50)
    RBC = serializers.CharField(max_length=50)
    HCT = serializers.CharField(max_length=50)
    MCV = serializers.CharField(max_length=50)
    MCH = serializers.CharField(max_length=50)
    MCHC = serializers.CharField(max_length=50)
    WBC = serializers.CharField(max_length=50)
    PLATELETS = serializers.CharField(max_length=50)
    NEUTROPHILS = serializers.CharField(max_length=50)
    LYMPHOCYTES = serializers.CharField(max_length=50)
    MONOCYTES = serializers.CharField(max_length=50)
    EOSINOPHILS = serializers.CharField(max_length=50)
    BASOPHILS = serializers.CharField(max_length=50)
    ESR = serializers.CharField(max_length=50)
