"""
Kumbh-Drishti AI: Missing Person & Lost Child AI Matcher
Performs multi-feature matching across distributed Kumbh Mela CCTV feeds.
"""

import cv2
import numpy as np
import os
from PIL import Image


class MissingPersonEngine:
    def __init__(self):
        self.face_cascade = None
        try:
            face_xml = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(face_xml):
                fc = cv2.CascadeClassifier(face_xml)
                if not fc.empty():
                    self.face_cascade = fc
        except Exception:
            self.face_cascade = None

    def extract_visual_signature(self, image_bgr):
        """
        Extracts a multi-modal visual signature (HSV color histogram & edge structure).
        """
        if image_bgr is None or image_bgr.size == 0:
            return None
            
        resized = cv2.resize(image_bgr, (128, 256))
        
        # 1. Color Histogram in HSV space
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
        torso = hsv[int(256 * 0.2):int(256 * 0.7), :]
        hist_hsv = cv2.calcHist([torso], [0, 1], None, [18, 12], [0, 180, 0, 256])
        cv2.normalize(hist_hsv, hist_hsv, 0, 1, cv2.NORM_MINMAX)
        
        # 2. Texture / Edge signature
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        hist_edge = cv2.calcHist([edges], [0], None, [16], [0, 256])
        cv2.normalize(hist_edge, hist_edge, 0, 1, cv2.NORM_MINMAX)
        
        # 3. Detect face crop if available
        face_crop = None
        if self.face_cascade is not None and not self.face_cascade.empty():
            try:
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20))
                if len(faces) > 0:
                    fx, fy, fw, fh = faces[0]
                    face_crop = resized[fy:fy+fh, fx:fx+fw]
            except Exception:
                pass
            
        return {
            "hsv_hist": hist_hsv,
            "edge_hist": hist_edge,
            "face_crop": face_crop,
            "processed_image": resized
        }

    def compute_similarity(self, sig1, sig2):
        """
        Computes composite similarity score (0 - 100%) between two visual signatures.
        """
        if sig1 is None or sig2 is None:
            return 0.0
            
        bhatt_dist = cv2.compareHist(sig1["hsv_hist"], sig2["hsv_hist"], cv2.HISTCMP_BHATTACHARYYA)
        color_sim = max(0.0, (1.0 - bhatt_dist)) * 100.0
        edge_sim = max(0.0, cv2.compareHist(sig1["edge_hist"], sig2["edge_hist"], cv2.HISTCMP_CORREL)) * 100.0
        
        total_score = (0.70 * color_sim) + (0.30 * edge_sim)
        return round(min(99.4, max(5.0, total_score)), 1)

    def search_in_gallery(self, query_img_bgr, gallery_records):
        """
        Searches the query image against all registered CCTV gallery snapshots.
        """
        query_sig = self.extract_visual_signature(query_img_bgr)
        if query_sig is None:
            return []
            
        results = []
        for record in gallery_records:
            cand_img = record["image_bgr"]
            cand_sig = self.extract_visual_signature(cand_img)
            score = self.compute_similarity(query_sig, cand_sig)
            
            results.append({
                "record_id": record["id"],
                "person_name": record.get("name", "Unknown Person"),
                "sector": record["sector"],
                "camera_id": record["camera_id"],
                "timestamp": record["timestamp"],
                "similarity_score": score,
                "thumbnail": cand_img,
                "matched": score >= 65.0
            })
            
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results
