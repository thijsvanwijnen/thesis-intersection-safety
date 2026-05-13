"""
review_photos.py

Keyboard-driven photo reviewer for manual quality control.
Shows each annotated photo fullscreen; press a key to approve or reject.

Controls:
    →  /  Space    Next photo (keep)
    ←              Previous photo (go back)
    B              Mark as bad and go to next
    U              Undo: un-mark the current photo if it was marked bad
    Q  /  Escape   Quit and save progress

Flags:
    --snapshot   Mark all photos currently in the folder as "seen" without
                 showing them. Run this BEFORE executing NB05c + NB07 +
                 prepare_inspection_photos.py so that --new-only afterwards
                 shows only the replacement photos.
    --new-only   Only show photos not yet seen in a previous session.
                 Useful for reviewing replacement photos after NB05c + NB07.
                 Old bad_photos.csv entries are preserved automatically.
    --good-only  Only show photos NOT currently marked as bad. Useful for a
                 second-pass review of approved photos.
    --reset      Ignore all saved progress and start from scratch.

Progress is saved to a JSON file after every action so you can quit and
resume at any time without losing your work.

Output:
    bad_photos.csv   — intersection_id and leg_bearing for all rejected photos,
                       ready to filter out of the analysis

Run from the intersections/ folder:
    python scripts/review_photos.py
    python scripts/review_photos.py --new-only
"""

import argparse
import csv
import json
import os
import sys
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk

# ---------------------------------------------------------------------------
# Default paths
# ---------------------------------------------------------------------------
VAULT_ROOT   = r"D:\rotterdam_aiis_2025\vault-production\vault_v1"
PHOTOS_DIR   = os.path.join(VAULT_ROOT, "reprojected_directional_fov90_dist20_new_to_check")

# Progress + output live next to this script
SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(SCRIPT_DIR, "review_progress.json")
OUTPUT_CSV    = os.path.join(SCRIPT_DIR, "bad_photos.csv")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_photos(photos_dir: str) -> list[str]:
    """Return sorted list of .jpeg/.jpg file paths in the flat review folder."""
    exts = {".jpeg", ".jpg"}
    files = [
        os.path.join(photos_dir, f)
        for f in sorted(os.listdir(photos_dir))
        if Path(f).suffix.lower() in exts
    ]
    return files


def parse_filename(path: str) -> tuple[str, str]:
    """
    Extract intersection_id and bearing from a flat filename like
    '180274036_leg_278.jpeg' -> ('180274036', '278').
    """
    stem = Path(path).stem                      # '180274036_leg_278'
    parts = stem.split("_leg_", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return stem, ""                             # fallback: use full stem


def load_progress(path: str) -> dict:
    """Load saved progress from JSON; return empty state if file missing."""
    if os.path.exists(path):
        with open(path) as f:
            state = json.load(f)
        # Add seen_files if missing (backward compatibility with old progress files)
        state.setdefault("seen_files", [])
        return state
    return {"current_index": 0, "bad_files": [], "seen_files": []}


def save_progress(path: str, state: dict) -> None:
    """Persist current index, bad-file list, and seen-file list to JSON."""
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


def write_output_csv(output_path: str, bad_files: list[str]) -> None:
    """Write intersection_id + leg_bearing for all bad photos to CSV."""
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["intersection_id", "leg_bearing"])
        for fpath in bad_files:
            intersection_id, bearing = parse_filename(fpath)
            writer.writerow([intersection_id, bearing])


# ---------------------------------------------------------------------------
# Viewer
# ---------------------------------------------------------------------------

class PhotoReviewer:
    def __init__(self, root: tk.Tk, photos: list[str], state: dict):
        self.root    = root
        self.photos  = photos
        self.state   = state            # {"current_index": int, "bad_files": [...], "seen_files": [...]}
        self.bad_set  = set(state["bad_files"])
        self.seen_set = set(state["seen_files"])

        self.root.title("Photo Reviewer")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)

        # Image label fills the window
        self.img_label = tk.Label(root, bg="black")
        self.img_label.pack(fill=tk.BOTH, expand=True)

        # Status bar at the bottom
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(
            root, textvariable=self.status_var,
            bg="#222", fg="white", font=("Segoe UI", 14),
            anchor="w", padx=12, pady=6,
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Key bindings
        root.bind("<Right>",  lambda e: self.next_photo())
        root.bind("<space>",  lambda e: self.next_photo())
        root.bind("<Left>",   lambda e: self.prev_photo())
        root.bind("<b>",      lambda e: self.mark_bad())
        root.bind("<B>",      lambda e: self.mark_bad())
        root.bind("<u>",      lambda e: self.unmark_bad())
        root.bind("<U>",      lambda e: self.unmark_bad())
        root.bind("<q>",      lambda e: self.quit())
        root.bind("<Q>",      lambda e: self.quit())
        root.bind("<Escape>", lambda e: self.quit())

        self.show_current()

    def current_path(self) -> str:
        return self.photos[self.state["current_index"]]

    def show_current(self) -> None:
        idx   = self.state["current_index"]
        path  = self.current_path()
        total = len(self.photos)

        # Load and scale image to fit the screen while keeping aspect ratio
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight() - 40   # leave room for status bar

        img = Image.open(path)
        img.thumbnail((screen_w, screen_h), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img)
        self.img_label.configure(image=self.tk_img)

        # Status bar text
        is_bad    = path in self.bad_set
        bad_count = len(self.bad_set)
        marker    = "  [BAD]" if is_bad else ""
        fname     = os.path.basename(path)

        self.status_var.set(
            f"  {idx + 1} / {total}   |   {fname}{marker}"
            f"   |   {bad_count} marked bad"
            f"   |   -> next   <- back   B mark bad   U undo   Q quit"
        )

        # Highlight status bar red when current photo is marked bad
        self.status_bar.configure(bg="#8b0000" if is_bad else "#222")

    def next_photo(self) -> None:
        # Record current photo as seen before advancing
        self.seen_set.add(self.current_path())
        self.state["seen_files"] = list(self.seen_set)

        if self.state["current_index"] < len(self.photos) - 1:
            self.state["current_index"] += 1
            self._persist()
            self.show_current()
        else:
            # Already at the last photo — still persist the seen update
            self._persist()

    def prev_photo(self) -> None:
        if self.state["current_index"] > 0:
            self.state["current_index"] -= 1
            self._persist()
            self.show_current()

    def mark_bad(self) -> None:
        path = self.current_path()
        if path not in self.bad_set:
            self.bad_set.add(path)
            # Also mark as seen so --new-only skips it in future sessions
            self.seen_set.add(path)
            self.state["bad_files"]  = list(self.bad_set)
            self.state["seen_files"] = list(self.seen_set)
            self._persist()
        self.next_photo()

    def unmark_bad(self) -> None:
        path = self.current_path()
        if path in self.bad_set:
            self.bad_set.discard(path)
            self.state["bad_files"] = list(self.bad_set)
            self._persist()
        self.show_current()

    def _persist(self) -> None:
        """Save progress JSON and regenerate the output CSV."""
        save_progress(PROGRESS_FILE, self.state)
        write_output_csv(OUTPUT_CSV, list(self.bad_set))

    def quit(self) -> None:
        self._persist()
        print(f"\nProgress saved to:  {PROGRESS_FILE}")
        print(f"Bad photos CSV:     {OUTPUT_CSV}")
        print(f"Marked bad: {len(self.bad_set)} / {len(self.photos)}")
        self.root.destroy()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--photos-dir", default=PHOTOS_DIR,
                        help="Folder with flat annotated photos (to-check folder).")
    parser.add_argument("--reset", action="store_true",
                        help="Ignore saved progress and start from the first photo.")
    parser.add_argument("--new-only", action="store_true",
                        help="Only show photos not yet seen in a previous session. "
                             "Old bad_photos.csv entries are preserved automatically.")
    parser.add_argument("--good-only", action="store_true",
                        help="Only show photos not currently marked as bad. "
                             "Useful for a second-pass review of approved photos.")
    parser.add_argument("--snapshot", action="store_true",
                        help="Mark all current photos as seen without showing them. "
                             "Run before NB05c + NB07 so --new-only later shows only new photos.")
    args = parser.parse_args()

    if not os.path.exists(args.photos_dir):
        sys.exit(f"Photos folder not found: {args.photos_dir}\n"
                 "Run prepare_inspection_photos.py first.")

    all_photos = load_photos(args.photos_dir)
    if not all_photos:
        sys.exit("No .jpeg/.jpg files found in the photos folder.")

    print(f"Found {len(all_photos)} photos in {args.photos_dir}")

    if args.snapshot:
        # Record every photo currently in the folder as seen, without showing any.
        # This lets --new-only correctly skip them after new photos are added.
        state = load_progress(PROGRESS_FILE)
        seen_set = set(state.get("seen_files", [])) | set(all_photos)
        state["seen_files"] = list(seen_set)
        save_progress(PROGRESS_FILE, state)
        print(f"Snapshot saved: {len(seen_set)} photos marked as seen in {PROGRESS_FILE}")
        print("You can now run NB05c + NB07 + prepare_inspection_photos.py.")
        print("Afterwards, use --new-only to review only the replacement photos.")
        return

    if args.reset:
        state = {"current_index": 0, "bad_files": [], "seen_files": []}
        photos = all_photos
    elif args.good_only:
        # Load full state so bad_files are preserved when writing the CSV
        state = load_progress(PROGRESS_FILE)
        bad_set = set(state.get("bad_files", []))
        photos = [p for p in all_photos if p not in bad_set]
        state["current_index"] = 0
        print(f"Good photos to review: {len(photos)}  (skipping {len(bad_set)} already marked bad)")
    elif args.new_only:
        # Load full saved state so old bad_files are preserved in the output CSV
        state = load_progress(PROGRESS_FILE)
        seen = set(state.get("seen_files", [])) | set(state.get("bad_files", []))
        photos = [p for p in all_photos if p not in seen]
        if not photos:
            print("No new photos to review — all photos have already been seen.")
            return
        # Reset index to 0 for the new subset; bad_files and seen_files carry over
        state["current_index"] = 0
        print(f"New photos to review: {len(photos)}  (skipping {len(all_photos) - len(photos)} already seen)")
    else:
        state  = load_progress(PROGRESS_FILE)
        photos = all_photos
        # Clamp index in case the photo list changed since last run
        state["current_index"] = min(state["current_index"], len(photos) - 1)
        # Remove any saved bad_files that no longer exist on disk
        state["bad_files"] = [p for p in state["bad_files"] if p in set(photos)]
        if state["current_index"] > 0:
            print(f"Resuming from photo {state['current_index'] + 1} / {len(photos)}")

    root = tk.Tk()
    PhotoReviewer(root, photos, state)
    root.mainloop()


if __name__ == "__main__":
    main()
