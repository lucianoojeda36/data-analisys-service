from rest_framework.views import APIView
from rest_framework.response import Response
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from django.http import FileResponse, HttpResponse
from django.views import View
from .models import Sale
from .serializers import SaleSerializer
import matplotlib
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import io

matplotlib.use('Agg')

class SalesSummaryView(APIView):
    def get(self, request):
        # Retrieve all sales data from the database
        sales_data = Sale.objects.all().values()
        
        df = pd.DataFrame(sales_data)
        
        # Check and remove NaN or infinite values
        df = df.replace([np.inf, -np.inf], np.nan).dropna()

        # If no data is available
        if df.empty:
            return Response({"error": "No sales data available."}, status=400)

        try:
            # Generate a statistical summary using Pandas
            summary = df.describe(include='all').to_dict()

            # Replace NaN with a manageable value
            for key, value in summary.items():
                summary[key] = {k: (v if not pd.isna(v) else "N/A") for k, v in value.items()}

            return Response(summary)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class SalesVisualizationView(APIView):
    def get(self, request):
        # Retrieve all sales data from the database
        sales_data = Sale.objects.all()
        serializer = SaleSerializer(sales_data, many=True)

        # Convert serialized data to a DataFrame
        df = pd.DataFrame(serializer.data)

        # If no data is available
        if df.empty:
            return Response({"error": "No sales data available."}, status=400)

        # Create an example bar chart
        plt.figure(figsize=(10, 6))
        sns.barplot(x='product_name', y='quantity', data=df)

        # Save the chart in memory as a PDF
        buffer = io.BytesIO()
        plt.savefig(buffer, format='pdf')
        buffer.seek(0)
        plt.close()  # Close the figure to free memory

        # Return the PDF as an HTTP response
        return FileResponse(buffer, as_attachment=True, filename='sales_visualization.pdf')
    

class DownloadGraphView(View):
    def get(self, request, *args, **kwargs):
        # Retrieve all sales data from the database
        sales_data = Sale.objects.all()
        serializer = SaleSerializer(sales_data, many=True)

        # Convert serialized data to a DataFrame
        df = pd.DataFrame(serializer.data)

        # If no data is available
        if df.empty:
            return HttpResponse("No sales data available.", status=400)

        # Create a bar chart using sold quantities by product
        plt.figure(figsize=(10, 6))
        plt.bar(df['product_name'], df['quantity'])
        plt.title('Quantity Sold by Product')
        plt.xlabel('Product Name')
        plt.ylabel('Quantity Sold')
        plt.xticks(rotation=45)

        # Create an in-memory buffer to save the chart
        buffer = BytesIO()
        plt.savefig(buffer, format='png')  # Save as PNG
        plt.close()
        buffer.seek(0)  # Return to the start of the buffer

        # Save the image temporarily
        image_path = 'temp_image.png'
        with open(image_path, 'wb') as f:
            f.write(buffer.getvalue())

        # Create the PDF using ReportLab
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter

        # Add text to the PDF
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 80, "Sales Report")

        c.setFillColor('black')  # Set the text color to black
        c.setFont("Helvetica", 12)
        text = "This report shows the quantity of products sold in the last month."
        c.drawString(100, height - 100, text)  # Adjust the Y position as needed

        # Add the chart image to the PDF
        c.drawImage(image_path, 50, height - 400, width=500, height=300)

        c.showPage()
        c.save()  # Save the PDF
        pdf_buffer.seek(0)  # Return to the start of the buffer

        # Remove the temporary image
        os.remove(image_path)

        # Create the HTTP response with the PDF content
        response = FileResponse(pdf_buffer, as_attachment=True, filename='sales_visualization.pdf')
        return response
