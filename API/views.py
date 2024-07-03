# scanner/views.py
import PyPDF2
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from .serializers import CBCReportSerializer
from pdfreader import SimplePDFViewer, PageDoesNotExist
import os
import logging
from django.shortcuts import render

logger = logging.getLogger(__name__)

class CBCReportView(APIView):
    parser_classes = [MultiPartParser]

    def get(self, request, format=None):
        # Return the HTML template for GET requests
        return render(request, 'upload_info.html')

    def post(self, request, format=None):
        logger.info("Received request with data: %s", request.data)
        
        if 'file' not in request.FILES:
            logger.error("File not found in request")
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = request.FILES['file']
        logger.info("Received file: %s", file_obj.name)
        
        temp_dir = 'temp'
        
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        pdf_path = os.path.join(temp_dir, file_obj.name)
        
        with open(pdf_path, 'wb+') as temp_file:
            for chunk in file_obj.chunks():
                temp_file.write(chunk)
        
        if not os.path.exists(pdf_path):
            logger.error("File not found after upload")
            return Response({"error": "File not found after upload."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            text = self.extract_text_from_pdf(pdf_path)
            # print(text)
        except Exception as e:
            logger.error("Failed to process PDF: %s", str(e))
            return Response({"error": f"Failed to process PDF: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        attributes = self.parse_cbc_report(text)
        
        # serializer = CBCReportSerializer(data=attributes)
        # if serializer.is_valid():
        #     return Response(serializer.data, status=status.HTTP_200_OK)
        # logger.error("Serializer errors: %s", serializer.errors)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        logger.info("Parsed attributes: %s", attributes)
        print("PARSED ATTRIBUTES:****", attributes)
        return Response(attributes, status=status.HTTP_200_OK)

    def extract_text_from_pdf(self, pdf_path):
        with open(pdf_path, 'rb') as file:
        #     viewer = SimplePDFViewer(file)
        #     text = ""
        #     try:
        #         while True:
        #             viewer.render()
        #             text += viewer.canvas.text_content
        #             viewer.next()
        #     except PageDoesNotExist:
        #         pass

            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
        return text

    def parse_cbc_report(self, text):
        attribute_mapping = {
            'HB': ['HB', 'HEMOGLOBIN', 'Hemoglobin', 'Haemoglobin', 'HAEMOGLOBIN'],
            'HCT': ['HCT', 'HEMATOCRIT', 'Hematocrit', 'HAEMATOCRIT'],
            'RBC': ['RBC', 'RED BLOOD CELLS', 'Red Blood Cells', 'Red blood cells'],
            'MCV': ['MCV'],
            'MCH': ['MCH'],
            'MCHC': ['MCHC'],
            'WBC': ['WBC', 'WHITE BLOOD CELLS', 'White Blood Cells', 'White blood cells'],
            'PLATELETS': ['PLATELETS', 'PLATELET COUNT', 'Platelet Count', 'Platelet count'],
            'NEUTROPHILS%': ['NEUTROPHILS%', 'Neutrophils', 'NEUTROPHILS'],
            'LYMPHOCYTES%': ['LYMPHOCYTES%', 'Lymphocytes', 'LYMPHOCYTES'],
            'MONOCYTES%': ['MONOCYTES%', 'Monocytes', 'MONOCYTES'],
            'EOSINOPHILS%': ['EOSINOPHILS%', 'Eosinophils', 'EOSINOPHILS'],
            'BASOPHILS%': ['BASOPHILS%', 'Basophils', 'BASOPHILS'],
            'ESR': ['ESR']
        }

        attributes = {key: None for key in attribute_mapping}
        lines = text.split('\n')

        for line in lines:
            for key, synonyms in attribute_mapping.items():
                if any(synonym in line.upper() for synonym in synonyms):
                    # Extract the numeric value from the line
                    numeric_value = next((s for s in line.split() if s.replace('.', '', 1).replace(',', '', 1).isdigit()), None)
                    if numeric_value:
                        attributes[key] = numeric_value
                    break

        # Remove None values from attributes
        attributes = {k: v for k, v in attributes.items() if v is not None}

        return attributes

class PromptGeneratorView(APIView):
    parser_classes = [MultiPartParser]
    