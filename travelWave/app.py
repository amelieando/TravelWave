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
    "imgs/img1.jpg",
    "imgs/img2.jpg",
    "imgs/img3.jpg",
    "imgs/img4.jpg",
    "imgs/img5.jpg",
    "imgs/img6.jpg",
    "imgs/img7.jpg",
    "imgs/img8.jpg",
    "imgs/img9.jpg",
    "imgs/img10.jpg",
    "imgs/img11.jpg",
    "imgs/img12.jpg",
    "imgs/img13.jpg",
    "imgs/img14.jpg",
    "imgs/img15.jpg",
    "imgs/img16.jpg",
    "imgs/img17.jpg",
    "imgs/img18.jpg",
    "imgs/img19.jpg",
    "imgs/img20.jpg",
]

@app.route("/")
def index():
    return render_template("index.html", slideshow_images=SLIDESHOW_IMAGES, show_sidebar=False)

@app.route("/planner", methods=["GET"])
def planner():
    # Pass empty/default values for the form on initial GET request
    return render_template("planner.html", 
                           destination="", 
                           start_date="", 
                           end_date="", 
                           travelers=1, 
                           budget="", 
                           accommodation_type="", 
                           transportation="", 
                           interests="",
                           itinerary_html=None,
                           show_sidebar=True)

@app.route("/create_itinerary", methods=["POST"])
def create_itinerary():
    destination = request.form["destination"]
    start_date_str = request.form["start_date"]
    end_date_str = request.form["end_date"]
    travelers = int(request.form["travelers"])
    budget = request.form.get("budget")
    accommodation_type = request.form.get("accommodation_type")
    transportation = request.form.get("transportation")
    interests = request.form.get("interests")

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        if start_date > end_date:
            flash("Start date cannot be after end date.", "error")
            # Keep original form data on error
            return render_template(
                "planner.html",
                destination=destination,
                start_date=start_date_str,
                end_date=end_date_str,
                travelers=travelers,
                budget=budget,
                accommodation_type=accommodation_type,
                transportation=transportation,
                interests=interests,
                itinerary_html=None, # No itinerary on error
                show_sidebar=True
            )
    except ValueError:
        flash("Invalid date format.", "error")
        # Keep original form data on error
        return render_template(
            "planner.html",
            destination=destination,
            start_date=start_date_str,
            end_date=end_date_str,
            travelers=travelers,
            budget=budget,
            accommodation_type=accommodation_type,
            transportation=transportation,
            interests=interests,
            itinerary_html=None, # No itinerary on error
            show_sidebar=True
        )

    # Call the AI itinerary generation function
    itinerary_html = generate_ai_itinerary(
        destination, start_date, end_date, travelers, budget, interests, accommodation_type, transportation
    )

    # Save the trip to the database
    new_trip = TripItinerary(
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        travelers=travelers,
        budget=budget,
        interests=interests,
        accommodation_type=accommodation_type,
        transportation=transportation,
        itinerary_content=itinerary_html # Save the generated HTML
    )
    db.session.add(new_trip)
    db.session.commit()
    flash("Itinerary generated and saved successfully!", "success")

    return render_template(
        "planner.html",
        destination=destination,
        start_date=start_date_str,
        end_date=end_date_str,
        travelers=travelers,
        budget=budget,
        accommodation_type=accommodation_type,
        transportation=transportation,
        interests=interests,
        itinerary_html=itinerary_html,
        show_sidebar=True
    )

@app.route("/saved_trips")
def saved_trips():
    trips = TripItinerary.query.order_by(TripItinerary.created_at.desc()).all()
    return render_template("saved_trips.html", trips=trips, show_sidebar=True)

# User's provided AI Itinerary Generation Function
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
        1. You are a pro experienced traveler who has traveled to every place in the world and has all the recommendations possible for people who need ideas for a trip.
        2. Create a trip overview with key highlights for must do activities
        3. Day-by-day detailed schedule with morning, afternoon, and evening activities listing recomended places to go and what to do based off of the users desires and {destination}, also add time stamps for everything
        4. In the detailed day-by-day schedule add specific restaurant recommendations for meals, and mention what kind of restaurant they are
        5. List cultural attractions and activities based on their interests
        6. Practical travel tips specific to {destination}
        7. Estimated costs where possible, stop writting after this.

        
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

# Fallback itinerary function (previously generate_basic_itinerary_html)
def generate_fallback_itinerary(
    destination,
    start_date,
    end_date,
    travelers,
    budget,
    accommodation_type,
    transportation,
    interests,
):
    """Generates a basic HTML itinerary as a fallback."""
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
        <p><em>Note: AI-generated content is temporarily unavailable. This is a basic itinerary fallback.</em></p>
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

if __name__ == "__main__":
    app.run(debug=True)
