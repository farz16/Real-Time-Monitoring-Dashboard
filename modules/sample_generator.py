"""
Kumbh-Drishti AI: Sample Media & Simulation Dataset Generator
Generates realistic crowd frames and CCTV gallery records for instant offline testing and live demos.
"""

import cv2
import numpy as np
import random


class SampleMediaGenerator:
    @staticmethod
    def generate_simulated_crowd_frame(crowd_level="CRITICAL", width=800, height=500):
        """
        Synthesizes a realistic visual simulation of Kumbh Mela Ghat / Bridge crowd.
        - LOW: 15-25 persons (Safe flow)
        - MODERATE: 45-65 persons (Moderate density)
        - CRITICAL: 110-160 persons (Severe overcrowding & stampede hazard)
        """
        # Background: Ghat stone steps & river water
        img = np.zeros((height, width, 3), dtype=np.uint8)
        
        # River water gradient at top
        for y in range(int(height * 0.28)):
            c_val = int(140 + (y / (height * 0.28)) * 40)
            img[y, :] = [c_val, 110, 60] # River water (BGR)
            
        # Stone steps gradient
        for y in range(int(height * 0.28), height):
            c_val = int(80 + ((y - height * 0.28) / (height * 0.72)) * 50)
            img[y, :] = [c_val, c_val + 10, c_val + 20] # Sandstone / pavement
            
        # Add railing / barriers
        cv2.line(img, (0, int(height * 0.30)), (width, int(height * 0.30)), (60, 60, 60), 6)
        for rx in range(0, width, 50):
            cv2.line(img, (rx, int(height * 0.25)), (rx, int(height * 0.30)), (60, 60, 60), 3)

        # Set crowd count
        if crowd_level == "LOW":
            n_people = random.randint(18, 26)
            include_fallen = False
        elif crowd_level == "MODERATE":
            n_people = random.randint(48, 62)
            include_fallen = False
        else: # CRITICAL
            n_people = random.randint(120, 155)
            include_fallen = True

        # Saffron, Red, Yellow, White, Blue clothing colors common in Indian pilgrimages
        attire_colors = [
            (30, 105, 237),  # Saffron / Orange (BGR)
            (34, 34, 200),   # Red
            (0, 215, 255),   # Yellow / Gold
            (230, 230, 230), # White Kurta
            (180, 80, 50),   # Blue
            (50, 160, 80),   # Green
            (120, 50, 180)   # Maroon
        ]
        
        skin_tones = [
            (115, 145, 195),
            (100, 130, 180),
            (90, 115, 160),
            (125, 160, 210)
        ]

        # Draw people distributed across the ghat
        np.random.seed(42 if crowd_level == "CRITICAL" else (101 if crowd_level == "MODERATE" else 777))
        
        y_start = int(height * 0.35)
        for i in range(n_people):
            # Perspective scaling: people closer to bottom are larger
            py = int(np.random.uniform(y_start, height - 30))
            scale = 0.55 + 0.65 * ((py - y_start) / (height - y_start))
            
            px = int(np.random.uniform(30, width - 40))
            color = attire_colors[i % len(attire_colors)]
            skin = skin_tones[i % len(skin_tones)]
            
            head_r = int(10 * scale)
            body_w = int(24 * scale)
            body_h = int(38 * scale)
            
            # Draw body (Torso / Kurta)
            cv2.ellipse(img, (px, py + int(body_h * 0.45)), (body_w // 2, body_h // 2), 0, 0, 360, color, -1)
            # Draw head
            cv2.circle(img, (px, py - int(head_r * 0.5)), head_r, skin, -1)
            # Draw hair
            cv2.ellipse(img, (px, py - int(head_r * 0.8)), (head_r, int(head_r * 0.6)), 0, 180, 360, (20, 20, 20), -1)

        # Draw a simulated fallen person for critical hazard demo
        if include_fallen:
            fx, fy = int(width * 0.52), int(height * 0.78)
            # Horizontal body lying on stone steps
            cv2.ellipse(img, (fx, fy), (42, 14), 0, 0, 360, (30, 105, 237), -1)
            cv2.circle(img, (fx - 36, fy), 11, (100, 130, 180), -1) # Fallen head

        return img

    @staticmethod
    def generate_sample_gallery():
        """
        Creates a simulated database of detected persons from Kumbh Mela CCTV streams.
        """
        records = [
            {
                "id": "KBH-REC-001",
                "name": "Aarav Sharma (Child, Age 8)",
                "sector": "Sector 3 - Ram Ghat Entry",
                "camera_id": "CCTV-CAM-04",
                "timestamp": "10:14:22 AM",
                "attire_color": (30, 105, 237) # Orange Kurta
            },
            {
                "id": "KBH-REC-002",
                "name": "Radha Devi (Elderly, Age 68)",
                "sector": "Sector 5 - Triveni Sangam Gate 2",
                "camera_id": "CCTV-CAM-12",
                "timestamp": "10:18:45 AM",
                "attire_color": (34, 34, 200) # Red Saree
            },
            {
                "id": "KBH-REC-003",
                "name": "Vikram Patil (Male, Age 42)",
                "sector": "Sector 1 - Railway Foot Overbridge",
                "camera_id": "CCTV-CAM-01",
                "timestamp": "09:55:10 AM",
                "attire_color": (230, 230, 230) # White Attire
            },
            {
                "id": "KBH-REC-004",
                "name": "Meera Joshi (Female, Age 29)",
                "sector": "Sector 6 - Akharas Concourse",
                "camera_id": "CCTV-CAM-19",
                "timestamp": "10:22:05 AM",
                "attire_color": (0, 215, 255) # Yellow Dupatta
            }
        ]
        
        gallery = []
        for r in records:
            # Generate person thumbnail image
            thumb = np.zeros((200, 120, 3), dtype=np.uint8)
            thumb[:] = (40, 40, 50)
            # Draw person body with their specific attire color
            cv2.ellipse(thumb, (60, 120), (35, 60), 0, 0, 360, r["attire_color"], -1)
            # Head
            cv2.circle(thumb, (60, 45), 22, (110, 140, 190), -1)
            # Hair
            cv2.ellipse(thumb, (60, 35), (22, 14), 0, 180, 360, (20, 20, 20), -1)
            
            gallery.append({
                "id": r["id"],
                "name": r["name"],
                "sector": r["sector"],
                "camera_id": r["camera_id"],
                "timestamp": r["timestamp"],
                "image_bgr": thumb
            })
            
        return gallery
