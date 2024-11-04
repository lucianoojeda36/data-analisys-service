from django.db import models

class Sale(models.Model):
    sale_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    price = models.FloatField()
    sale_date = models.DateField()
    
    class Meta:
        db_table = 'sales' 
    
    def __str__(self):
        return self.product_name
