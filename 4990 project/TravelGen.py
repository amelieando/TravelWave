from flask import Flask, request, jsonify, render_template
import google.generativeai as genai

# Global configuration
API_KEY = "AIzaSyCcdFlnejJo3zVBaKTre4bdYfphKOe7_Aw"  # Replace with your actual Google API key

# Configure the Google Generative AI client
genai.configure(api_key=API_KEY)

# Initialize the model
model = genai.GenerativeModel("gemini-2.0-flash")  # Use the correct model name

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """
    Serve the frontend HTML page.
    """
    return render_template('TravelFront.html')

@app.route('/generate-itinerary', methods=['POST'])
def generate_itinerary():
    """
    API endpoint to generate a travel itinerary.
    """
    data = request.get_json()
    if not data or 'vacay_description' not in data:
        return jsonify({"error": "vacay_description is required"}), 400
    
    vacation_description = data['vacay_description']
    travel_prompt = "Generate a travel itinerary for my next vacation: " + vacation_description
    
    try:
        # Generate content using the Google Generative Language API
        response = model.generate_content(travel_prompt)
        itinerary = response.text
        return jsonify({"travel_prompt": itinerary})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
