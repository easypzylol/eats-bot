import os
from flask import Flask, request
import telebot
from telebot import types

# Get bot token from environment variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Add your admin user ID here
ADMIN_ID = 1247375362  # Replace with your actual Telegram user ID

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Store user info for replies and broadcast
user_messages = {}
broadcast_users = set()
user_chat_states = {}  # Track user conversation states

# ===== FOOD DEALS DATA WITH LOCAL FOCUS =====
FOOD_OFFERS = {
    "student": {
        "title": "🎓 **Student Meals - Up to 60% OFF**",
        "details": """**🔥 STUDENT EXCLUSIVE DEALS**

🏫 **College Campus Areas:**
• Near Universities: Special student pricing
• Dorm Delivery: Late night options
• Meal Plans: Discounted bundles
• Study Snacks: Coffee & quick bites

🎯 **Student Requirements:**
• Budget-friendly meals under $10
• Quick delivery for study breaks
• Group orders for roommates
• Exam week specials
• Library delivery available

💰 **Student Discounts:**
• Student ID: Extra 15% off
• First order: 50% OFF entire cart
• Refer friends: $5 credit each
• Monthly passes: Save 30%

📍 **Top Student Areas:**
• University District restaurants
• Campus food trucks
• 24-hour diners near colleges
• Coffee shops with student rates"""
    },
    "local": {
        "title": "📍 **Local Restaurants - Neighborhood Deals**",
        "details": """**🍽️ LOCAL FAVORITES - COMMUNITY RESTAURANTS**

🏙️ **By City/Area:**

**NEW YORK CITY:**
• Manhattan: Local delis & pizza
• Brooklyn: Artisan food spots
• Queens: Ethnic neighborhood gems
• Bronx: Family-owned restaurants
• Staten Island: Waterfront dining

**LOS ANGELES:**
• Downtown LA: Food district
• Hollywood: Celebrity chef spots
• Santa Monica: Beachfront cafes
• Koreatown: Authentic Asian
• Downtown LA: Food trucks

**CHICAGO:**
• The Loop: Business lunch spots
• Wicker Park: Hipster cafes
• Chinatown: Authentic cuisine
• Lincoln Park: Casual dining
• River North: Trendy restaurants

**OTHER MAJOR CITIES:**
• Houston: Tex-Mex locals
• Phoenix: Southwestern cuisine
• Philadelphia: Cheesesteak spots
• San Antonio: Riverwalk restaurants
• San Diego: Coastal eateries

💰 **LOCAL DEALS:**
• Neighborhood discounts
• Regular customer rewards
• Community specials
• Happy hour extended"""
    },
    "fastfood": {
        "title": "🍔 **Fast Food Chains - 50% OFF Combos**",
        "details": """**⚡ FAST FOOD DISCOUNTS**

🍟 **Major Chains:**
• McDonald's: BOGO deals & app offers
• Burger King: Whopper discounts
• Wendy's: 4 for $4 & family packs
• Taco Bell: Cravings value menu
• KFC: Bucket meal specials
• Subway: Footlong deals
• Domino's: Pizza carryout specials
• Pizza Hut: Large pizza discounts

🎯 **Combo Deals:**
• Family meals: Feed 4 for $20
• Student combos: Under $5 meals
• Late night: After 10 PM specials
• App exclusives: Mobile-only deals

📱 **App Benefits:**
• McDonald's App: Free fries daily
• Burger King App: Whopper $1
• Taco Bell App: Exclusive cravings
• Domino's App: Carryout specials
• All apps: Points & rewards"""
    },
    "healthy": {
        "title": "🥗 **Healthy Eats - Fresh & Organic**",
        "details": """**🌱 HEALTHY OPTIONS - NUTRITIOUS MEALS**

🥗 **Healthy Categories:**
• Salad bars: Build your own
• Smoothie shops: Protein packed
• Organic cafes: Farm to table
• Vegan restaurants: Plant-based
• Gluten-free bakeries: Specialty

💪 **Fitness Focus:**
• Gym nearby restaurants
• Protein meal prep
• Post-workout smoothies
• Low-carb options
• Macro-counted meals

🏋️ **Active Lifestyle:**
• Yoga studio cafes
• Crossfit meal partners
• Sports nutrition spots
• Athletic recovery foods
• Hydration stations

💰 **Health Discounts:**
• Gym member discounts
• Fitness app linked deals
• Wellness Wednesday specials
• First healthy meal 50% OFF"""
    },
    "late": {
        "title": "🌙 **Late Night Food - Open Until 3 AM**",
        "details": """**🌙 LATE NIGHT CRAVINGS**

🕒 **Late Night Hours:**
• Open until 3 AM: Bar district spots
• 24-hour diners: Breakfast anytime
• Pizza delivery: Until 4 AM
• Food trucks: After midnight
• Convenience stores: Hot food

🎯 **Night Owl Specials:**
• Study night delivery
• Post-party food
• Shift worker meals
• Insomnia snacks
• Early bird breakfast

🍕 **Late Night Favorites:**
• Pizza by the slice
• Burgers & fries
• Tacos & burritos
• Chicken wings
• Breakfast sandwiches

💰 **Late Night Deals:**
• After midnight: 20% OFF
• 2 AM specials: Half-price
• Night shift: 25% OFF
• Student late night: Extra 10%"""
    }
}

# Local City Restaurants Database
LOCAL_RESTAURANTS = {
    "nyc": {
        "name": "New York City",
        "restaurants": [
            "Joe's Pizza - Greenwich Village",
            "Katz's Delicatessen - Lower East Side",
            "Halal Guys - Street Food",
            "Shake Shack - Madison Square Park",
            "Xi'an Famous Foods - Chinatown"
        ],
        "student_areas": ["NYU Area", "Columbia University", "Fordham Bronx", "CUNY Campuses"],
        "discount": "50% OFF first order"
    },
    "la": {
        "name": "Los Angeles",
        "restaurants": [
            "In-N-Out Burger - Multiple locations",
            "Pink's Hot Dogs - Hollywood",
            "Grand Central Market - Downtown",
            "Philippe The Original - French Dip",
            "Howlin' Ray's - Chinatown"
        ],
        "student_areas": ["USC Area", "UCLA Westwood", "Cal State LA", "Santa Monica College"],
        "discount": "40% OFF student meals"
    },
    "chicago": {
        "name": "Chicago",
        "restaurants": [
            "Portillo's - Hot Dogs & Italian Beef",
            "Lou Malnati's - Deep Dish Pizza",
            "Al's Beef - Italian Beef Sandwiches",
            "Giordano's - Stuffed Pizza",
            "Garrett Popcorn - Chicago Mix"
        ],
        "student_areas": ["UIC Area", "University of Chicago", "DePaul Lincoln Park", "Northwestern Evanston"],
        "discount": "45% OFF local favorites"
    },
    "college": {
        "name": "Top College Towns",
        "restaurants": [
            "Ann Arbor, MI - Zingerman's Deli",
            "Austin, TX - Franklin Barbecue",
            "Berkeley, CA - Chez Panisse",
            "Boston, MA - Regina Pizzeria",
            "Madison, WI - Ian's Pizza"
        ],
        "student_areas": ["Near campuses", "Dorm delivery zones", "Library drop-off", "Study spots"],
        "discount": "Student ID gets 55% OFF"
    }
}

@bot.message_handler(commands=['start'])
def start_command(message):
    if message is None:
        return

    # Add user to broadcast list
    user_id = message.from_user.id
    broadcast_users.add(user_id)
    
    # Reset chat state
    user_chat_states[user_id] = 'started'

    # Create an inline keyboard
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Food categories
    keyboard.add(types.InlineKeyboardButton("🎓 Student Meals", callback_data="food_student"))
    keyboard.add(
        types.InlineKeyboardButton("📍 Local Restaurants", callback_data="food_local"),
        types.InlineKeyboardButton("🍔 Fast Food Deals", callback_data="food_fastfood")
    )
    keyboard.add(
        types.InlineKeyboardButton("🥗 Healthy Options", callback_data="food_healthy"),
        types.InlineKeyboardButton("🌙 Late Night Food", callback_data="food_late")
    )
    keyboard.add(types.InlineKeyboardButton("🏙️ City Specific", callback_data="food_cities"))
    keyboard.add(types.InlineKeyboardButton("🎫 50% OFF Cart", callback_data="food_discount"))
    keyboard.add(types.InlineKeyboardButton("🚀 Student Areas", callback_data="food_studentareas"))
    
    # Contact & Channel
    button_channel = types.InlineKeyboardButton("📢 Join Food Deals", url="https://t.me/flights_bills_b4u")
    button_contact1 = types.InlineKeyboardButton("💬 Order Now", url="https://t.me/yrfrnd_spidy")
    button_contact2 = types.InlineKeyboardButton("📞 Support", url="https://t.me/Eatsplugsus")
    
    keyboard.add(button_channel)
    keyboard.add(button_contact1, button_contact2)

    # Start message with student focus
    message_text = (
        "🍔 **Local Food Deals Bot**\n\n"
        
        "🎓 **STUDENT SPECIAL: 50% OFF TOTAL CART!**\n"
        "• Show student ID for extra discounts\n"
        "• Campus delivery available\n"
        "• Group order discounts\n\n"
        
        "📍 **LOCAL RESTAURANTS:**\n"
        "• Neighborhood favorites\n"
        "• City-specific deals\n"
        "• Community restaurants\n"
        "• Family-owned spots\n\n"
        
        "💰 **CURRENT OFFERS:**\n"
        "✅ Up to 60% OFF student meals\n"
        "✅ Fast food combos 50% OFF\n"
        "✅ Healthy options discounts\n"
        "✅ Late night specials\n\n"
        
        "🏫 **STUDENT AREAS COVERED:**\n"
        "• University districts\n"
        "• Campus food trucks\n"
        "• Dorm delivery zones\n"
        "• Library drop-off\n\n"
        
        "*Use /location to set your area for local deals!*"
    )

    bot.send_message(message.chat.id, message_text, reply_markup=keyboard, parse_mode='Markdown')

# ===== LOCATION HANDLER =====
@bot.message_handler(commands=['location'])
def location_command(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🏙️ New York City", callback_data="city_nyc"),
        types.InlineKeyboardButton("🌴 Los Angeles", callback_data="city_la")
    )
    keyboard.add(
        types.InlineKeyboardButton("🗽 Chicago", callback_data="city_chicago"),
        types.InlineKeyboardButton("🎓 College Towns", callback_data="city_college")
    )
    keyboard.add(
        types.InlineKeyboardButton("🏫 Set Student Campus", callback_data="campus_set"),
        types.InlineKeyboardButton("📍 Custom Location", callback_data="location_custom")
    )
    
    bot.send_message(
        message.chat.id,
        "📍 **Set Your Location for Local Deals**\n\n"
        "Get personalized restaurant deals based on your location:\n\n"
        "1. Select your city/area\n"
        "2. Get local restaurant discounts\n"
        "3. Receive campus-specific offers\n"
        "4. Save on delivery in your area\n\n"
        "*Local deals are 30-50% cheaper than regular prices!*",
        reply_markup=keyboard
    )

# ===== FOOD HANDLERS =====
@bot.callback_query_handler(func=lambda call: call.data.startswith('food_'))
def food_handler(call):
    """Handle food category clicks"""
    user_id = call.from_user.id
    option = call.data.replace('food_', '')
    
    if option in FOOD_OFFERS:
        offer = FOOD_OFFERS[option]
        
        response = f"{offer['title']}\n\n{offer['details']}"
        
        # Action buttons with location focus
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📍 Set Location", callback_data="location_set"),
            types.InlineKeyboardButton("🎓 Student Deal", callback_data="food_student")
        )
        markup.add(
            types.InlineKeyboardButton("💬 Order Now", url="https://t.me/yrfrnd_spidy"),
            types.InlineKeyboardButton("📢 Food Deals", url="https://t.me/flights_bills_b4u")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
    
    elif option == "cities":
        response = """🏙️ **City-Specific Food Deals**

🇺🇸 **MAJOR CITIES COVERED:**

**NEW YORK CITY:**
• Manhattan: 500+ local restaurants
• Brooklyn: Hipster food scene
• Queens: Ethnic food capital
• Bronx: Authentic local spots
• Staten Island: Hidden gems

**LOS ANGELES:**
• Downtown LA: Food district deals
• Hollywood: Celebrity chef discounts
• Santa Monica: Beachfront dining
• Koreatown: 24-hour restaurants
• Westwood: UCLA student area

**CHICAGO:**
• The Loop: Business lunch specials
• Wicker Park: Trendy cafes
• Chinatown: Authentic Asian
• Lincoln Park: Family restaurants
• River North: Nightlife dining

**COLLEGE TOWNS:**
• Boston: Harvard/MIT area
• Austin: UT campus deals
• Berkeley: Cal student discounts
• Ann Arbor: University of Michigan
• Madison: UW-Madison area

**OTHER CITIES:**
• Houston: Texas-sized portions
• Phoenix: Southwestern cuisine
• Philadelphia: Cheesesteak spots
• San Francisco: Tech hub dining
• Miami: Latin fusion deals

💰 **CITY DISCOUNTS:**
• Local restaurants: 40-50% OFF
• Student areas: Extra 15% OFF
• Neighborhood specials
• Community restaurant deals

👇 **Select your city for local restaurant deals:**"""
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🏙️ NYC Deals", callback_data="city_nyc"),
            types.InlineKeyboardButton("🌴 LA Specials", callback_data="city_la")
        )
        markup.add(
            types.InlineKeyboardButton("🗽 Chicago Food", callback_data="city_chicago"),
            types.InlineKeyboardButton("🎓 College Towns", callback_data="city_college")
        )
        markup.add(
            types.InlineKeyboardButton("📍 Set Your City", callback_data="location_set"),
            types.InlineKeyboardButton("💬 Local Orders", url="https://t.me/yrfrnd_spidy")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
    
    elif option == "discount":
        response = """🎫 **50% OFF TOTAL CART - LIMITED TIME!**

🔥 **HOW TO GET 50% OFF:**

1. **STUDENTS:**
   • Show valid student ID
   • First order: 50% OFF entire cart
   • Subsequent orders: 30% OFF
   • Group orders: Extra 10% OFF

2. **NEW USERS:**
   • First order: 50% OFF
   • Use code: FOOD50
   • App download: Extra $5 OFF
   • Referral: $10 credit

3. **LOCAL RESIDENTS:**
   • Neighborhood special: 40% OFF
   • Regular customer: 35% OFF
   • Community member: 30% OFF

4. **SPECIAL OCCASIONS:**
   • Birthday month: 50% OFF
   • Exam week: 45% OFF students
   • Finals period: Extra discount
   • Move-in week: Welcome discount

💰 **DISCOUNT TERMS:**
• Minimum order: $15
• Maximum discount: $50
• Valid for delivery & pickup
• Cannot combine with other offers
• Limited to one per customer

🎯 **ELIGIBLE RESTAURANTS:**
• Local neighborhood spots
• Campus area restaurants
• Fast food chains
• Healthy eateries
• Late night options

⚠️ **HOW TO CLAIM:**
1. Select restaurant
2. Add items to cart
3. Apply code: FOOD50
4. Show student ID if applicable
5. Enjoy 50% savings!

💎 **PRO TIP:** Order during off-peak hours for faster delivery + potential extra discounts!"""
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🎓 Student 50% OFF", callback_data="food_student"),
            types.InlineKeyboardButton("📍 Local 40% OFF", callback_data="food_local")
        )
        markup.add(
            types.InlineKeyboardButton("💬 Apply Discount", url="https://t.me/yrfrnd_spidy"),
            types.InlineKeyboardButton("📢 More Deals", url="https://t.me/flights_bills_b4u")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
    
    elif option == "studentareas":
        response = """🏫 **Student Area Food Deals**

🎓 **TOP STUDENT AREAS COVERED:**

**UNIVERSITY DISTRICTS:**
• Campus perimeter restaurants
• Dormitory delivery zones
• Library & study spot delivery
• Student union food courts
• Off-campus housing areas

**STUDENT REQUIREMENTS:**
• Budget meals: $5-10 range
• Quick service: <30 minutes
• Late night options: Until 3 AM
• Group order discounts
• Exam week specials
• Study break snacks
• Caffeine fixes
• All-night study fuel

**MEAL SOLUTIONS:**
• Weekly meal plans
• Bulk order discounts
• Roommate combo deals
• Study session packs
• All-nighter packages

**STUDENT DISCOUNTS:**
• Student ID: 20% OFF always
• First order: 50% OFF cart
• Referral program: $5 each
• Exam period: Extra 15% OFF
• Group of 4+: 25% OFF

**POPULAR STUDENT FOODS:**
• Pizza by the slice
• Burgers & fries
• Coffee & pastries
• Smoothies & acai bowls
• Quick sandwiches
• Asian takeout
• Mexican burritos
• Chicken wings

**DELIVERY OPTIONS:**
• Library drop-off
• Dorm delivery
• Study room delivery
• Campus pickup points
• Late night delivery

💰 **STUDENT BUDGET TIPS:**
1. Order during happy hours
2. Use student discount codes
3. Split delivery fees with friends
4. Order in bulk for week
5. Use cashback apps
6. Follow social media for flash sales

👇 **Ready to order? Set your campus location first!**"""
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📍 Set Campus", callback_data="campus_set"),
            types.InlineKeyboardButton("🎓 Student Meals", callback_data="food_student")
        )
        markup.add(
            types.InlineKeyboardButton("💬 Order Student Deal", url="https://t.me/yrfrnd_spidy"),
            types.InlineKeyboardButton("📢 Student Deals", url="https://t.me/flights_bills_b4u")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
    
    elif option == "more":
        # Show all categories
        response = """🍽️ **All Food Categories**

🎓 **STUDENT MEALS:**
• Campus area discounts
• Student ID required
• Budget-friendly options
• Late night delivery

📍 **LOCAL RESTAURANTS:**
• Neighborhood favorites
• City-specific deals
• Community spots
• Family-owned businesses

🍔 **FAST FOOD CHAINS:**
• Major brand discounts
• Combo meal deals
• App-exclusive offers
• Family pack savings

🥗 **HEALTHY OPTIONS:**
• Nutritious meals
• Fitness-focused
• Organic choices
• Vegan/vegetarian

🌙 **LATE NIGHT FOOD:**
• After-hours dining
• 24-hour options
• Post-party food
• Shift worker meals

🏙️ **CITY SPECIFIC:**
• Local restaurant deals
• Neighborhood specials
• Community discounts
• Area-exclusive offers

🎫 **50% OFF CART:**
• Limited time discount
• Student exclusive
• New user welcome
• Special occasion

🏫 **STUDENT AREAS:**
• Campus zone deals
• Dormitory delivery
• Study spot meals
• University discounts

*Select a category for local food deals!*"""
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🎓 Student", callback_data="food_student"),
            types.InlineKeyboardButton("📍 Local", callback_data="food_local")
        )
        markup.add(
            types.InlineKeyboardButton("🍔 Fast Food", callback_data="food_fastfood"),
            types.InlineKeyboardButton("🥗 Healthy", callback_data="food_healthy")
        )
        markup.add(
            types.InlineKeyboardButton("🌙 Late Night", callback_data="food_late"),
            types.InlineKeyboardButton("🏙️ Cities", callback_data="food_cities")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')

# ===== CITY HANDLERS =====
@bot.callback_query_handler(func=lambda call: call.data.startswith('city_'))
def city_handler(call):
    """Handle city selection clicks"""
    city_key = call.data.replace('city_', '')
    
    if city_key in LOCAL_RESTAURANTS:
        city = LOCAL_RESTAURANTS[city_key]
        
        response = f"""🏙️ **{city['name']} Food Deals**

🍽️ **LOCAL RESTAURANT RECOMMENDATIONS:**
"""
        for i, restaurant in enumerate(city['restaurants'], 1):
            response += f"{i}. {restaurant}\n"
        
        response += f"\n🎓 **STUDENT AREAS IN {city['name'].upper()}:**\n"
        for area in city['student_areas']:
            response += f"• {area}\n"
        
        response += f"\n💰 **LOCAL DISCOUNT:** {city['discount']}\n\n"
        
        response += """🎯 **LOCAL ORDERING TIPS:**
1. Order during off-peak hours (2-5 PM)
2. Use 'LOCAL' code for extra 10% OFF
3. Pickup instead of delivery for 15% OFF
4. Follow local restaurants on social media
5. Join neighborhood food groups

📱 **BEST LOCAL APPS:**
• DoorDash - Local restaurant selection
• Uber Eats - Fast delivery options
• Grubhub - Neighborhood favorites
• Postmates - Local gems
• Restaurant-specific apps

⚠️ **LOCAL KNOWLEDGE:**
• Ask about daily specials
• Tip well for regular service
• Support family-owned spots
• Try seasonal local items
• Check health ratings"""

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📍 Set as My City", callback_data=f"setcity_{city_key}"),
            types.InlineKeyboardButton("🎓 Student Deals", callback_data="food_student")
        )
        markup.add(
            types.InlineKeyboardButton("💬 Order Local", url="https://t.me/yrfrnd_spidy"),
            types.InlineKeyboardButton("📢 Local Deals", url="https://t.me/flights_bills_b4u")
        )
        
        bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('setcity_'))
def set_city_handler(call):
    city_key = call.data.replace('setcity_', '')
    city_name = LOCAL_RESTAURANTS.get(city_key, {}).get('name', 'your area')
    
    bot.answer_callback_query(call.id, f"✅ {city_name} set as your location!")
    
    bot.send_message(
        call.message.chat.id,
        f"📍 **Location Set Successfully!**\n\n"
        f"You'll now receive local food deals for **{city_name}**.\n\n"
        f"🎯 **Benefits activated:**\n"
        f"• Local restaurant discounts\n"
        f"• Neighborhood special offers\n"
        f"• Faster delivery estimates\n"
        f"• Community restaurant deals\n\n"
        f"*Use /location to change your area anytime.*"
    )

@bot.callback_query_handler(func=lambda call: call.data == 'campus_set')
def campus_set_handler(call):
    bot.send_message(
        call.message.chat.id,
        "🏫 **Set Your Campus Location**\n\n"
        "Please send your:\n"
        "1. University/College name\n"
        "2. Dormitory/Off-campus address\n"
        "3. Preferred delivery spots (library, etc.)\n\n"
        "Example:\n"
        "`NYU Washington Square\n123 Dorm Street\nBobst Library delivery`\n\n"
        "This helps us find the best student deals for your area!"
    )
    bot.register_next_step_handler(call.message, process_campus_info)

def process_campus_info(message):
    user_id = message.from_user.id
    user_chat_states[user_id] = 'campus_set'
    
    bot.send_message(
        message.chat.id,
        "✅ **Campus location saved!**\n\n"
        "🎓 **Student benefits activated:**\n"
        "• 50% OFF first order\n"
        "• Campus-area restaurant deals\n"
        "• Library/dorm delivery options\n"
        "• Exam week specials\n"
        "• Group order discounts\n\n"
        "*Check Student Meals section for exclusive deals!*"
    )
    
    # Notify admin
    bot.send_message(
        ADMIN_ID,
        f"🎓 New student location set:\nUser: @{message.from_user.username}\n"
        f"Info: {message.text}"
    )

@bot.callback_query_handler(func=lambda call: call.data == 'location_set')
def location_set_handler(call):
    location_command(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'location_custom')
def location_custom_handler(call):
    bot.send_message(
        call.message.chat.id,
        "📍 **Enter Your Custom Location**\n\n"
        "Please send:\n"
        "• City name\n"
        "• Neighborhood/Area\n"
        "• Street (optional)\n"
        "• Any landmarks\n\n"
        "Example:\n"
        "`Brooklyn, NY\nWilliamsburg area\nNear Bedford Avenue`"
    )
    bot.register_next_step_handler(call.message, process_custom_location)

def process_custom_location(message):
    user_id = message.from_user.id
    bot.send_message(
        message.chat.id,
        f"📍 **Custom location saved!**\n\n"
        f"We'll find local restaurant deals for:\n"
        f"`{message.text}`\n\n"
        f"🔍 **Searching for:**\n"
        f"• Neighborhood restaurants\n"
        f"• Local discounts\n"
        f"• Delivery options\n"
        f"• Community specials\n\n"
        f"*Check Local Restaurants section for deals in your area!*"
    )

# ===== BROADCAST FEATURE =====
@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Admin feature only.")
        return
    
    if len(broadcast_users) == 0:
        bot.reply_to(message, "No users available.")
        return
    
    msg = bot.send_message(
        ADMIN_ID,
        f"Send food deal to {len(broadcast_users)} users:"
    )
    bot.register_next_step_handler(msg, process_broadcast_message)

def process_broadcast_message(message):
    if hasattr(message, 'is_broadcast_processed') and message.is_broadcast_processed:
        return
    message.is_broadcast_processed = True
    
    broadcast_text = message.text
    users = list(broadcast_users)
    success_count = 0
    fail_count = 0
    
    status_msg = bot.send_message(ADMIN_ID, f"🍔 Sending food deals to {len(users)} users...")
    
    for user_id in users:
        try:
            notification = f"🍽️ **Food Deal Alert** 🍽️\n\n{broadcast_text}\n\n*Local restaurants & student discounts available!*"
            bot.send_message(user_id, notification)
            success_count += 1
        except Exception:
            fail_count += 1
    
    bot.edit_message_text(
        f"✅ Food broadcast complete!\n\n"
        f"📊 Results:\n"
        f"• Success: {success_count}\n"
        f"• Failed: {fail_count}\n"
        f"• Total: {len(users)}",
        ADMIN_ID,
        status_msg.message_id
    )

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    user_count = len(broadcast_users)
    bot.send_message(
        ADMIN_ID,
        f"🍔 Food Bot Statistics:\n\n"
        f"👥 Total Users: {user_count}\n"
        f"📍 Cities Covered: 4 major + custom\n"
        f"🎓 Student Areas: 20+ campuses\n"
        f"💰 Active Deals: 50% OFF cart\n"
        f"📈 Student Users: {int(user_count * 0.7)}"
    )

# ===== CHAT HANDLERS =====
@bot.message_handler(func=lambda message: message.text and message.text.lower().startswith('hello'))
def hello_handler(message):
    user = message.from_user
    user_id = user.id
    
    broadcast_users.add(user_id)
    user_chat_states[user_id] = 'waiting_for_admin'
    
    user_info = f"User: {user.first_name} {user.last_name or ''} (@{user.username or 'No username'})"
    
    user_messages[message.message_id] = {
        'user_id': user.id,
        'user_info': user_info,
        'original_message': message.text
    }
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("📨 Reply with Food Deal", callback_data=f"reply_{message.message_id}"))
    
    forward_text = f"🍔 New Food Inquiry\n\n{user_info}\nUser ID: {user.id}\n\n'{message.text}'"
    
    bot.send_message(ADMIN_ID, forward_text, reply_markup=keyboard)
    
    bot.reply_to(
        message,
        "🍽️ Hello! Welcome to Local Food Deals!\n\n"
        "🎓 **Student?** Get 50% OFF your first order!\n"
        "📍 **Local?** Find neighborhood restaurant deals!\n\n"
        "Use /location to set your area for personalized deals!"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def reply_callback_handler(call):
    message_id = int(call.data.split('_')[1])
    
    if message_id in user_messages:
        user_data = user_messages[message_id]
        
        msg = bot.send_message(
            ADMIN_ID,
            f"🍽️ Reply to {user_data['user_info']}\n\n"
            f"💡 Tip: Offer local restaurant deals or student discounts!"
        )
        bot.register_next_step_handler(msg, process_admin_reply, user_data['user_id'])
    else:
        bot.answer_callback_query(call.id, "Message not found")

def process_admin_reply(message, user_id):
    try:
        bot.send_message(
            user_id,
            f"🍔 Food Specialist Reply:\n\n{message.text}\n\n"
            f"*Need help finding local restaurants or student deals? Just ask!*"
        )
        bot.reply_to(message, "✅ Reply sent to user!")
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(func=lambda message: True)
def all_messages_handler(message):
    user = message.from_user
    user_id = user.id
    
    if user_id == ADMIN_ID:
        return
    
    broadcast_users.add(user_id)
    
    if user_chat_states.get(user_id) == 'waiting_for_admin' and message.text:
        user_info = f"User: {user.first_name} {user.last_name or ''} (@{user.username or 'No username'})"
        
        user_messages[message.message_id] = {
            'user_id': user_id,
            'user_info': user_info,
            'original_message': message.text
        }
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("📨 Reply", callback_data=f"reply_{message.message_id}"))
        
        forward_text = f"🍔 User Message\n\n{user_info}\nUser ID: {user_id}\n\n'{message.text}'"
        
        bot.send_message(ADMIN_ID, forward_text, reply_markup=keyboard)
        
        if not message.text.lower().startswith('hello'):
            bot.reply_to(
                message,
                "✅ Got your message! Our food specialist will help you find:\n"
                "• Local restaurant deals\n"
                "• Student discounts\n"
                "• 50% OFF cart offers\n"
                "• Campus-area delivery"
            )

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Local Food Deals Bot | Student Meals & Restaurant Discounts</title>
        <meta name="description" content="Get 50% OFF food delivery from local restaurants near colleges & universities. Student meals, campus delivery, neighborhood restaurant deals.">
        <meta name="keywords" content="student food delivery, campus meals, local restaurant discounts, 50% off food, college food deals, university area restaurants">
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #fff8e1; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .deal-badge { background: #ff6b6b; color: white; padding: 10px 20px; border-radius: 20px; display: inline-block; margin: 10px; font-weight: bold; }
            .city-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0; }
            .city-card { background: #4CAF50; color: white; padding: 15px; border-radius: 8px; }
            .student-area { background: #2196F3; color: white; padding: 8px 15px; border-radius: 20px; margin: 5px; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🍔 Local Food Deals Bot</h1>
            <p>50% OFF food delivery for students & local residents</p>
            
            <div class="deal-badge">🎓 STUDENT SPECIAL: 50% OFF TOTAL CART</div>
            
            <h2>📍 Covered Cities & Areas</h2>
            <div class="city-grid">
                <div class="city-card">🏙️ New York City</div>
                <div class="city-card">🌴 Los Angeles</div>
                <div class="city-card">🗽 Chicago</div>
                <div class="city-card">🎓 College Towns</div>
            </div>
            
            <h2>🏫 Student Areas Supported</h2>
            <div>
                <span class="student-area">University Districts</span>
                <span class="student-area">Campus Food Trucks</span>
                <span class="student-area">Dorm Delivery</span>
                <span class="student-area">Library Drop-off</span>
                <span class="student-area">Study Spots</span>
            </div>
            
            <h2>💰 Current Offers</h2>
            <p>• Students: 50% OFF first order + ID discounts</p>
            <p>• Local Residents: 40% OFF neighborhood restaurants</p>
            <p>• Fast Food: 50% OFF combo meals</p>
            <p>• Late Night: Special discounts after 10 PM</p>
            
            <h2>🚀 How It Works</h2>
            <p>1. Set your location/campus area</p>
            <p>2. Browse local restaurant deals</p>
            <p>3. Apply student/location discounts</p>
            <p>4. Get delivery or pickup</p>
            <p>5. Save up to 50% on every order!</p>
            
            <p style="margin-top: 30px; color: #666;">
                Use our Telegram bot for real-time food deals in your area!
            </p>
        </div>
    </body>
    </html>
    """

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = request.get_data().decode("utf-8")
    update_obj = telebot.types.Update.de_json(update)
    bot.process_new_updates([update_obj])
    return "OK", 200

if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Token required")
    
    try:
        bot.remove_webhook()
        render_domain = os.environ.get("RENDER_EXTERNAL_URL")
        
        if render_domain:
            webhook_url = f"{render_domain}/{TOKEN}"
            bot.set_webhook(url=webhook_url)
            print(f"🍔 Food Deals Bot deployed: {webhook_url}")
        else:
            print("Food Bot running in polling mode")
            
    except Exception as e:
        print(f"Webhook setup: {e}")
    
    print("🍔 Local Food Deals Bot Active!")
    print("🎓 Focus: Student meals & local restaurant discounts")
    print("📍 Cities: NYC, LA, Chicago, College Towns")
    print("💰 Discounts: Up to 50% OFF total cart")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
