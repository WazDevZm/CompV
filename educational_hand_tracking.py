import cv2
from cvzone.HandTrackingModule import HandDetector
import cvzone
import numpy as np
import random
import math

# Initialize camera and detector
cap = cv2.VideoCapture(0)
cap.set(3, 1920)  # Width
cap.set(4, 1080)  # Height
detector = HandDetector(detectionCon=0.8)

# Colors for educational elements
colors = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'yellow': (0, 255, 255),
    'purple': (255, 0, 255),
    'orange': (0, 165, 255),
    'pink': (203, 192, 255)
}

# Educational shapes class
class EducationalShape:
    def __init__(self, pos, shape_type, color, size=80):
        self.pos = pos
        self.shape_type = shape_type
        self.color = color
        self.size = size
        self.is_dragging = False
        self.original_pos = pos.copy()
        
    def draw(self, img):
        x, y = self.pos
        half_size = self.size // 2
        
        if self.shape_type == "circle":
            cv2.circle(img, (x, y), half_size, self.color, -1)
            cv2.circle(img, (x, y), half_size, (255, 255, 255), 2)
        elif self.shape_type == "square":
            cv2.rectangle(img, (x - half_size, y - half_size), 
                         (x + half_size, y + half_size), self.color, -1)
            cv2.rectangle(img, (x - half_size, y - half_size), 
                         (x + half_size, y + half_size), (255, 255, 255), 2)
        elif self.shape_type == "triangle":
            pts = np.array([[x, y - half_size], 
                           [x - half_size, y + half_size], 
                           [x + half_size, y + half_size]], np.int32)
            cv2.fillPoly(img, [pts], self.color)
            cv2.polylines(img, [pts], True, (255, 255, 255), 2)
    
    def is_inside(self, point):
        x, y = self.pos
        half_size = self.size // 2
        return (x - half_size < point[0] < x + half_size and 
                y - half_size < point[1] < y + half_size)
    
    def update_position(self, new_pos):
        self.pos = new_pos

# Educational activities
class EducationalGame:
    def __init__(self):
        self.shapes = []
        self.score = 0
        self.current_activity = "shapes"  # shapes, counting, colors
        self.target_count = 0
        self.collected_shapes = 0
        self.instructions = "Pinch your thumb and index finger to grab shapes!"
        self.create_shapes()
    
    def create_shapes(self):
        self.shapes = []
        shape_types = ["circle", "square", "triangle"]
        color_list = list(colors.values())
        
        # Create 8 random shapes for larger screen
        for i in range(8):
            x = random.randint(100, 1820)  # 1920 - 100
            y = random.randint(200, 880)  # 1080 - 200
            shape_type = random.choice(shape_types)
            color = random.choice(color_list)
            self.shapes.append(EducationalShape([x, y], shape_type, color))
    
    def draw_instructions(self, img):
        # Draw background for instructions - full width
        height, width = img.shape[:2]
        cv2.rectangle(img, (10, 10), (width-10, 100), (50, 50, 100), -1)
        cv2.rectangle(img, (10, 10), (width-10, 100), (255, 255, 255), 3)
        
        # Main instruction
        cv2.putText(img, self.instructions, (20, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Score
        cv2.putText(img, f"Score: {self.score}", (20, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    def draw_activity_buttons(self, img):
        # Draw activity selection buttons - larger for full screen
        button_y = 120
        height, width = img.shape[:2]
        button_width = (width - 100) // 3  # Divide screen into 3 equal parts
        
        activities = ["Shapes", "Counting", "Colors"]
        
        for i, activity in enumerate(activities):
            x = 20 + i * (button_width + 20)
            color = (0, 255, 0) if activity.lower() == self.current_activity else (100, 100, 100)
            cv2.rectangle(img, (x, button_y), (x + button_width, button_y + 60), color, -1)
            cv2.rectangle(img, (x, button_y), (x + button_width, button_y + 60), (255, 255, 255), 3)
            cv2.putText(img, activity, (x + 20, button_y + 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    
    def handle_activity_selection(self, cursor):
        button_y = 100
        activities = ["shapes", "counting", "colors"]
        
        for i, activity in enumerate(activities):
            x = 50 + i * 200
            if (x < cursor[0] < x + 150 and button_y < cursor[1] < button_y + 40):
                self.current_activity = activity
                self.score = 0
                self.create_shapes()
                return True
        return False
    
    def update_activity_instructions(self):
        if self.current_activity == "shapes":
            self.instructions = "Drag shapes around! Try to organize them by type!"
        elif self.current_activity == "counting":
            self.instructions = f"Count the {self.target_count} shapes! Drag them to the counting area!"
        elif self.current_activity == "colors":
            self.instructions = "Sort shapes by color! Drag them to color groups!"

# Initialize the educational game
game = EducationalGame()

# Main loop
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, draw=True)

    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        
        # Get distance between thumb and index finger for pinch gesture
        l, info, img = detector.findDistance((lmList[4][0], lmList[4][1]), 
                                           (lmList[8][0], lmList[8][1]), img)
        
        if l < 30:  # Pinching detected
            # Calculate cursor position (midpoint between thumb and index)
            cursor_x = (lmList[4][0] + lmList[8][0]) // 2
            cursor_y = (lmList[4][1] + lmList[8][1]) // 2
            cursor = [cursor_x, cursor_y]
            
            # Draw pinch indicator
            cv2.circle(img, (cursor_x, cursor_y), 15, (0, 255, 0), -1)
            cv2.circle(img, (cursor_x, cursor_y), 20, (0, 255, 0), 3)
            cv2.putText(img, "GRABBING!", (cursor_x - 30, cursor_y - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Check if clicking on activity buttons
            if game.handle_activity_selection(cursor):
                game.update_activity_instructions()
            else:
                # Check for shape interactions
                for shape in game.shapes:
                    if shape.is_inside(cursor):
                        shape.update_position(cursor)
                        game.score += 1
                        break
        else:
            # Show instruction when not pinching
            cv2.putText(img, "Pinch thumb and index finger to interact!", 
                       (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Draw all shapes
    for shape in game.shapes:
        shape.draw(img)
    
    # Draw UI elements
    game.draw_instructions(img)
    game.draw_activity_buttons(img)
    
    # Add some fun decorative elements
    cv2.putText(img, "LEARN WITH YOUR HANDS!", (400, 650), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)
    
    # Show the image
    cv2.imshow("Educational Hand Tracking", img)
    
    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
