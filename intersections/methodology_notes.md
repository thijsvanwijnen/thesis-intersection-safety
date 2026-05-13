# Methodological Notes
*Working document for report writing — records conceptual choices and their justification*

---

## 1. Study area delineation

The analysis is limited to the inner urban area of Rotterdam, enclosed by the main
highway ring (A20, A13, A16, A15). This boundary was drawn manually based on local
knowledge of the city's structure and saved as a GeoJSON polygon.

**Why this area?**
The highway ring forms a natural boundary between the dense urban street network and
the surrounding suburban/industrial areas. Intersections within the ring are more
likely to be the kind of urban junctions relevant to a road safety study — signalized
intersections, multi-leg junctions, mixed traffic environments. The outer areas contain
more highway on-ramps and industrial access roads which are less relevant.

---

## 2. Intersection definition

An intersection is defined as any NWB junction point (JTE_ID) where three or more
road segments meet (`street_count >= 3`). Nodes with only two connections are excluded
as these are simply points along a continuous road (e.g. where a road changes name or
speed limit), not genuine decision points for road users.

**Why this threshold?**
A two-road meeting point does not constitute a junction from a road safety perspective —
there is no conflict between crossing traffic streams. Three or more legs is the minimum
for a genuine intersection where road users must decide on priority, yield, or crossing.

---

## 3. Photo selection distance (5–55m band)

Photos are selected if they are taken between 5 and 55 metres of an intersection centroid.

**Why 55m?**
The threshold was validated through visual inspection against Google Maps. At 55m,
the intersection is still clearly visible and inspectable in the panoramic image.
Beyond this distance the intersection becomes too small to meaningfully assess
safety-relevant features (road markings, signage, geometry).

**Why exclude below 5m?**
At distances below 5m, the camera is already within the intersection itself rather than
approaching it. Photos taken inside the junction do not represent an approach perspective
and are therefore excluded.

---

## 4. Dropping the directional (cone) filter

An initial version of the photo selection included a directional filter — only keeping
photos where the intersection fell within ±60° of the vehicle's driving direction (Pan angle).
This filter was subsequently removed.

**Why removed?**
The camera system records full 360° equirectangular panoramas. This means every selected
photo captures the full surrounding environment — the intersection is always visible
somewhere in the image regardless of which direction the vehicle was driving. A
directional filter would unnecessarily discard valid photos where the intersection
is visible to the side or behind the vehicle, without any gain in image quality.

The directional logic is still relevant, but applied later (see Section 6) — not for
filtering photos out, but for knowing where to look within the panorama.

---

## 5. Per-leg approach: one image per road leg

Rather than using any photo taken near an intersection, the analysis is structured
around **approach legs** — the individual road segments that connect to each intersection.

**Why per-leg?**
Different legs of the same intersection can have very different safety characteristics:
one approach may have a clear sightline while another is obstructed by parked cars or
vegetation. A single photo of the intersection does not capture these differences.
By selecting one photo per leg, each approach is assessed on its own terms.

This also makes the dataset more balanced across intersections with different numbers
of legs (T-junctions have 3 legs, crossroads have 4, some complex junctions have 5+).

---

## 6. Leg direction from NWB geometry

The bearing of each approach leg is derived from the road network geometry in the
NWB (Nationaal Wegenbestand) — specifically, the direction from the neighboring
junction node toward the intersection node. This gives the compass angle from which
a road user would arrive when traveling along that leg.

**Why NWB geometry rather than photo-derived direction?**
NWB road geometry is a stable, nationally maintained source for the physical layout of
the street network. Deriving approach directions from photo metadata alone would
introduce noise from vehicle movement (slight curves, lane changes). NWB gives
the canonical direction of the road independent of how any individual vehicle traveled it.

---

## 7. Photo-to-leg matching criteria

For each leg, the best photo is selected from all photos within 55m using two criteria:
1. The photo must be positioned on the correct side of the intersection for that leg
   (within ±45° of the expected approach direction)
2. Among qualifying photos, the one closest to 30m from the intersection is preferred

**Why 30m as the ideal distance?**
At 30m, the approaching road user is close enough that the intersection's geometry,
signage and markings are clearly visible, but far enough to capture the full junction
rather than being inside it. This approximates the decision-making zone — the point
at which a driver must assess the intersection and decide how to proceed.

**Why ±45° directional tolerance?**
The vehicle does not always travel perfectly along the road centreline, and roads
curve slightly. A ±45° window is narrow enough to exclude photos taken from the wrong
leg, while wide enough to accommodate normal driving variation and gentle curves.

---

## 8. Image reprojection method

360° equirectangular panoramas are converted to flat perspective images for visual
analysis. Perspective reprojection (rather than simple rectangular cropping) is used.

**Why perspective reprojection rather than cropping?**
A simple rectangular crop of an equirectangular image introduces barrel distortion —
straight lines appear curved, particularly toward the left and right edges. This
distortion makes it harder to assess spatial relationships in the scene (road width,
sightline length, geometry of the junction). Perspective reprojection mathematically
corrects for this distortion, producing an image equivalent to what a standard camera
would capture — straight lines remain straight.

**Why center the intersection in the reprojected image?**
The reprojection is oriented so the intersection is in the center of the output frame,
regardless of the vehicle's actual driving direction. This ensures all approach images
are consistently framed for comparison — the junction geometry is always the focal
point of the image, not an incidental element at the edge of frame.

**Current reprojection parameters** (confirmed for the annotation phase; may be adjusted
after discussion with road safety experts before final analysis):
- Horizontal field of view: 90°
- Output resolution: 1500 × 880 px (after car hood crop)
- Vertical tilt: +5° upward
- Bottom crop: 12% removed

---

## 9. Car hood removal

The camera is mounted on a vehicle, meaning the car's hood is visible in the bottom
portion of every image. This is removed by combining a slight upward tilt during
reprojection with a fixed bottom crop.

**Why remove it?**
The car hood is not part of the road environment and adds no information relevant to
safety assessment. Its presence at the bottom of every image is a visual distraction
during inspection and may introduce bias in pairwise comparisons if it is more or less
prominent in different images.

---

---

## 10. Road type filtering (NWB)

Before counting intersections, road segments are filtered to a relevant subset using
two NWB attributes applied in sequence:

1. `WEGBEHSRT == 'G'` — keep only gemeente-managed roads, excluding national (Rijk)
   and provincial (Provincie) roads
2. `BST_CODE in {RB, ERF, HR}` — keep only normal carriageways (rijbaan, erf/woonerf,
   hoofdrijbaan), excluding roundabout lanes (NRB, GRB, TRB), slip roads (AFR, OPR)

**Why filter by road manager first?**
Without the gemeente filter, junction points on national and provincial roads are
included, inflating the dataset with motorway on/off-ramps and interchange junctions
that are not relevant to urban road safety research.

**Why filter by road type (BST_CODE)?**
Roundabout lanes and slip roads form separate NWB segments that would otherwise
generate spurious junction points. Removing them ensures the intersection count
reflects genuine decision points for road users, not artefacts of how the network
is encoded.

---

## 11. Junction deduplication

After extracting raw junction points, a deduplication step merges junctions that
represent the same physical intersection but appear as multiple NWB points.

Two types of duplicates are handled:

1. **Dual carriageway pairs** — roads with a physical central reservation are stored
   as two parallel NWB segments, producing two junction points per physical intersection.
   These are merged when two junctions are within 25m of each other and at least one
   connecting road has `FOW=2` (multiple carriageway).

2. **Bayonet artefacts** — administrative splits in the network (e.g. at municipality
   or road name boundaries) create closely-spaced junction pairs that are not real
   physical intersections. These are merged when two junctions are within 7m of each other.

**Why these thresholds?**
The 25m threshold for dual carriageways was set by inspecting the typical separation
between parallel carriageways in Rotterdam. The 7m threshold for bayonet artefacts
was set to be tight enough to avoid merging genuinely distinct junctions while
catching the spurious close pairs introduced by administrative splits.

After deduplication, the dataset reduces from 5,846 to 4,858 junctions.

---

## 12. Stratification design

Intersections are stratified along two active dimensions before sampling:

- **dim_type**: T-junction (3-arm) vs. 4+-junction (4 or more arms)
- **dim_priority**: VRI (traffic light controlled), geen_voorrang (uncontrolled),
  voorrang (priority road / yield sign)

This produces 6 strata. Two further dimensions (crash risk level, speed limit) are
present in the data structure but are currently inactive — all intersections receive
a placeholder value (`_`) for these.

**Why these two dimensions?**
Intersection type (T vs. 4+) captures a fundamental difference in geometry and the
number of potential conflict points. Priority regime captures the legal and regulatory
safety environment at the junction. Together they define meaningfully different
intersection contexts for safety assessment.

**Why equal sampling (N=70 per stratum)?**
Equal sampling ensures each stratum is represented by a similar number of observations,
preventing the analysis from being dominated by the most common stratum
(T / geen_voorrang, which makes up ~62% of all intersections).
Strata with fewer than 70 available intersections contribute all available members
(e.g. T/VRI has only 16 intersections).

---

## 13. Bradley-Terry pairwise comparison design

Intersections are compared in pairs using a pairwise survey, and a Bradley-Terry (BT)
model is fitted to convert comparison outcomes into a continuous safety score per intersection.

**Pair schedule design:**
The comparison schedule is built in two layers:

1. **Within-stratum pairs** — each intersection is compared primarily against others in
   its own stratum. A minimum spanning tree backbone guarantees within-stratum connectivity,
   and additional pairs are added until every intersection has at least 7 comparisons.
   Small strata (≤20 intersections) receive a full round-robin instead.

2. **Bridging pairs** — cross-stratum pairs connect the 6 strata into a single connected
   graph, which is a requirement for BT estimation (scores from disconnected components
   cannot be placed on a common scale). A spanning tree of 5 links provides minimum
   connectivity; 3 extra diagonal links add robustness.

**Rater assignment:**
The full schedule of 1,681 pairs is distributed across 16 raters. Each rater receives
40 pairs (approximately 20 minutes at 2 pairs/minute): 15 anchor pairs shown to all
raters (used for inter-rater reliability checks, drawn from cross-stratum bridging pairs)
and 25 unique pairs. Pairs are shuffled before assignment so each rater sees a mix of
strata rather than one stratum at a time.

**Survey platform:** PixelSurvey, a platform designed for image-based pairwise
comparisons. Each task presents two approach images side by side and asks which
intersection looks less safe.

**Traffic intensity display:** Alongside each image, raters are shown the average
traffic intensity of the approach leg in vehicles per hour (derived from daily counts,
divided by 24 and rounded to the nearest 10). Intensity is included because road layout
should be assessed in the context of the traffic load it serves — a narrow road with
little traffic may be appropriate, while the same layout carrying heavy traffic may be
genuinely unsafe. Showing intensity allows raters to factor this into their safety
judgment rather than judging road geometry in isolation.

---

*Last updated: 2026-05-05*
