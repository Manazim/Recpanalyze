import os
import requests
from flask import Flask, request, render_template, redirect
from inference_sdk import InferenceHTTPClient
import tempfile
from jamaibase import JamAI, protocol as p
import re

# Initialize Flask app
app = Flask(__name__)

jamai = JamAI(api_key="", project_id="")

# Roboflow Client Configuration
CLIENT = InferenceHTTPClient(
    api_url="",
    api_key=""
)
MODEL_ID = "fruits-and-vegetables-2vf7u/1"

# Spoonacular API Configuration
SPOONACULAR_API_KEY = ""
SPOONACULAR_API_URL = "https://api.spoonacular.com/recipes/complexSearch"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return "No image uploaded", 400

    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400

    # Create a temporary file to save the image
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file.read())
        temp_file.close()

        # Perform inference with Roboflow using the temporary file path
        result = CLIENT.infer(temp_file.name, model_id=MODEL_ID)
        print(result)  # Log the inference response

    detected_items = []

    # Process the detection results and get item labels
    for prediction in result["predictions"]:
        label = prediction["class"]
        detected_items.append(label)

    # Now fetch recipes using the detected items
    recipes = []
    if detected_items:
        # Call Spoonacular API for recipe suggestions
        params = {
            "apiKey": SPOONACULAR_API_KEY,
            "query": ",".join(detected_items),
            "number": 20,  # Number of recipes to fetch
            "ranking": 2  # Prioritize recipes that use all ingredients
        }
        response = requests.get(SPOONACULAR_API_URL, params=params)
        
        

        if response.status_code == 200:
            results = response.json().get('results', [])
            for recipe in results:
                recipe_id = recipe.get('id')
                # Fetch detailed recipe information
                recipe_details_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
                details_response = requests.get(recipe_details_url, params={"apiKey": SPOONACULAR_API_KEY})

                if details_response.status_code == 200:
                    details = details_response.json()
                    source_url = details.get('spoonacularSourceUrl')
                    summary = details.get ('summary')
                    
                   
                    if source_url:
                        recipe['view_url'] = source_url  # Use the source URL for redirection
                        
                    if summary:
                        recipe['summary_menu'] = summary  # Use the source URL for redirection
                        
                else:
                    recipe['view_url'] = "#"  # Fallback if source URL is not available

            recipes = results
        else:
            recipes = [{"title": "Failed to fetch recipes", "error": response.status_code}]

    # Render the page with detected items and recipe suggestions
    return render_template(
        'recipes.html', 
        ingredients=detected_items,  # Detected ingredients
        recipes=recipes              # Recipe suggestions
    )

@app.route('/redirect_to_recipe/<path:url>')
def redirect_to_recipe(url):
    # Redirect to the spoonacular source URL directly
    return redirect(url)

@app.route('/analyze', methods=['POST'])
def analyze_recipe():
    # Extract user input for weight, height, and diseases
    weight = request.form['weight']
    height = request.form['height']
    diseases = request.form['diseases']
    recipe_summary = request.form['recipe_summary']
    recep = recipe_summary
    print(recep)

    try:
        completion = jamai.add_table_rows(
            "action",
            p.RowAddRequest(
                table_id="Recipe",
                data=[{"weight": weight, "height": height, "diseases": diseases, "summary": recipe_summary}],
                stream=False
            )
        )

        # Extract analysis result
      

        if completion.rows:
           output_row = completion.rows[0].columns  # Access the row's columns
           suitability = output_row.get("Result")
    
           if suitability:
             # Convert suitability to a string if it's not already
            suitability_str = str(suitability)
          
        
        # Use regex to match content= and properly handle escaped quotes
            match = re.search(r"content=['\"](.*?)['\"], name=None", suitability_str)
            

        
            if match:
            # Replace escaped single quotes with actual single quotes
             content = match.group(1).replace("\\'", "'")
             suitability = content
             suitability = format_analysis(suitability)
              
            else:
                print("not match")


        else:
            suitability = "No analysis available"
    except Exception as e:
        suitability = f"Error: {str(e)}"
        
    return render_template('analysis_result.html', suitability=suitability)

def format_analysis(suitability):
    # Convert **text** to <strong>text</strong> for bold
    formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', suitability)

    # Handle headings: # -> <h1>, ## -> <h2>, ### -> <h3>
    formatted = re.sub(r'^### (.+)$', r'<h3>\1</h3>', formatted, flags=re.MULTILINE)
    formatted = re.sub(r'^## (.+)$', r'<h2>\1</h2>', formatted, flags=re.MULTILINE)
    formatted = re.sub(r'^# (.+)$', r'<h1>\1</h1>', formatted, flags=re.MULTILINE)

    # Handle escaped \n sequences
    formatted = formatted.replace("\\n", "\n")

    # Replace actual newlines with <br>
    formatted = formatted.replace("\n", "<br>")

    return formatted



if __name__ == '__main__':
    app.run(debug=True)
