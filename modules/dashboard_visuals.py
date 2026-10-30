"""
Kumbh-Drishti AI: Dashboard Visuals & GIS Heatmap Generator
Renders dynamic aerial river-curve map, animated CCTV video feeds, and real-time charts.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import io
import time
import math
from PIL import Image
from scipy.ndimage import gaussian_filter


class DashboardVisuals:
    @staticmethod
    def generate_aerial_river_heatmap(tick=0):
        """
        Generates an aerial satellite-style GIS map of the river curve with pulsating heatmaps.
        """
        w, h = 900, 520
        map_img = np.zeros((h, w, 3), dtype=np.uint8)
        map_img[:] = (26, 32, 44)

        # Draw urban road network grid lines
        for x in range(0, w, 35):
            cv2.line(map_img, (x, 0), (x + 40, h), (40, 50, 65), 1)
        for y in range(0, h, 35):
            cv2.line(map_img, (0, y), (w, y + 20), (40, 50, 65), 1)
            
        # Draw curved River (Ganga/Yamuna Sangam curve)
        river_pts = np.array([
            [0, 80], [220, 100], [380, 160], [450, 240], 
            [520, 360], [650, 430], [900, 450],
            [900, 350], [680, 320], [560, 220], 
            [480, 120], [320, 40], [0, 20]
        ], np.int32)
        cv2.fillPoly(map_img, [river_pts], (75, 60, 30))
        cv2.polylines(map_img, [river_pts], True, (110, 95, 50), 2)

        # Draw bridges across the river
        cv2.line(map_img, (340, 145), (420, 75), (160, 170, 180), 5)
        cv2.line(map_img, (500, 300), (600, 270), (160, 170, 180), 5)

        # Dynamic pulsating intensity based on tick
        pulse = 0.85 + 0.15 * math.sin(tick * 0.4)

        # Heatmap accumulation layer
        heat_layer = np.zeros((h, w), dtype=np.float32)
        hotspots = [
            (460, 360, 1.0 * pulse, 45),  # Sector 4 (Severe Red Hotspot)
            (560, 210, 0.9 * pulse, 40),  # Bridge 2 (Orange/Red)
            (480, 280, 0.7, 50),          # Ghat Area (Yellow/Green)
            (360, 230, 0.5, 35),          # Sector 6
            (620, 290, 0.4 * pulse, 30),  # Gate 6
            (240, 180, 0.3, 30)           # Gate 1
        ]
        
        for (hx, hy, intensity, radius) in hotspots:
            heat_layer[hy, hx] += intensity * 100.0

        smoothed = gaussian_filter(heat_layer, sigma=32)
        if np.max(smoothed) > 0:
            norm_heat = (smoothed / np.max(smoothed) * 255).astype(np.uint8)
        else:
            norm_heat = np.zeros((h, w), dtype=np.uint8)

        heat_color = cv2.applyColorMap(norm_heat, cv2.COLORMAP_JET)
        mask = norm_heat > 25
        map_img[mask] = cv2.addWeighted(map_img[mask], 0.35, heat_color[mask], 0.65, 0)

        # Pins
        pins = [
            {"name": "Gate 1", "x": 230, "y": 140, "color": (50, 50, 220)},
            {"name": "Sector 4", "x": 460, "y": 340, "color": (50, 50, 220)},
            {"name": "Bridge 2", "x": 560, "y": 190, "color": (0, 165, 255)},
            {"name": "Ghat Area", "x": 520, "y": 390, "color": (0, 165, 255)},
            {"name": "Gate 6", "x": 670, "y": 300, "color": (0, 165, 255)},
            {"name": "Gate 9", "x": 780, "y": 420, "color": (220, 120, 30)},
            {"name": "Sector 7", "x": 620, "y": 160, "color": (50, 180, 50)}
        ]

        for p in pins:
            px, py = p["x"], p["y"]
            # Pulsing radius for red danger pins
            rad = 10 + (2 if ("Sector 4" in p["name"] and tick % 2 == 0) else 0)
            cv2.circle(map_img, (px, py), rad, p["color"], -1)
            cv2.circle(map_img, (px, py), rad + 2, (255, 255, 255), 2)
            cv2.circle(map_img, (px, py), 4, (255, 255, 255), -1)
            
            label = p["name"]
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.rectangle(map_img, (px - tw//2 - 4, py + 14), (px + tw//2 + 4, py + 30), (15, 23, 42), -1)
            cv2.putText(map_img, label, (px - tw//2, py + 26), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (240, 240, 240), 1, cv2.LINE_AA)

        return map_img

    @staticmethod
    def generate_cctv_camera_feed(camera_name="Gate 1", density="HIGH", tick=0):
        """
        Generates realistic animated CCTV video frames with moving crowd particles and live timestamps.
        """
        w, h = 380, 220
        img = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Base pavement & river steps
        for y in range(h):
            shade = int(50 + (y / h) * 45)
            img[y, :] = [shade, shade + 8, shade + 15]
            
        n_people = 130 if density == "HIGH" else (65 if density == "MEDIUM" else 25)
        np.random.seed(abs(hash(camera_name)) % 10000)
        
        # Base coordinates
        base_coords = []
        for _ in range(n_people):
            base_coords.append((np.random.randint(15, w - 15), np.random.randint(25, h - 15)))

        colors = [(30, 105, 237), (34, 34, 200), (220, 220, 220), (180, 80, 50)]
        
        # Render animated moving people
        for i, (bx, by) in enumerate(base_coords):
            # Add dynamic walking displacement based on tick
            dx = int(math.sin(tick * 0.3 + i) * 6)
            dy = int(math.cos(tick * 0.2 + i) * 3)
            
            px = max(10, min(w - 10, bx + dx))
            py = max(20, min(h - 10, by + dy))
            scale = 0.4 + 0.6 * (py / h)
            
            col = colors[i % len(colors)]
            
            # Body & Head
            cv2.ellipse(img, (px, py + int(12 * scale)), (int(7 * scale), int(14 * scale)), 0, 0, 360, col, -1)
            cv2.circle(img, (px, py - int(3 * scale)), int(4 * scale), (120, 150, 190), -1)

        # Draw CCTV HUD overlay with LIVE TICKING CLOCK
        t_str = time.strftime("%H:%M:%S")
        msec = int((time.time() * 100) % 100)
        rec_dot = "●" if (tick % 2 == 0) else " "
        cv2.putText(img, f"REC {rec_dot} {t_str}.{msec:02d}", (12, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 255), 1, cv2.LINE_AA)
        
        (lw, lh), _ = cv2.getTextSize(camera_name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(img, (8, h - 30), (16 + lw, h - 8), (0, 0, 0), -1)
        cv2.putText(img, camera_name, (12, h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        
        return img

    @staticmethod
    def generate_donut_risk_chart(high_count=3, medium_count=6, low_count=15):
        """
        Renders the circular donut chart matching the reference UI.
        """
        fig, ax = plt.subplots(figsize=(4.2, 3.2), facecolor='#111c38')
        ax.set_facecolor('#111c38')
        
        sizes = [high_count, medium_count, low_count]
        colors = ['#ef4444', '#f59e0b', '#22c55e']
        labels = [f"High ({high_count})", f"Medium ({medium_count})", f"Low ({low_count})"]
        
        wedges, texts = ax.pie(
            sizes, 
            colors=colors, 
            startangle=90, 
            wedgeprops=dict(width=0.42, edgecolor='#111c38', linewidth=2)
        )
        
        ax.legend(
            wedges, labels,
            title="",
            loc="center left",
            bbox_to_anchor=(0.95, 0.5),
            frameon=False,
            labelcolor='white',
            fontsize=10
        )
        
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=120, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        buf.seek(0)
        return Image.open(buf)
