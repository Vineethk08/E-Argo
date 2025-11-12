from django.shortcuts import redirect, render
from django.contrib import messages
from markupsafe import Markup
import requests
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import User, ResNet9
from django.contrib.auth import authenticate, login
from .disease import disease_dic
from .fertilizer import fertilizer_dic
import numpy as np
import pandas as pd
from datetime import datetime
import pickle
import io
import os

# Optional PyTorch imports
try:
    import torch
    from torchvision import transforms
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    transforms = None

from PIL import Image

# Get the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

crop_recommendation_model_path = os.path.join(BASE_DIR, 'models', 'RandomForest.pkl')
if os.path.exists(crop_recommendation_model_path):
    crop_recommendation_model = pickle.load(
        open(crop_recommendation_model_path, 'rb'))
else:
    crop_recommendation_model = None
    print(f"Warning: Crop recommendation model not found at {crop_recommendation_model_path}")

# Loading plant disease classification model

disease_classes = ['Apple___Apple_scab',
                   'Apple___Black_rot',
                   'Apple___Cedar_apple_rust',
                   'Apple___healthy',
                   'Blueberry___healthy',
                   'Cherry_(including_sour)___Powdery_mildew',
                   'Cherry_(including_sour)___healthy',
                   'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
                   'Corn_(maize)___Common_rust_',
                   'Corn_(maize)___Northern_Leaf_Blight',
                   'Corn_(maize)___healthy',
                   'Grape___Black_rot',
                   'Grape___Esca_(Black_Measles)',
                   'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
                   'Grape___healthy',
                   'Orange___Haunglongbing_(Citrus_greening)',
                   'Peach___Bacterial_spot',
                   'Peach___healthy',
                   'Pepper,_bell___Bacterial_spot',
                   'Pepper,_bell___healthy',
                   'Potato___Early_blight',
                   'Potato___Late_blight',
                   'Potato___healthy',
                   'Raspberry___healthy',
                   'Soybean___healthy',
                   'Squash___Powdery_mildew',
                   'Strawberry___Leaf_scorch',
                   'Strawberry___healthy',
                   'Tomato___Bacterial_spot',
                   'Tomato___Early_blight',
                   'Tomato___Late_blight',
                   'Tomato___Leaf_Mold',
                   'Tomato___Septoria_leaf_spot',
                   'Tomato___Spider_mites Two-spotted_spider_mite',
                   'Tomato___Target_Spot',
                   'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
                   'Tomato___Tomato_mosaic_virus',
                   'Tomato___healthy']

# disease prediction
disease_model_path = os.path.join(BASE_DIR, 'models', 'plant_disease_model.pth')
if TORCH_AVAILABLE and os.path.exists(disease_model_path):
    disease_model = ResNet9(3, len(disease_classes))
    disease_model.load_state_dict(torch.load(
        disease_model_path, map_location=torch.device('cpu')))
    disease_model.eval()
else:
    disease_model = None
    if not TORCH_AVAILABLE:
        print("Warning: PyTorch is not installed. Disease detection will not work.")
    else:
        print(f"Warning: Disease detection model not found at {disease_model_path}")


def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'aboutus.html')

def contact(request):
    return render(request, 'contact.html')

def userlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Wrong Username or Password')
            return render(request, 'userlogin.html')
    else:
        return render(request, 'userlogin.html')

def usersignup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']

        # Validate passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match. Please try again.')
            return render(request, 'usersignup.html')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" is already taken. Please choose a different username.')
            return render(request, 'usersignup.html')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, f'Email "{email}" is already registered. Please use a different email or try logging in.')
            return render(request, 'usersignup.html')

        try:
            user = User.objects.create_user(
                username=username, 
                last_name=last_name, 
                first_name=first_name, 
                password=password1, 
                email=email, 
                is_user=True
            )
            user.save()
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('userlogin')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}. Please try again.')
            return render(request, 'usersignup.html')
    else:
        return render(request, 'usersignup.html')



def logout_view(request):
    logout(request)
    return redirect('/')

def crop_recommend(request):
    return render(request, 'crop.html')

def fertilizer_recommendation(request):
    return render(request, 'fertilizer.html')

def disease(request):
    return render(request, 'disease.html')

def weather_fetch(city_name):
    """
    Fetch and returns the temperature and humidity of a city
    :params: city_name
    :return: temperature, humidity
    """
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid=9d7cde1f6d07ec55650544be1631307e'
        response = requests.get(url, timeout=10)
        x = response.json()

        # Check if request was successful
        if response.status_code == 200 and "main" in x:
            y = x["main"]
            temperature = round((y["temp"] - 273.15), 2)
            humidity = y["humidity"]
            return temperature, humidity
        else:
            # API returned an error (invalid key, city not found, etc.)
            return None
    except (requests.RequestException, KeyError, ValueError) as e:
        # Handle network errors, missing keys, or JSON parsing errors
        print(f"Weather API error: {e}")
        return None


def crop_prediction(request):

    if request.method == 'POST':
        if crop_recommendation_model is None:
            messages.error(request, 'Crop recommendation model is not available. Please add the model file.')
            return render(request, 'crop.html')
            
        try:
            N = int(request.POST['nitrogen'])
            P = int(request.POST['phosphorous'])
            K = int(request.POST['pottasium'])
            ph = float(request.POST['ph'])
            rainfall = float(request.POST['rainfall'])

            # state = request.POST.get("stt")
            city = request.POST.get("city")

            # Try to fetch weather data
            weather_data = weather_fetch(city)
            
            if weather_data != None:
                temperature, humidity = weather_data
                data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
                my_prediction = crop_recommendation_model.predict(data)
                print(my_prediction)
                final_prediction = my_prediction[0]

                return render(request, 'crop-result.html', context={"prediction":final_prediction})
            else:
                # Weather API failed - use default values for temperature and humidity
                # Default: 25°C temperature, 60% humidity (typical agricultural conditions)
                temperature = 25.0
                humidity = 60.0
                messages.warning(request, f'Could not fetch weather data for {city}. Using default values (Temperature: {temperature}°C, Humidity: {humidity}%).')
                
                data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
                my_prediction = crop_recommendation_model.predict(data)
                print(my_prediction)
                final_prediction = my_prediction[0]

                return render(request, 'crop-result.html', context={"prediction":final_prediction})
        except (ValueError, KeyError) as e:
            messages.error(request, f'Invalid input data. Please check your values and try again.')
            return render(request, 'crop.html')


def predict_image(img, model=None):
    """
    Transforms image to tensor and predicts disease label
    :params: image
    :return: prediction (string)
    """
    if not TORCH_AVAILABLE:
        return None
        
    if model is None:
        model = disease_model
    if model is None:
        return None
        
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.ToTensor(),
    ])
    image = Image.open(io.BytesIO(img))
    img_t = transform(image)
    img_u = torch.unsqueeze(img_t, 0)

    # Get predictions from model
    yb = model(img_u)
    # Pick index with highest probability
    _, preds = torch.max(yb, dim=1)
    prediction = disease_classes[preds[0].item()]
    # Retrieve the class label
    return prediction

def disease_prediction(request):
    if request.method == 'POST':
        # Check if PyTorch is available
        if not TORCH_AVAILABLE:
            messages.error(request, 'PyTorch is not installed. Disease detection requires PyTorch (needs Python 3.11 or 3.12). Please install PyTorch first.')
            return render(request, 'disease.html')
        
        # Check if model is available
        if disease_model is None:
            messages.error(request, 'Disease detection model is not available. Please add the model file (plant_disease_model.pth) to the models directory.')
            return render(request, 'disease.html')
            
        if 'file' not in request.FILES:
            messages.error(request, 'No file was uploaded. Please select an image file.')
            return render(request, 'disease.html')
            
        file = request.FILES['file']
        if not file:
            messages.error(request, 'Invalid file. Please upload a valid image file.')
            return render(request, 'disease.html')
            
        try:
            img = file.read()
            prediction = predict_image(img)
            if prediction is None:
                messages.error(request, 'Model prediction failed. Please try a different image or check if the model is properly loaded.')
                return render(request, 'disease.html')
            prediction = Markup(str(disease_dic[prediction]))
            return render(request, 'disease-result.html', context={"prediction": prediction})
        except Exception as e:
            messages.error(request, f'Error processing image: {str(e)}. Please ensure you uploaded a valid image file.')
            return render(request, 'disease.html')
    return render(request, 'disease.html')


def fert_recommend(request):
    title = '- Fertilizer Suggestion'
    crop_name = str(request.POST['cropname'])
    N = int(request.POST['nitrogen'])
    P = int(request.POST['phosphorous'])
    K = int(request.POST['pottasium'])
    # ph = float(request.form['ph'])

    fertilizer_csv_path = os.path.join(BASE_DIR, 'Data', 'fertilizer.csv')
    if not os.path.exists(fertilizer_csv_path):
        messages.error(request, 'Fertilizer data file is not available. Please add the fertilizer.csv file.')
        return render(request, 'fertilizer.html')
    
    df = pd.read_csv(fertilizer_csv_path)

    nr = df[df['Crop'] == crop_name]['N'].iloc[0]
    pr = df[df['Crop'] == crop_name]['P'].iloc[0]
    kr = df[df['Crop'] == crop_name]['K'].iloc[0]

    n = nr - N
    p = pr - P
    k = kr - K
    temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
    max_value = temp[max(temp.keys())]
    if max_value == "N":
        if n < 0:
            key = 'NHigh'
        else:
            key = "Nlow"
    elif max_value == "P":
        if p < 0:
            key = 'PHigh'
        else:
            key = "Plow"
    else:
        if k < 0:
            key = 'KHigh'
        else:
            key = "Klow"

    response = Markup(str(fertilizer_dic[key]))

    return render(request, 'fertilizer-result.html', context = {"recommendation": response, "title":title})