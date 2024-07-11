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
# from .forms import UploadFileForm
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
        # logger.info("Received request with data: %s", request.data)
        
        if 'file' not in request.FILES or 'email' not in request.data:
            print("File or email not found in request")
            return Response({"error": "No file or email provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        file_obj = request.FILES['file']
        # username = request.data['username']
        report_identifier = request.data['report_identifier']
        email = request.data['email']
        file_name = file_obj.name
        # print('file OBJ:***', file_obj)

        if report_identifier:
            try:
                user_report = UserReport.objects.get(email=email, report_identifier=report_identifier)
            except UserReport.DoesNotExist:
                user_report = UserReport(email=email, report_identifier=report_identifier)
        else:
            user_report = UserReport(email=email)


        if 'MEDSCAN_00' in file_name:
            # user_report = UserReport(diagnosis_file = file_obj)
            user_report.diagnosis_file = file_obj
            # user_report.save()
        else:
                
            # user_report = UserReport(email= email, file=file_obj)
            user_report.uploaded_file =file_obj
            user_report.save()
            # user_report.save()
            # print('USER REPORT UPDATED FILE AND USER************')
            file_type = file_obj.content_type
            file_extension = os.path.splitext(file_obj.name)[1].lower()
            
            print(file_extension)

            #Checking to see if the file is a pdf or an image

            if file_type == 'application/pdf' or file_extension == '.pdf':
                user_report.save()
                pdf_path = user_report.uploaded_file.path
                print(user_report.uploaded_file)
                try:
                    text = self.extract_text_from_pdf(pdf_path)
                except Exception as e:
                    return Response({"error": f"Failed to process PDF: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            elif file_type in ['image/jpeg', 'image/png'] or file_extension in ['.jpg', '.jpeg', '.png']:
                user_report.save()
                image_path = user_report.uploaded_file.path
                try:
                    text = self.extract_text_from_image(image_path)
                except Exception as e:
                    return Response({"error": f"Failed to process image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)

            
            # print('image path determined')
            attributes = self.parse_cbc_report(text)
            
            print("PARSED ATTRIBUTES:****", attributes)
            return Response(attributes, status=status.HTTP_200_OK)

        user_report.save()
        return Response({"message": "File uploaded successfully."}, status=status.HTTP_200_OK)


    def extract_text_from_pdf(self, pdf_path):
        print('opening file....', pdf_path)
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
        reports = UserReport.objects.filter(email=email).values('uploaded_file', 'diagnosis_file', 'uploaded_at', 'report_identifier')
        return Response(reports, status=status.HTTP_200_OK)

