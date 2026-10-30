"""
Kumbh-Drishti AI: Anomaly & Stampede Risk Detection Engine
Analyzes crowd turbulence, fallen person detection, and bottleneck risk index.
"""

import cv2
import numpy as np
import time


class AnomalyDetector:
    def __init__(self):
        self.alert_history = []

    def compute_stampede_risk_score(self, density_per_m2, movement_turbulence=0.5, bottleneck_factor=0.3):
        """
        Computes a normalized Stampede Risk Score (0 - 100%) based on:
        - Spatial Density (Weight: 50%)
        - Kinetic Movement Turbulence / Panic Velocity (Weight: 30%)
        - Structural Bottleneck Factor (Weight: 20%)
        """
        # Density contribution (0 to 6.0 scale normalized to 0-100)
        density_score = min(100.0, (density_per_m2 / 5.5) * 100.0)
        
        # Turbulence contribution
        turb_score = min(100.0, movement_turbulence * 100.0)
        
        # Bottleneck contribution
        bottleneck_score = min(100.0, bottleneck_factor * 100.0)
        
        # Weighted Risk Score
        total_risk = (0.50 * density_score) + (0.30 * turb_score) + (0.20 * bottleneck_score)
        total_risk = round(min(100.0, max(0.0, total_risk)), 1)
        
        if total_risk < 35.0:
            category = "LOW HAZARD"
            badge = "🟢 NORMAL"
            color = "#22c55e"
        elif total_risk < 65.0:
            category = "MODERATE TURBULENCE"
            badge = "🟡 ELEVATED"
            color = "#eab308"
        elif total_risk < 85.0:
            category = "HIGH STAMPEDE PROBABILITY"
            badge = "🟠 WARNING"
            color = "#f97316"
        else:
            category = "CRITICAL STAMPEDE IMMINENT"
            badge = "🔴 DANGER"
            color = "#ef4444"
            
        return {
            "risk_score": total_risk,
            "category": category,
            "badge": badge,
            "color": color,
            "density_component": round(density_score, 1),
            "turbulence_component": round(turb_score, 1),
            "bottleneck_component": round(bottleneck_score, 1)
        }

    def detect_fallen_persons(self, image_bgr, bounding_boxes):
        """
        Detects individuals who have collapsed or fallen to the ground.
        Fallen persons exhibit horizontal aspect ratio (width > height) and lower elevation.
        """
        h_img, w_img = image_bgr.shape[:2]
        fallen_boxes = []
        
        for (x, y, w, h) in bounding_boxes:
            aspect_ratio = float(w) / (float(h) + 1e-5)
            # Normal standing human has aspect ratio w/h ~ 0.3 - 0.6
            # Fallen person on ground has aspect ratio > 1.15
            if aspect_ratio >= 1.15 and (w * h) > 300:
                fallen_boxes.append((x, y, w, h))
            elif y > (h_img * 0.65) and aspect_ratio > 0.95:
                # Lower ground plane horizontal contour
                fallen_boxes.append((x, y, w, h))

        # Check for contour anomalies on ground
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        lower_region = gray[int(h_img * 0.5):, :]
        _, thresh = cv2.threshold(lower_region, 60, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 600 < area < 4500:
                bx, by, bw, bh = cv2.boundingRect(cnt)
                if (float(bw) / (bh + 1e-5)) > 1.6:
                    actual_by = by + int(h_img * 0.5)
                    fallen_boxes.append((bx, actual_by, bw, bh))

        # Annotate image
        annotated = image_bgr.copy()
        for (x, y, w, h) in fallen_boxes:
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 0, 255), 3)
            cv2.putText(annotated, "FALLEN PERSON DETECTED", (x, max(15, y - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
        return len(fallen_boxes), fallen_boxes, annotated

    def log_incident(self, sector_name, risk_score, density, status, action_taken):
        """Logs an event into the incident history log."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "sector": sector_name,
            "density_p_m2": density,
            "risk_score": risk_score,
            "status": status,
            "action_taken": action_taken
        }
        self.alert_history.insert(0, entry)
        return entry
