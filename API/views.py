# scanner/views.py
import PyPDF2
import cv2
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from .serializers import CBCReportSerializer
from pdfreader import SimplePDFViewer, PageDoesNotExist
import os
import logging
from django.shortcuts import render
from .models import UserReport
from django.contrib.auth.models import User
from .forms import UploadFileForm
from django.http import JsonResponse
import pytesseract
from PIL import Image
logger = logging.getLogger(__name__)

class CBCReportView(APIView):
    parser_classes = [MultiPartParser]

    def get(self, request, format=None):
        # Return the HTML template for GET requests
        return render(request, 'upload_info.html')

    def post(self, request, format=None):
        print('STARTED')
        logger.info("Received request with data: %s", request.data)
        
        if 'file' not in request.FILES or 'email' not in request.data:
            print("File or email not found in request")
            return Response({"error": "No file or email provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = request.FILES['file']
        # username = request.data['username']
        email = request.data['email']
        
        user_report = UserReport(email= email, file=file_obj)
        user_report.save()
        print('USER REPORT UPDATED FILE AND USER************')
        file_type = file_obj.content_type
        file_extension = os.path.splitext(file_obj.name)[1].lower()
        print(file_extension)
        if file_type == 'application/pdf' or file_extension == '.pdf':
            pdf_path = user_report.file.path
            try:
                text = self.extract_text_from_pdf(pdf_path)
            except Exception as e:
                return Response({"error": f"Failed to process PDF: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        elif file_type in ['image/jpeg', 'image/png'] or file_extension in ['.jpg', '.jpeg', '.png']:
            image_path = user_report.file.path
            try:
                text = self.extract_text_from_image(image_path)
            except Exception as e:
                return Response({"error": f"Failed to process image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)

        # pdf_path = user_report.file.path
        try:
            text = self.extract_text_from_pdf(pdf_path)
            # user_report.text = text
            # user_report.save()
            # print('USER REPORT UPDATED TEXT************')
        except Exception as e:
            return Response({"error": f"Failed to process PDF: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        
        # logger.info("Received file: %s", file_obj.name)
        
        # temp_dir = 'temp'
        
        # if not os.path.exists(temp_dir):
        #     os.makedirs(temp_dir)
        

        # pdf_path = os.path.join(temp_dir, file_obj.name)
        
        # with open(pdf_path, 'wb+') as temp_file:
        #     for chunk in file_obj.chunks():
        #         temp_file.write(chunk)
        
        # if not os.path.exists(pdf_path):
        #     logger.error("File not found after upload")
        #     return Response({"error": "File not found after upload."}, status=status.HTTP_400_BAD_REQUEST)

        # try:
        #     text = self.extract_text_from_pdf(pdf_path)
        #     # print(text)
        # except Exception as e:
        #     logger.error("Failed to process PDF: %s", str(e))
        #     return Response({"error": f"Failed to process PDF: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
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
        print('opening file....')
        with open(pdf_path, 'rb') as file:
            print('file opened----')
            
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

    def preprocess_image(self, image):
        image = cv2.imread(image, cv2.IMREAD_GRAYSCALE)

        #Apply thresholding
        _, image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        image = cv2.medianBlur(image, 3)

        return image
    
    def extract_text_from_image(self, image):
        #preprocessing the image
        final_image = self.preprocess_image(image)

        #convert image to a format compatible with PIL 
        pil_image = Image.fromarray(final_image)

        #using tesseract
        text = pytesseract.image_to_string(pil_image)

        return text

    def parse_cbc_report(self, text):
        attribute_mapping = {
            'HB': ['HB', 'HEMOGLOBIN', 'Hemoglobin', 'Haemoglobin', 'HAEMOGLOBIN'],
            'HCT': ['HCT', 'HEMATOCRIT', 'Hematocrit', 'HAEMATOCRIT'],
            'RBC': ['RBC', 'RED BLOOD CELLS', 'Red Blood Cells', 'Red blood cells','Red Cell Count'],
            'MCV': ['MCV','M.C.V', 'M.CV', 'MC.V'],
            'MCH': ['MCH','M.CH', 'MC.H','M.C.H'],
            'MCHC': ['MCHC','M.CH.C', 'MC.H.C','M.C.H.C','M.C.HC','MC.HC'],
            'WBC': ['WBC', 'WHITE BLOOD CELLS', 'White Blood Cells', 'White blood cells'],
            'PLATELETS': ['PLATELETS', 'PLATELET COUNT', 'Platelet Count', 'Platelet count', 'Platelets'],
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

class UserReportView(APIView):
    def get(self, request, email, format=None):
        # try:
        #     # file = request.FILES['files']
        #     # user = User.objects.get(username=username)
        #     email = User.objects.get(email = email)

        # except User.DoesNotExist:
        #     return Response({"error": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        print(f'EMAIL---- {email}')
        reports = UserReport.objects.filter(email = email).values('file', 'uploaded_at')
        return Response(reports, status=status.HTTP_200_OK)



