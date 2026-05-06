from prophet import Prophet
import pandas as pd
from .sales_data import get_sales_data
from products.models import Product

def forecast_demand(product_id, periods=30):
    """পরবর্তী ৩০ দিনের চাহিদা প্রেডিক্ট করো"""
    
    df = get_sales_data(product_id, days=90)
    if df is None or len(df) < 7:
        return {"error": "পর্যাপ্ত ডাটা নেই (কমপক্ষে ৭ দিনের সেলস লাগবে)"}
    
    # Prophet মডেল তৈরি
    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False,
        changepoint_prior_scale=0.05
    )
    model.fit(df)
    
    # ভবিষ্যতের জন্য ডেটাফ্রেম
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    
    # শুধু প্রেডিক্টেড অংশ বের করো
    predicted = forecast.tail(periods)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    predicted['ds'] = predicted['ds'].dt.strftime('%Y-%m-%d')
    predicted['yhat'] = predicted['yhat'].round(0).astype(int)
    
    return {
        "product_id": product_id,
        "product_name": Product.objects.get(id=product_id).name,
        "forecast": predicted.to_dict('records')
    }