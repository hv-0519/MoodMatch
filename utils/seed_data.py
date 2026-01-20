# utils/seed_data.py

def get_seed_data():
    '''Return seed data for activities table'''
    return [
        # ===== CREATIVE MOODS =====
        # Writing
        ('Short Story Writing', 'Creative', 'writing', '2h', 'None', 'Medium', 'Indoor', 'Home', 'Write a creative short story'),
        ('Poetry Composition', 'Creative', 'writing', '1h', 'None', 'Low', 'Indoor', 'Home', 'Express yourself through poetry'),
        ('Blog Article Writing', 'Creative', 'writing', '2h', 'None', 'Medium', 'Indoor', 'Home', 'Share your thoughts online'),
        ('Novel Writing Session', 'Creative', 'writing', '4h', 'None', 'High', 'Indoor', 'Home', 'Work on your novel'),
        ('Screenwriting', 'Creative', 'writing', 'full_day', 'None', 'High', 'Indoor', 'Home', 'Write a screenplay'),
        
        # Drawing/Art
        ('Watercolor Painting', 'Creative', 'drawing', '2h', 'low', 'Medium', 'Indoor', 'Home', 'Create beautiful watercolor art'),
        ('Digital Art Creation', 'Creative', 'drawing', '4h', 'medium', 'Medium', 'Indoor', 'Home', 'Design digital artwork'),
        ('Sketching Practice', 'Creative', 'drawing', '1h', 'None', 'Low', 'Indoor', 'Home', 'Improve your drawing skills'),
        ('Portrait Drawing', 'Creative', 'drawing', '2h', 'None', 'Medium', 'Indoor', 'Home', 'Draw realistic portraits'),
        ('Oil Painting', 'Creative', 'drawing', '4h', 'medium', 'Medium', 'Indoor', 'Home', 'Traditional oil painting'),
        ('Acrylic Art', 'Creative', 'drawing', '2h', 'low', 'Medium', 'Indoor', 'Home', 'Vibrant acrylic paintings'),
        
        # Music
        ('Music Composition', 'Creative', 'music', '2h', 'low', 'Medium', 'Indoor', 'Home', 'Compose your own music'),
        ('Learn Guitar Chords', 'Creative', 'music', '1h', 'medium', 'Low', 'Indoor', 'Home', 'Practice guitar'),
        ('Piano Practice', 'Creative', 'music', '2h', 'None', 'Low', 'Indoor', 'Home', 'Improve piano skills'),
        ('Songwriting', 'Creative', 'music', '4h', 'None', 'Medium', 'Indoor', 'Home', 'Write your own songs'),
        ('Music Production', 'Creative', 'music', '4h', 'high', 'High', 'Indoor', 'Home', 'Produce electronic music'),
        
        # Photography
        ('Street Photography', 'Creative', 'photography', '2h', 'None', 'High', 'Outdoor', 'Short', 'Capture urban moments'),
        ('Nature Photography', 'Creative', 'photography', '4h', 'low', 'High', 'Outdoor', 'Long', 'Photograph landscapes'),
        ('Portrait Photography', 'Creative', 'photography', '2h', 'low', 'Medium', 'Indoor', 'Short', 'Capture people'),
        ('Product Photography', 'Creative', 'photography', '2h', 'medium', 'Medium', 'Indoor', 'Home', 'Professional product shots'),
        ('Wildlife Photography', 'Creative', 'photography', 'full_day', 'high', 'High', 'Outdoor', 'Long', 'Capture wildlife'),
        
        # Video Editing
        ('Video Vlog Editing', 'Creative', 'video_editing', '4h', 'None', 'Medium', 'Indoor', 'Home', 'Edit your video content'),
        ('Short Film Production', 'Creative', 'video_editing', 'full_day', 'medium', 'High', 'Outdoor', 'Short', 'Create a short film'),
        ('YouTube Video Editing', 'Creative', 'video_editing', '2h', 'None', 'Medium', 'Indoor', 'Home', 'Edit for YouTube'),
        ('Wedding Video Editing', 'Creative', 'video_editing', 'full_day', 'None', 'High', 'Indoor', 'Home', 'Professional wedding videos'),
        
        # Designing
        ('Graphic Design Project', 'Creative', 'designing', '4h', 'low', 'Medium', 'Indoor', 'Home', 'Create stunning graphics'),
        ('Logo Design', 'Creative', 'designing', '2h', 'None', 'Medium', 'Indoor', 'Home', 'Design a professional logo'),
        ('UI/UX Design', 'Creative', 'designing', '4h', 'None', 'High', 'Indoor', 'Home', 'Design user interfaces'),
        ('Poster Design', 'Creative', 'designing', '2h', 'None', 'Medium', 'Indoor', 'Home', 'Create eye-catching posters'),
        ('Web Design', 'Creative', 'designing', 'full_day', 'None', 'High', 'Indoor', 'Home', 'Design beautiful websites'),
        
        # Journaling
        ('Bullet Journaling', 'Creative', 'journaling', '1h', 'low', 'Low', 'Indoor', 'Home', 'Organize your thoughts creatively'),
        ('Gratitude Journal', 'Creative', 'journaling', '1h', 'None', 'Low', 'Indoor', 'Home', 'Practice daily gratitude'),
        ('Travel Journal', 'Creative', 'journaling', '1h', 'low', 'Low', 'Indoor', 'Home', 'Document your travels'),
        ('Dream Journal', 'Creative', 'journaling', '1h', 'None', 'Low', 'Indoor', 'Home', 'Record your dreams'),
        
        # DIY Crafts
        ('Handmade Greeting Cards', 'Creative', 'diy_crafts', '2h', 'low', 'Medium', 'Indoor', 'Home', 'Craft personalized cards'),
        ('Origami Art', 'Creative', 'diy_crafts', '1h', 'None', 'Low', 'Indoor', 'Home', 'Paper folding art'),
        ('Knitting Project', 'Creative', 'diy_crafts', '4h', 'low', 'Low', 'Indoor', 'Home', 'Create knitted items'),
        ('Scrapbooking', 'Creative', 'diy_crafts', '2h', 'low', 'Low', 'Indoor', 'Home', 'Preserve memories creatively'),
        ('Candle Making', 'Creative', 'diy_crafts', '2h', 'low', 'Medium', 'Indoor', 'Home', 'Create custom candles'),
        ('Jewelry Making', 'Creative', 'diy_crafts', '2h', 'medium', 'Medium', 'Indoor', 'Home', 'Craft unique jewelry'),
        
        # ===== INTELLECTUAL / LEARNING MOODS =====
        # Reading
        ('Read a Novel', 'Intellectual', 'reading', '2h', 'None', 'Low', 'Indoor', 'Home', 'Immerse in a good book'),
        ('Read Non-Fiction', 'Intellectual', 'reading', '2h', 'low', 'Medium', 'Indoor', 'Home', 'Learn something new'),
        ('Visit Local Library', 'Intellectual', 'reading', '2h', 'None', 'Low', 'Indoor', 'Short', 'Explore new books at library'),
        ('Book Club Meeting', 'Intellectual', 'reading', '2h', 'None', 'Medium', 'Indoor', 'Short', 'Discuss books with others'),
        ('Poetry Reading', 'Intellectual', 'reading', '1h', 'None', 'Low', 'Indoor', 'Home', 'Enjoy poetry collections'),
        
        # Research
        ('Research Project', 'Intellectual', 'research', 'full_day', 'None', 'High', 'Indoor', 'Home', 'Deep dive into a topic'),
        ('Academic Paper Reading', 'Intellectual', 'research', '2h', 'None', 'High', 'Indoor', 'Home', 'Study research papers'),
        ('Historical Research', 'Intellectual', 'research', '4h', 'None', 'Medium', 'Indoor', 'Home', 'Explore history'),
        ('Scientific Research', 'Intellectual', 'research', '4h', 'None', 'High', 'Indoor', 'Home', 'Study scientific topics'),
        
        # Learning
        ('Online Course: Python', 'Intellectual', 'learning', '4h', 'None', 'Medium', 'Indoor', 'Home', 'Learn programming'),
        ('Language Learning App', 'Intellectual', 'learning', '1h', 'None', 'Low', 'Indoor', 'Home', 'Practice new language'),
        ('Skill Development Workshop', 'Intellectual', 'learning', 'full_day', 'medium', 'Medium', 'Indoor', 'Short', 'Attend workshop'),
        ('Online Certification Course', 'Intellectual', 'learning', 'weekend', 'medium', 'High', 'Indoor', 'Home', 'Earn certification'),
        ('Master Class', 'Intellectual', 'learning', '4h', 'high', 'Medium', 'Indoor', 'Home', 'Learn from experts'),
        
        # Tutorials
        ('Tutorial: Adobe Photoshop', 'Intellectual', 'tutorials', '2h', 'None', 'Medium', 'Indoor', 'Home', 'Master new software'),
        ('Coding Tutorial', 'Intellectual', 'tutorials', '4h', 'None', 'Medium', 'Indoor', 'Home', 'Learn to code'),
        ('Video Editing Tutorial', 'Intellectual', 'tutorials', '2h', 'None', 'Medium', 'Indoor', 'Home', 'Learn video editing'),
        ('3D Modeling Tutorial', 'Intellectual', 'tutorials', '4h', 'None', 'High', 'Indoor', 'Home', 'Learn 3D design'),
        
        # Documentaries
        ('Watch Documentary', 'Intellectual', 'documentaries', '2h', 'None', 'Low', 'Indoor', 'Home', 'Educational content'),
        ('Science Documentary Series', 'Intellectual', 'documentaries', '4h', 'None', 'Low', 'Indoor', 'Home', 'Deep dive into science'),
        ('Nature Documentary', 'Intellectual', 'documentaries', '2h', 'None', 'Low', 'Indoor', 'Home', 'Explore nature'),
        ('Historical Documentary', 'Intellectual', 'documentaries', '2h', 'None', 'Low', 'Indoor', 'Home', 'Learn about history'),
        
        # ===== GAMING & DIGITAL ENTERTAINMENT =====
        # Mobile Games
        ('Mobile Puzzle Games', 'Gaming', 'mobile_games', '1h', 'None', 'Low', 'Indoor', 'Home', 'Casual gaming session'),
        ('Strategy Mobile Games', 'Gaming', 'mobile_games', '2h', 'None', 'Medium', 'Indoor', 'Home', 'Tactical gameplay'),
        ('Action Mobile Games', 'Gaming', 'mobile_games', '1h', 'None', 'Low', 'Indoor', 'Home', 'Fast-paced action'),
        ('RPG Mobile Games', 'Gaming', 'mobile_games', '4h', 'None', 'Low', 'Indoor', 'Home', 'Role-playing adventures'),
        
        # PC Games
        ('PC Strategy Game', 'Gaming', 'pc_games', '4h', 'medium', 'Medium', 'Indoor', 'Home', 'Immersive gaming experience'),
        ('RPG Adventure', 'Gaming', 'pc_games', 'full_day', 'high', 'Low', 'Indoor', 'Home', 'Story-driven gameplay'),
        ('First-Person Shooter', 'Gaming', 'pc_games', '2h', 'high', 'Medium', 'Indoor', 'Home', 'Competitive FPS'),
        ('Simulation Games', 'Gaming', 'pc_games', '4h', 'medium', 'Low', 'Indoor', 'Home', 'Build and manage'),
        
        # Brain Games
        ('Chess Online', 'Gaming', 'brain_games', '1h', 'None', 'Medium', 'Indoor', 'Home', 'Strategic thinking game'),
        ('Memory Training Games', 'Gaming', 'brain_games', '1h', 'None', 'Low', 'Indoor', 'Home', 'Improve memory'),
        ('Logic Puzzles', 'Gaming', 'brain_games', '1h', 'None', 'Medium', 'Indoor', 'Home', 'Solve logical problems'),
        ('Trivia Games', 'Gaming', 'brain_games', '1h', 'None', 'Low', 'Indoor', 'Home', 'Test your knowledge'),
        
        # Puzzles
        ('Sudoku Challenge', 'Gaming', 'puzzles', '1h', 'None', 'Low', 'Indoor', 'Home', 'Number puzzle solving'),
        ('Crossword Puzzles', 'Gaming', 'puzzles', '1h', 'None', 'Low', 'Indoor', 'Home', 'Word puzzles'),
        ('Jigsaw Puzzles', 'Gaming', 'puzzles', '2h', 'low', 'Low', 'Indoor', 'Home', 'Physical puzzle assembly'),
        ("Rubik\\'s Cube", 'Gaming', 'puzzles', '1h', 'low', 'Medium', 'Indoor', 'Home', 'Solve the cube'),
        
        # Board Games
        ('Board Game Night', 'Gaming', 'board_games', '2h', 'low', 'Medium', 'Indoor', 'Home', 'Social board gaming'),
        ('Strategy Board Games', 'Gaming', 'board_games', '4h', 'medium', 'Medium', 'Indoor', 'Home', 'Complex board games'),
        ('Card Games', 'Gaming', 'board_games', '1h', 'None', 'Low', 'Indoor', 'Home', 'Classic card games'),
        ('Tabletop RPG', 'Gaming', 'board_games', '4h', 'low', 'Medium', 'Indoor', 'Home', 'Dungeons & Dragons'),
        
        # ===== PHYSICAL & ADVENTURE =====
        # Hiking/Running
        ('Morning Jog', 'Physical', 'hiking', '1h', 'None', 'High', 'Outdoor', 'Short', 'Cardio workout outdoors'),
        ('Trail Running', 'Physical', 'hiking', '2h', 'None', 'High', 'Outdoor', 'Short', 'Nature running'),
        ('Mountain Hiking', 'Physical', 'hiking', 'full_day', 'low', 'High', 'Outdoor', 'Long', 'Challenging trail adventure'),
        ('Nature Walk', 'Physical', 'hiking', '2h', 'None', 'Low', 'Outdoor', 'Short', 'Peaceful nature walk'),
        ('Forest Trail', 'Physical', 'hiking', '4h', 'None', 'Medium', 'Outdoor', 'Long', 'Explore forest trails'),
        
        # Cycling
        ('City Cycling', 'Physical', 'cycling', '2h', 'None', 'High', 'Outdoor', 'Short', 'Explore city on bike'),
        ('Mountain Biking', 'Physical', 'cycling', '4h', 'medium', 'High', 'Outdoor', 'Long', 'Off-road cycling'),
        ('Bike Tour', 'Physical', 'cycling', 'full_day', 'low', 'High', 'Outdoor', 'Long', 'Long-distance cycling'),
        ('Spin Class', 'Physical', 'cycling', '1h', 'medium', 'High', 'Indoor', 'Short', 'Indoor cycling workout'),
        
        # Gym
        ('Gym Workout', 'Physical', 'gym', '2h', 'medium', 'High', 'Indoor', 'Short', 'Strength training session'),
        ('CrossFit Class', 'Physical', 'gym', '1h', 'high', 'High', 'Indoor', 'Short', 'Intense workout'),
        ('Weightlifting', 'Physical', 'gym', '2h', 'medium', 'High', 'Indoor', 'Short', 'Build muscle mass'),
        ('Cardio Session', 'Physical', 'gym', '1h', 'medium', 'High', 'Indoor', 'Short', 'Heart-pumping cardio'),
        
        # Dance/Yoga
        ('Yoga Class', 'Physical', 'dance', '1h', 'low', 'Medium', 'Indoor', 'Short', 'Mindful movement'),
        ('Zumba Dance', 'Physical', 'dance', '1h', 'low', 'High', 'Indoor', 'Short', 'Dance fitness'),
        ('Ballet Class', 'Physical', 'dance', '2h', 'medium', 'Medium', 'Indoor', 'Short', 'Classical dance'),
        ('Hip Hop Dance', 'Physical', 'dance', '1h', 'low', 'High', 'Indoor', 'Short', 'Urban dance style'),
        ('Pilates', 'Physical', 'dance', '1h', 'medium', 'Medium', 'Indoor', 'Short', 'Core strengthening'),
        
        # Sports
        ('Basketball Game', 'Physical', 'sports', '2h', 'None', 'High', 'Outdoor', 'Short', 'Team sport activity'),
        ('Tennis Match', 'Physical', 'sports', '2h', 'low', 'High', 'Outdoor', 'Short', 'Individual sport'),
        ('Soccer Practice', 'Physical', 'sports', '2h', 'None', 'High', 'Outdoor', 'Short', 'Team football'),
        ('Badminton', 'Physical', 'sports', '1h', 'None', 'Medium', 'Indoor', 'Short', 'Indoor racket sport'),
        ('Swimming', 'Physical', 'sports', '1h', 'low', 'High', 'Indoor', 'Short', 'Full-body workout'),
        
        # Adventure Sports
        ('Rock Climbing', 'Physical', 'adventure_sports', '4h', 'high', 'High', 'Indoor', 'Short', 'Indoor climbing gym'),
        ('Kayaking', 'Physical', 'adventure_sports', '4h', 'medium', 'High', 'Outdoor', 'Long', 'Water adventure'),
        ('Zip Lining', 'Physical', 'adventure_sports', '4h', 'high', 'Medium', 'Outdoor', 'Long', 'Aerial adventure'),
        ('Paragliding', 'Physical', 'adventure_sports', 'full_day', 'high', 'Medium', 'Outdoor', 'Long', 'Sky adventure'),
        ('Scuba Diving', 'Physical', 'adventure_sports', 'full_day', 'high', 'High', 'Outdoor', 'Long', 'Underwater exploration'),
        
        # ===== TRAVEL & EXPLORATION =====
        # Short Range
        ('Visit Local Cafe', 'Travel', 'short_range', '2h', 'low', 'Low', 'Indoor', 'Short', 'Discover cozy cafes'),
        ('Museum Visit', 'Travel', 'short_range', '4h', 'low', 'Medium', 'Indoor', 'Short', 'Explore art and history'),
        ('Art Gallery Tour', 'Travel', 'short_range', '2h', 'None', 'Low', 'Indoor', 'Short', 'Contemporary art'),
        ('Farmers Market', 'Travel', 'short_range', '2h', 'low', 'Medium', 'Outdoor', 'Short', 'Local fresh produce'),
        ('Botanical Garden', 'Travel', 'short_range', '2h', 'low', 'Medium', 'Outdoor', 'Short', 'Nature in the city'),
        ('City Walking Tour', 'Travel', 'short_range', '4h', 'None', 'Medium', 'Outdoor', 'Short', 'Explore city landmarks'),
        ('Bookstore Browsing', 'Travel', 'short_range', '2h', 'low', 'Low', 'Indoor', 'Short', 'Discover new books'),
        ('Local Theatre Show', 'Travel', 'short_range', '4h', 'medium', 'Low', 'Indoor', 'Short', 'Live performance'),
        
        # Long Range
        ('Weekend Beach Trip', 'Travel', 'long_range', 'weekend', 'high', 'Medium', 'Outdoor', 'Long', 'Coastal getaway'),
        ('Historical Fort Visit', 'Travel', 'long_range', 'full_day', 'medium', 'Medium', 'Outdoor', 'Long', 'Explore heritage sites'),
        ('Mountain Resort', 'Travel', 'long_range', 'weekend', 'high', 'High', 'Outdoor', 'Long', 'Hill station retreat'),
        ('Road Trip Adventure', 'Travel', 'long_range', 'weekend', 'high', 'High', 'Outdoor', 'Long', 'Scenic drive exploration'),
        ('National Park Visit', 'Travel', 'long_range', 'full_day', 'medium', 'High', 'Outdoor', 'Long', 'Wildlife and nature'),
        ('Cultural City Tour', 'Travel', 'long_range', 'weekend', 'high', 'Medium', 'Outdoor', 'Long', 'Historic city exploration'),
        ('Wine Tasting Tour', 'Travel', 'long_range', 'full_day', 'high', 'Low', 'Outdoor', 'Long', 'Visit vineyards'),
        ('Temple Tour', 'Travel', 'long_range', 'full_day', 'low', 'Medium', 'Outdoor', 'Long', 'Spiritual journey'),
        
        # ===== LIFESTYLE & PRODUCTIVITY =====
        # Cooking
        ('Try New Recipe', 'Lifestyle', 'cooking', '2h', 'low', 'Medium', 'Indoor', 'Home', 'Cook a gourmet meal'),
        ('Baking Session', 'Lifestyle', 'cooking', '2h', 'low', 'Medium', 'Indoor', 'Home', 'Bake fresh bread or cookies'),
        ('Cooking Class', 'Lifestyle', 'cooking', '4h', 'medium', 'Medium', 'Indoor', 'Short', 'Learn new cuisine'),
        ('International Cuisine', 'Lifestyle', 'cooking', '2h', 'medium', 'Medium', 'Indoor', 'Home', 'Cook exotic dishes'),
        ('Barbecue Grilling', 'Lifestyle', 'cooking', '4h', 'medium', 'Medium', 'Outdoor', 'Home', 'Outdoor cooking'),
        
        # Gardening
        ('Garden Planting', 'Lifestyle', 'gardening', '2h', 'low', 'Medium', 'Outdoor', 'Home', 'Grow your own plants'),
        ('Vegetable Garden Setup', 'Lifestyle', 'gardening', '4h', 'medium', 'High', 'Outdoor', 'Home', 'Start veggie garden'),
        ('Flower Bed Design', 'Lifestyle', 'gardening', '2h', 'low', 'Medium', 'Outdoor', 'Home', 'Create flower garden'),
        ('Indoor Plants Care', 'Lifestyle', 'gardening', '1h', 'low', 'Low', 'Indoor', 'Home', 'Maintain houseplants'),
        ('Herb Garden', 'Lifestyle', 'gardening', '2h', 'low', 'Medium', 'Outdoor', 'Home', 'Grow fresh herbs'),
        
        # Self-care
        ('Spa Day at Home', 'Lifestyle', 'self_care', '2h', 'low', 'Low', 'Indoor', 'Home', 'Relaxation and rejuvenation'),
        ('Meditation Session', 'Lifestyle', 'self_care', '1h', 'None', 'Low', 'Indoor', 'Home', 'Mindfulness practice'),
        ('Bubble Bath', 'Lifestyle', 'self_care', '1h', 'low', 'Low', 'Indoor', 'Home', 'Relaxing bath'),
        ('Face Mask Treatment', 'Lifestyle', 'self_care', '1h', 'low', 'Low', 'Indoor', 'Home', 'Skincare routine'),
        ('Aromatherapy', 'Lifestyle', 'self_care', '1h', 'low', 'Low', 'Indoor', 'Home', 'Essential oils therapy'),
        
        # Cleaning/Organizing
        ('Home Organization', 'Lifestyle', 'cleaning', '4h', 'None', 'High', 'Indoor', 'Home', 'Declutter and organize'),
        ('Deep Cleaning', 'Lifestyle', 'cleaning', 'full_day', 'low', 'High', 'Indoor', 'Home', 'Thorough house cleaning'),
        ('Closet Organization', 'Lifestyle', 'cleaning', '2h', 'None', 'Medium', 'Indoor', 'Home', 'Organize wardrobe'),
        ('Digital Declutter', 'Lifestyle', 'cleaning', '2h', 'None', 'Low', 'Indoor', 'Home', 'Organize digital files'),
        
        # Financial Planning
        ('Budget Planning', 'Lifestyle', 'financial_planning', '2h', 'None', 'Medium', 'Indoor', 'Home', 'Financial review'),
        ('Investment Research', 'Lifestyle', 'financial_planning', '4h', 'None', 'High', 'Indoor', 'Home', 'Plan investments'),
        ('Expense Tracking', 'Lifestyle', 'financial_planning', '1h', 'None', 'Low', 'Indoor', 'Home', 'Track spending'),
        ('Tax Planning', 'Lifestyle', 'financial_planning', '4h', 'None', 'High', 'Indoor', 'Home', 'Prepare tax documents'),
        
        # Meal Prep
        ('Meal Prep Sunday', 'Lifestyle', 'meal_prep', '4h', 'medium', 'High', 'Indoor', 'Home', 'Prepare weekly meals'),
        ('Healthy Snack Prep', 'Lifestyle', 'meal_prep', '2h', 'low', 'Medium', 'Indoor', 'Home', 'Nutritious snacks'),
        ('Batch Cooking', 'Lifestyle', 'meal_prep', '4h', 'medium', 'High', 'Indoor', 'Home', 'Cook in bulk'),
        ('Freezer Meals', 'Lifestyle', 'meal_prep', '4h', 'medium', 'High', 'Indoor', 'Home', 'Prepare frozen meals'),
        
        # ===== SOCIAL INTERACTION =====
        # Meeting Friends
        ('Coffee with Friends', 'Social', 'meeting_friends', '2h', 'low', 'Low', 'Indoor', 'Short', 'Catch up over coffee'),
        ('Dinner Party', 'Social', 'meeting_friends', '4h', 'medium', 'Medium', 'Indoor', 'Home', 'Host friends for dinner'),
        ('Picnic in Park', 'Social', 'meeting_friends', '4h', 'low', 'Low', 'Outdoor', 'Short', 'Outdoor gathering'),
        ('Game Night with Friends', 'Social', 'meeting_friends', '4h', 'low', 'Medium', 'Indoor', 'Home', 'Social board games'),
        ('Brunch Date', 'Social', 'meeting_friends', '2h', 'medium', 'Low', 'Indoor', 'Short', 'Weekend brunch'),
        
        # Local Events
        ('Attend Local Event', 'Social', 'local_events', '4h', 'medium', 'Medium', 'Outdoor', 'Short', 'Community gathering'),
        ('Concert or Show', 'Social', 'local_events', '4h', 'high', 'Medium', 'Indoor', 'Short', 'Live entertainment'),
        ('Food Festival', 'Social', 'local_events', '4h', 'medium', 'Medium', 'Outdoor', 'Short', 'Culinary experience'),
        ('Art Exhibition', 'Social', 'local_events', '2h', 'None', 'Low', 'Indoor', 'Short', 'Local art show'),
        ('Sports Event', 'Social', 'local_events', '4h', 'high', 'Low', 'Outdoor', 'Short', 'Watch live sports'),
        
        # Volunteering
        ('Volunteer at Shelter', 'Social', 'volunteering', '4h', 'None', 'Medium', 'Indoor', 'Short', 'Give back to community'),
        ('Beach Cleanup', 'Social', 'volunteering', '4h', 'None', 'High', 'Outdoor', 'Short', 'Environmental volunteering'),
        ('Food Bank Volunteer', 'Social', 'volunteering', '4h', 'None', 'Medium', 'Indoor', 'Short', 'Help feed the hungry'),
        ('Animal Shelter Help', 'Social', 'volunteering', '4h', 'None', 'Medium', 'Indoor', 'Short', 'Care for animals'),
        ('Community Garden', 'Social', 'volunteering', '4h', 'None', 'High', 'Outdoor', 'Short', 'Community gardening'),
        
        # Online Community
        ('Join Online Community', 'Social', 'online_community', '1h', 'None', 'Low', 'Indoor', 'Home', 'Connect with like-minded people'),
        ('Virtual Game Night', 'Social', 'online_community', '2h', 'None', 'Low', 'Indoor', 'Home', 'Online multiplayer'),
        ('Discord Chat', 'Social', 'online_community', '1h', 'None', 'Low', 'Indoor', 'Home', 'Chat with friends'),
        ('Online Forum Discussion', 'Social', 'online_community', '1h', 'None', 'Low', 'Indoor', 'Home', 'Engage in discussions'),
        ('Virtual Meetup', 'Social', 'online_community', '2h', 'None', 'Low', 'Indoor', 'Home', 'Online networking'),
    ]