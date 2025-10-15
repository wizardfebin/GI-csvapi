import csv
from io import TextIOWrapper
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .models import User

class CSVUploadAPIView(APIView):
    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({"error": "No file uploaded"},status=status.HTTP_400_BAD_REQUEST
            )
        
        if not uploaded_file.name.lower().endswith('.csv'):
            return Response({"error": "Only .csv files are accepted."},status=status.HTTP_400_BAD_REQUEST
            )

        try:
            csv_file = TextIOWrapper(uploaded_file.file, encoding='utf-8')
            reader = csv.DictReader(csv_file)
        except Exception as e:
            return Response(
                {"error": "Could not read CSV file.", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        required_headers = {"name", "email", "age"}
        if not reader.fieldnames or not required_headers.issubset({h.strip().lower() for h in reader.fieldnames}):
            return Response({"error": "CSV must contain headers: name,email,age"},status=status.HTTP_400_BAD_REQUEST
            )

        saved_count = 0
        rejected_count = 0
        skipped_count = 0
        errors = []

        for row_idx, row in enumerate(reader, start=2):
            row = {k.strip().lower(): (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            email = row.get("email", "").lower().strip()

            if email and User.objects.filter(email__iexact=email).exists():
                skipped_count += 1
                continue

            serializer = UserSerializer(data=row)
            if not serializer.is_valid():
                rejected_count += 1
                errors.append({"row": row_idx,"data": row,"errors": serializer.errors
                })
                continue

            try:
                serializer.save()
                saved_count += 1
            except Exception as e:
                rejected_count += 1
                errors.append({"row": row_idx,"data": row,"errors": {"non_field_error": [str(e)]}
                })

        return Response({"message": "File processed successfully.","saved_count": saved_count,"rejected_count": rejected_count,"skipped_count": skipped_count,"errors": errors}, status=status.HTTP_200_OK)
