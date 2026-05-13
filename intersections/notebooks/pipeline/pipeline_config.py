# pipeline_config.py — shared tunable constants for the Rotterdam intersection photo pipeline.
# All notebooks in the pipeline import from this file so that changing a parameter
# here propagates to every notebook without editing them individually.
#
# After changing values here, re-run notebook 01 to recompute max_dist_m / ideal_dist_m
# in intersections_merged.gpkg. Notebooks 02 and 04 read from that file and pick up
# the new values automatically on their next run.

# --- Photo capture distances ---
# Notebook 01 uses these to compute per-intersection max_dist_m and ideal_dist_m,
# which are stored in intersections_merged.gpkg and read by notebooks 02 and 04.

# Buffer added on top of ideal_dist_m to set the outer search radius.
# max_dist_m = ideal_dist_m + CAPTURE_BUFFER_M
CAPTURE_BUFFER_M = 5  # metres

# Ideal photo distance formula: ideal_dist_m = BASE + cluster_radius * FACTOR
# IDEAL_PHOTO_DIST_BASE is the ideal distance for singletons (radius = 0).
# IDEAL_DIST_RADIUS_FACTOR controls how much larger intersections push the ideal
# distance outward — 1/3 means a radius-15m cluster gets 25 + 5 = 30m ideal,
# and a radius-30m cluster gets 25 + 10 = 35m ideal (less aggressive than 1:1).
IDEAL_PHOTO_DIST_BASE    = 20    # metres — ideal shot distance for singletons
IDEAL_DIST_RADIUS_FACTOR = 1/2   # scaling of cluster radius added to the ideal distance

# --- Notebook 02: spatial pre-filter buffer parameters ---
# These control the annular buffers built around each intersection to pre-select
# candidate photos before the more expensive spatial join in notebook 04.

FALLBACK_BUFFER_M   = 55  # outer radius (m) when max_dist_m is missing from the .gpkg
BUFFER_MARGIN_M     = 5   # safety margin on top of max_dist_m to catch floating-point edge cases
INNER_BUFFER_METERS = 5   # min distance from intersection centre — excludes photos inside the junction

# --- Notebook 04: photo selection ---

MIN_DIST         = 5   # metres — minimum photo distance from intersection centre
STITCH_THRESHOLD = 1   # degrees — angular gap beyond which two directional cameras are stitched
