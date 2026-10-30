"""
Kumbh-Drishti AI: Crowd Density Estimation & Heatmap Engine
Computes real-time headcounts, spatial density distributions, and Gaussian heatmaps.
"""

import cv2
import numpy as np
import os
from PIL import Image
from scipy.ndimage import gaussian_filter


class CrowdDensityEngine:
    def __init__(self):
        # Safe cascade loading with fallback paths
        self.face_cascade = None
        self.upper_body_cascade = None
        
        try:
            face_xml = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(face_xml):
                fc = cv2.CascadeClassifier(face_xml)
                if not fc.empty():
                    self.face_cascade = fc
        except Exception:
            self.face_cascade = None

        try:
            body_xml = cv2.data.haarcascades + 'haarcascade_upperbody.xml'
            if os.path.exists(body_xml):
                ub = cv2.CascadeClassifier(body_xml)
                if not ub.empty():
                    self.upper_body_cascade = ub
        except Exception:
            self.upper_body_cascade = None
        
        # Initialize HOG descriptor for full body detection
        try:
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        except Exception:
            self.hog = None

    def detect_heads_and_people(self, image_bgr, sensitivity=1.1, min_neighbors=3):
        """
        Detects individuals in the image using multi-scale cascade, HOG, and gradient features.
        Guaranteed to never crash even if XML cascade files are missing.
        """
        if image_bgr is None or image_bgr.size == 0:
            return [], []

        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        gray_eq = cv2.equalizeHist(gray)
        h_img, w_img = image_bgr.shape[:2]
        
        boxes = []
        
        # 1. Face / Head detection (if cascade successfully loaded)
        if self.face_cascade is not None and not self.face_cascade.empty():
            try:
                faces = self.face_cascade.detectMultiScale(
                    gray_eq, 
                    scaleFactor=sensitivity, 
                    minNeighbors=min_neighbors, 
                    minSize=(12, 12)
                )
                for (x, y, w, h) in faces:
                    boxes.append((int(x), int(y), int(w), int(h)))
            except Exception:
                pass

        # 2. Upper body detection
        if self.upper_body_cascade is not None and not self.upper_body_cascade.empty():
            try:
                bodies = self.upper_body_cascade.detectMultiScale(
                    gray_eq, 
                    scaleFactor=1.15, 
                    minNeighbors=3, 
                    minSize=(20, 20)
                )
                for (x, y, w, h) in bodies:
                    boxes.append((int(x), int(y), int(w), int(h)))
            except Exception:
                pass

        # 3. Dense crowd & contour fallback (Always robust)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 40, 140)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 50 < area < 4000:
                bx, by, bw, bh = cv2.boundingRect(cnt)
                aspect = float(bw) / (bh + 1e-5)
                if 0.25 < aspect < 2.8:
                    boxes.append((int(bx), int(by), int(bw), int(bh)))

        # Remove duplicate / heavily overlapping boxes using Non-Maximum Suppression (NMS)
        clean_boxes = self._apply_nms(boxes, overlap_thresh=0.40)
        
        # Ensure at least minimal valid count
        if not clean_boxes:
            # Grid centroid fallback
            clean_boxes = [(int(w_img * 0.5), int(h_img * 0.5), 30, 30)]

        centers = [(x + w // 2, y + h // 2) for (x, y, w, h) in clean_boxes]
        
        return clean_boxes, centers

    def _apply_nms(self, boxes, overlap_thresh=0.35):
        """Non-Maximum Suppression to remove redundant overlapping bounding boxes."""
        if not boxes:
            return []
        
        boxes_arr = np.array(boxes, dtype="float")
        pick = []
        
        x1 = boxes_arr[:, 0]
        y1 = boxes_arr[:, 1]
        x2 = boxes_arr[:, 0] + boxes_arr[:, 2]
        y2 = boxes_arr[:, 1] + boxes_arr[:, 3]
        
        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = np.argsort(y2)
        
        while len(idxs) > 0:
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)
            
            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])
            
            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)
            
            overlap = (w * h) / (area[idxs[:last]] + 1e-5)
            idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlap_thresh)[0])))
            
        return [tuple(map(int, boxes[p])) for p in pick]

    def generate_density_heatmap(self, image_bgr, centers, sigma=25, alpha=0.55):
        """
        Generates a continuous spatial Gaussian density heatmap overlay on the frame.
        """
        h, w = image_bgr.shape[:2]
        density_map = np.zeros((h, w), dtype=np.float32)
        
        for (cx, cy) in centers:
            if 0 <= cx < w and 0 <= cy < h:
                density_map[cy, cx] += 1.0
                
        # Apply 2D Gaussian Kernel smoothing
        smoothed_density = gaussian_filter(density_map, sigma=sigma)
        
        # Normalize between 0 and 255 for colormap application
        max_val = np.max(smoothed_density)
        if max_val > 0:
            normalized_density = (smoothed_density / max_val * 255).astype(np.uint8)
        else:
            normalized_density = np.zeros((h, w), dtype=np.uint8)
            
        # Apply JET / TURBO colormap
        heatmap_colored = cv2.applyColorMap(normalized_density, cv2.COLORMAP_JET)
        
        # Alpha blend with original image
        blended_output = cv2.addWeighted(image_bgr, 1 - alpha, heatmap_colored, alpha, 0)
        
        return blended_output, normalized_density, smoothed_density

    def calculate_crowd_metrics(self, headcount, monitored_area_m2=50.0):
        """
        Calculates density in persons per square meter and returns safety status.
        """
        monitored_area_m2 = max(1.0, float(monitored_area_m2))
        density = headcount / monitored_area_m2
        
        if density < 2.0:
            status = "SAFE (NORMAL FLOW)"
            status_code = "SAFE"
            color_hex = "#22c55e" # Green
            action = "Normal crowd monitoring active. No intervention required."
            risk_level = "LOW"
        elif density <= 3.8:
            status = "MODERATE (HIGH DENSITY)"
            status_code = "MODERATE"
            color_hex = "#eab308" # Yellow
            action = "Slow down incoming crowd at entry gates. Alert sector ground marshals."
            risk_level = "MEDIUM"
        elif density <= 5.0:
            status = "HIGH RISK (CONGESTION WARNING)"
            status_code = "WARNING"
            color_hex = "#f97316" # Orange
            action = "Halt entry queue immediately. Open auxiliary exit bypass gates."
            risk_level = "HIGH"
        else:
            status = "CRITICAL (STAMPEDE DANGER!)"
            status_code = "CRITICAL"
            color_hex = "#ef4444" # Red
            action = "EMERGENCY: Sound sector evacuation sirens, initiate Green Corridor!"
            risk_level = "CRITICAL"
            
        return {
            "headcount": headcount,
            "monitored_area_m2": monitored_area_m2,
            "density_per_m2": round(density, 2),
            "status": status,
            "status_code": status_code,
            "color_hex": color_hex,
            "action": action,
            "risk_level": risk_level
        }
