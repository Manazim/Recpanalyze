# Recpanalyze

# README for Recipe Recommendation System

# Overview

This project is a **Recipe Recommendation System** that integrates machine learning inference and multiple APIs to detect ingredients from uploaded images and provide recipe suggestions. It also offers an analysis feature that evaluates recipe suitability based on user-specific data.

---

# Features

### 1. Ingredient Detection  
   Uses the Roboflow Inference API to detect ingredients in uploaded images.

### 2. Recipe Recommendation  
   Fetches recipes based on detected ingredients using the Spoonacular API.

### 3. Recipe Analysis
   Allows users to input personal details (e.g., weight, height, and health conditions) and analyzes recipe suitability using JamAI.

### 4. Dynamic Redirection 
   Redirects users to detailed recipe pages on Spoonacular.

---

# Dependencies

## Python Libraries:  
  - `os`  
  - `requests`  
  - `flask`  
  - `tempfile`  
  - `re`  
  - External SDKs: `inference_sdk`, `jamaibase`  

## APIs and Services:
  - Roboflow Inference API: For object detection in images.
  - Spoonacular API: For recipe retrieval.
  - JamAI: For advanced analysis and result storage.

---

# File Structure

- `app.py`: Main application file containing the Flask app and routes.
- `templates/`: Directory for HTML templates.
  - `index.html`: Home page for image uploads.
  - `recipes.html`: Displays detected ingredients and recommended recipes.
  - `analysis_result.html`: Shows analyzed recipe suitability.
- `static/`: Directory for static files (CSS, JS, images).

---

# Usage

1. Install Dependencies 
   Use the following command to install required Python libraries:
   ```bash
   pip install flask requests
   ```

2. Run the Application  
   Start the Flask application:
   ```bash
   python app.py
   ```
   By default, the app runs on `http://127.0.0.1:5000`.

3. Upload an Image  
   - Navigate to the home page.
   - Upload an image of food items.
   - View detected ingredients and recipes.

4. Analyze Recipe
   - Input your weight, height, and health conditions.
   - Get a detailed analysis of the recipe's suitability.

---

# API Configuration

1. Roboflow API  
   - Replace `api_url` and `api_key` in `InferenceHTTPClient` initialization with your Roboflow credentials.

2. Spoonacular API 
   - Replace `SPOONACULAR_API_KEY` with your Spoonacular API key.

3. JamAI API
   - Replace the `api_key` and `project_id` in `JamAI` initialization with your JamAI credentials.

---

# Code Highlights

## Ingredient Detection (Roboflow)
```python
result = CLIENT.infer(temp_file.name, model_id=MODEL_ID)
for prediction in result["predictions"]:
    label = prediction["class"]
    detected_items.append(label)
```

## Recipe Fetching (Spoonacular)
```python
params = {
    "apiKey": SPOONACULAR_API_KEY,
    "query": ",".join(detected_items),
    "number": 20,
    "ranking": 2
}
response = requests.get(SPOONACULAR_API_URL, params=params)
```

## Analysis and Formatting
```python
formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', suitability)
formatted = formatted.replace("\\n", "\n").replace("\n", "<br>")
```

---
