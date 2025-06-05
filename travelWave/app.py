import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.middleware.proxy_fix import ProxyFix
from database import db
from models import TripItinerary
from datetime import datetime, timedelta
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure Google Generative AI
# Global configuration
API_KEY = "AIzaSyCcdFlnejJo3zVBaKTre4bdYfphKOe7_Aw" 

# Configure the Google Generative AI client
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///travel_planner.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Stock photo URLs for slideshow
SLIDESHOW_IMAGES = [
    "https://pixabay.com/get/gc2a303c15163839f9f2697be3cf8cfc9f39f03263821520024ebf9b33f6c820eb33db6cc1b896ba9cffc6d972b0f6b52c805e34fee7edbf5b3f802699b920a29_1280.jpg",
    "https://pixabay.com/get/g31e55b1f494dc3e80bec9bb63ca4de6aa6bf7d010bfc6ccf0a670d51dbd55a1c5f3a158d2264c55fa4e5f371b53a7ea8a16b85c920312f498de84c62095c4ad9_1280.jpg",
    "https://pixabay.com/get/g2b8d74c124536dd8ce1aa23b37de415cc9ce07d599ad3cb3e8a7c2d603f0c26164d6d8c86bb8c5c054e6f4288ba3e086658bf30e6b6f9e1222329cfc0f23958f_1280.jpg",
    "https://pixabay.com/get/g62b1f875562c8534eede0773ace5e5d1f43295cb86927ffa504d4f3613413830ae1b9cce03db5f71290df746427f2c9cb3d5777c7839e4771bc1ca21904d1a6a_1280.jpg",
    "https://pixabay.com/get/g18fdf5d710797243efa617119db2015e4f23fc60d20a0e2664c53d42050eb6b21af78e43ff1ea48aaf4fcea35c5a9f155a8c5505cba4c564f58f0bea1b1ca7d4_1280.jpg",
    "https://pixabay.com/get/gc8ef0b6cb203008584a6f50a086c4c9efae5dfb203f8f450032aa728c2d02fc3ff74de9b4599fa030c8bb64a4797f96486140f18c8e954b78746081c686aebdc_1280.jpg",
    "https://pixabay.com/get/ga8f37e32339d886093cc20b3f17332d819d262b8d733d0b20cb30dae687f1c9d9e9194faec599b3d254726ead942358013018a97d2979721b983e78b5be2f97f_1280.jpg",
    "https://pixabay.com/get/ge876656e25744807cd7b5ea8aee1e7ffcc28a2ecd3071df14945c16f322dd8aea668bd06966c32724aa9c8b017ad3eff599fba3bd0890b116bd183b65a082177_1280.jpg",
    "https://pixabay.com/get/g7ce9db5d4aa8ae051137d05b9329dac733971d9e233c2fdf1527955da25d2f5557f3078fda6b2c228d0b7973fb4de6966f36f53410709fc731e13f8cb7291790_1280.jpg",
    "https://pixabay.com/get/gb9e67e2976997e7bd7c4d010e19724d38b95956e4daa865b88b9757c70d51052e33de1bf9892730883720a064bf48bb0b11334dda837e7cf230cc371e32446c5_1280.jpg",
]

# Routes
@app.route('/')
def index():
    """Landing page with slideshow background"""
    return render_template('index.html', slideshow_images=SLIDESHOW_IMAGES)

@app.route('/planner')
def planner():
    """Trip planning interface"""
    return render_template('planner.html')

@app.route('/create_itinerary', methods=['POST'])
def create_itinerary():
    """Create a new travel itinerary using Google Gemini AI"""
    try:
        # Get form data
        destination = request.form.get('destination')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        travelers = int(request.form.get('travelers', 1))
        budget = request.form.get('budget')
        interests = request.form.get('interests')
        accommodation_type = request.form.get('accommodation_type')
        transportation = request.form.get('transportation')
        
        # Validate required fields
        if not destination or not start_date_str or not end_date_str:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('planner'))
        
        # Parse dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        if start_date >= end_date:
            flash('End date must be after start date.', 'error')
            return redirect(url_for('planner'))
        
        # Generate AI-powered itinerary
        itinerary_content = generate_ai_itinerary(
            destination, start_date, end_date, travelers, 
            budget, interests, accommodation_type, transportation
        )
        
        # Create new itinerary
        itinerary = TripItinerary(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            travelers=travelers,
            budget=budget,
            interests=interests,
            accommodation_type=accommodation_type,
            transportation=transportation,
            itinerary_content=itinerary_content
        )
        
        db.session.add(itinerary)
        db.session.commit()
        
        flash('Your AI-generated travel itinerary has been created successfully!', 'success')
        return render_template('planner.html', itinerary=itinerary)
        
    except Exception as e:
        logging.error(f"Error creating itinerary: {str(e)}")
        flash('An error occurred while creating your itinerary. Please try again.', 'error')
        return redirect(url_for('planner'))

def generate_ai_itinerary(destination, start_date, end_date, travelers, budget, interests, accommodation_type, transportation):
    """Generate a detailed travel itinerary using Google Gemini AI"""
    
    try:
        duration = (end_date - start_date).days
        
        # Create a detailed prompt for the AI
        prompt = f"""
        Create a detailed, personalized travel itinerary for a {duration}-day trip to {destination}.
        
        Trip Details:
        - Destination: {destination}
        - Travel Dates: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}
        - Number of Travelers: {travelers}
        - Budget: {budget if budget else 'Not specified'}
        - Accommodation Type: {accommodation_type if accommodation_type else 'Not specified'}
        - Transportation: {transportation if transportation else 'Not specified'}
        - Interests: {interests if interests else 'General sightseeing'}
        
        Please provide a comprehensive itinerary that includes:
        1. A trip overview with key highlights for must do activities
        2. Day-by-day detailed schedule with morning, afternoon, and evening activities listing recomended places to go and what to do, also add time stamps for everything
        3. In the detailed day-by-day schedule add specific restaurant recommendations for meals
        4. List cultural attractions and activities based on their interests
        5. Practical travel tips specific to {destination}
        6. Estimated costs where possible
        
        Format the response in HTML with proper headings, lists, and structure that will look good on a website.
        Use <h3>, <h4>, <h5> for headings, <p> for paragraphs, <ul>/<li> for lists, and <div> with appropriate classes.
        Make it engaging and informative!
        """
        
        # Generate content using Gemini AI
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text
        else:
            # Fallback to basic itinerary if AI fails
            return generate_fallback_itinerary(destination, start_date, end_date, travelers, budget, interests, accommodation_type, transportation)
            
    except Exception as e:
        logging.error(f"Error generating AI itinerary: {str(e)}")
        # Fallback to basic itinerary if AI fails
        return generate_fallback_itinerary(destination, start_date, end_date, travelers, budget, interests, accommodation_type, transportation)

def generate_fallback_itinerary(destination, start_date, end_date, travelers, budget, interests, accommodation_type, transportation):
    """Fallback function for basic itinerary generation if AI fails"""
    duration = (end_date - start_date).days
    
    return f"""
    <h3>Your {duration}-Day Trip to {destination}</h3>
    <div class="trip-overview">
        <p><strong>Travel Dates:</strong> {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}</p>
        <p><strong>Number of Travelers:</strong> {travelers}</p>
        {f'<p><strong>Budget:</strong> {budget}</p>' if budget else ''}
        {f'<p><strong>Accommodation Type:</strong> {accommodation_type}</p>' if accommodation_type else ''}
        {f'<p><strong>Transportation:</strong> {transportation}</p>' if transportation else ''}
        {f'<p><strong>Interests:</strong> {interests}</p>' if interests else ''}
    </div>
    
    <div class="ai-notice">
        <p><em>Note: This is a basic itinerary. AI-generated content is temporarily unavailable.</em></p>
    </div>
    
    <h4>Basic Daily Itinerary</h4>
    <div class="day-plan">
        <h5>Day 1 - Arrival</h5>
        <p>Arrive in {destination}, check into accommodation, and explore the local area.</p>
    </div>
    
    <div class="travel-tips">
        <h4>General Travel Tips</h4>
        <ul>
            <li>Check visa requirements and ensure your passport is valid</li>
            <li>Research local customs and etiquette</li>
            <li>Pack appropriate clothing for the weather</li>
        </ul>
    </div>
    """

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)