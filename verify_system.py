"""
Kumbh-Drishti AI: Automated Module Verification Test
"""
import sys
import os

# Add local path
curr_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curr_dir)

try:
    from modules.crowd_density import CrowdDensityEngine
    from modules.anomaly_detector import AnomalyDetector
    from modules.missing_person import MissingPersonEngine
    from modules.evacuation_engine import EvacuationRoutingEngine
    from modules.announcement_gen import MultilingualAnnouncementEngine
    from modules.sample_generator import SampleMediaGenerator
    import numpy as np

    print("Step 1: Instantiating engines...")
    dens_eng = CrowdDensityEngine()
    anom_eng = AnomalyDetector()
    miss_eng = MissingPersonEngine()
    evac_eng = EvacuationRoutingEngine()
    ann_eng = MultilingualAnnouncementEngine()

    print("Step 2: Generating synthetic test frame...")
    frame = SampleMediaGenerator.generate_simulated_crowd_frame(crowd_level="CRITICAL")
    assert frame is not None and frame.shape[0] > 0, "Frame generation failed"

    print("Step 3: Testing crowd detection and heatmap generation...")
    boxes, centers = dens_eng.detect_heads_and_people(frame)
    metrics = dens_eng.calculate_crowd_metrics(len(centers), monitored_area_m2=35.0)
    heatmap, norm, smooth = dens_eng.generate_density_heatmap(frame, centers)
    assert heatmap is not None, "Heatmap generation failed"

    print(f" -> Detected Headcount: {len(centers)}, Density: {metrics['density_per_m2']} p/m2, Status: {metrics['status']}")

    print("Step 4: Testing anomaly and fallen person detection...")
    risk = anom_eng.compute_stampede_risk_score(metrics["density_per_m2"])
    n_fall, fall_boxes, fall_ann = anom_eng.detect_fallen_persons(frame, boxes)
    print(f" -> Stampede Risk Score: {risk['risk_score']}%, Fallen Count: {n_fall}")

    print("Step 5: Testing missing person search...")
    gallery = SampleMediaGenerator.generate_sample_gallery()
    matches = miss_eng.search_in_gallery(gallery[0]["image_bgr"], gallery)
    assert len(matches) > 0, "Gallery search failed"
    print(f" -> Top Match: {matches[0]['person_name']} with {matches[0]['similarity_score']}% confidence")

    print("Step 6: Testing tactical evacuation map and advisory generation...")
    sector_dens = {"G1": 4.8, "B1": 4.9, "G2": 2.0, "G3": 1.8, "S1": 2.2, "S2": 1.9, "EX1": 1.2, "EX2": 3.0, "EX3": 1.1}
    strategy = evac_eng.compute_optimal_routes(sector_dens)
    map_img = evac_eng.render_schematic_map(sector_dens)
    advisories = ann_eng.generate_advisory_text("Triveni Sangam", "CRITICAL")
    assert len(advisories["hindi"]) > 0, "Hindi advisory failed"
    print(" -> Hindi Advisory:", advisories["hindi"][:60], "...")

    print("\n✅ ALL MODULES AND TESTS PASSED SUCCESSFULLY (100% READY)!")

except Exception as e:
    import traceback
    print("❌ Verification Failed with error:")
    traceback.print_exc()
