from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import StockLog
from products.models import Product
import pandas as pd

def get_sales_data(product_id, days=90):
    """গত ৯০ দিনের সেলস ডাটা রিটার্ন করবে (প্রতিদিনের সামারি)"""
    
    start_date = timezone.now() - timedelta(days=days)
    
    logs = StockLog.objects.filter(
        product_id=product_id,
        reason='sale',
        quantity_change__lt=0,  # নেগেটিভ ভ্যালু
        timestamp__gte=start_date
    ).values('timestamp__date').annotate(
        daily_sales=Sum('quantity_change')  # নেগেটিভ সেলস হবে
    ).order_by('timestamp__date')
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(list(logs))
    if df.empty:
        return None
    
    df['daily_sales'] = -df['daily_sales']  # পজিটিভ সেলসে রূপান্তর
    df['ds'] = pd.to_datetime(df['timestamp__date'])
    df['y'] = df['daily_sales']
    
    return df[['ds', 'y']]