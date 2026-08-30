import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys

def main():
    try:
        img = mpimg.imread('map.png')
    except FileNotFoundError:
        print("Error: map.png not found.")
        sys.exit(1)

    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Note: imshow's default extent goes from 0 to width and height to 0 (inverted y-axis).
    # This is normal for images. Extracted coordinates will perfectly match this system.
    ax.imshow(img)
    ax.set_title("Click on the corners of the room.\nMiddle-click (or Enter) to finish the room.")

    print("=== Room Calibration Tool ===")
    print("Instructions:")
    print("1. Left-Click on each corner of a room to draw its boundary.")
    print("2. Middle-Click (or press Enter) to finish this room.")
    print("3. Repeat for the next room.")
    print("4. Close the image window when you are done.\n")

    room_counter = 1
    
    while plt.fignum_exists(fig.number):
        print(f"-> Define the corners of Room {room_counter} ...")
        # n=-1 allows unlimited clicks until middle-click
        try:
            pts = plt.ginput(n=-1, timeout=-1, show_clicks=True)
        except Exception:
            break
            
        if not pts:
            break
            
        # Format output to copy-paste into location_estimation.py
        pts_str = ", ".join([f"({x:.1f}, {y:.1f})" for x, y in pts])
        print(f"Result to copy-paste:")
        print(f"    'Room {room_counter}': mpath.Path([{pts_str}]),")
        print("-" * 40)
        
        room_counter += 1

    print("\nCalibration finished! Copy these lines into the ROOM_POLYGONS dictionary in location_estimation.py")

if __name__ == "__main__":
    main()
