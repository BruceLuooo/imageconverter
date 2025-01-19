from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
from django.http import FileResponse
import uuid 
from io import BytesIO

# Register HEIF opener (Allows pillow to convert HEIC files (Image file type of Iphone when Airdropped))
register_heif_opener()

class ImageUploadView(APIView):
    def post(self, request, *args, **kwargs):
        images = request.FILES.getlist("images") 
        
        images_to_convert = []
        dpi = 300
        a4_width, a4_height = int(8.27 * dpi), int(11.69 * dpi)

        for image in images:
            with Image.open(image) as img:
                img = ImageOps.exif_transpose(img)  # Correct orientation if necessary
                img = ImageOps.pad(img, (a4_width, a4_height), color='white', centering=(0.5, 0.5)) # Makes all pages the same size
                images_to_convert.append(img.convert('RGB'))  # Convert to RGB for saving as PDF

        if images_to_convert:

            output_pdf = BytesIO() #save in-memory because we don't need to actually save the pdf file right now in a server
            images_to_convert[0].save(output_pdf, save_all=True, append_images=images_to_convert[1:], format="PDF")
            output_pdf.seek(0)
            filename = str(uuid.uuid4()) + '.pdf'
            
            return FileResponse(output_pdf, content_type='application/pdf', as_attachment=True, filename=filename)
        else:
            return Response(
                {"error": "No valid images to process"},
                status=status.HTTP_400_BAD_REQUEST,
            )
