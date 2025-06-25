import asyncio
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager
from PIL import Image, ImageDraw, ImageFont, ImageOps
import hid
import numpy as np
import matplotlib.pyplot as plt
import time, re


# class FramePreview:
#     def __init__(self):
#         self.fig, self.ax = plt.subplots()
#         self.image = self.ax.imshow(np.zeros((HEIGHT, WIDTH)), cmap="gray", vmin=0, vmax=255)
#         self.ax.axis("off")
#         plt.ion()
#         plt.show()

#     def update(self, frame):
#         # Convert from mode "1" to "L" (8-bit grayscale)
#         frame_l = frame.convert("L")
#         # Invert so text shows up as dark-on-light (optional)
#         array = np.array(frame_l)
#         self.image.set_array(array)
#         self.fig.canvas.draw_idle()
#         plt.pause(0.01)  # Allow the plot to update


# Customize:
WIDTH, HEIGHT = 128, 32
PROGRESS_BAR_HEIGHT = 8
TEXT_HEIGHT = HEIGHT - PROGRESS_BAR_HEIGHT  # 26 pixels for text
FONT_PATH = r"C:\Windows\Fonts\david.ttf"
FONT_SIZE = 13
SMALL_FONT_SIZE = 11
VENDOR_ID, PRODUCT_ID = 0xFEED, 0x0000
SCROLL_GAP = 20  # Gap between end and start of scrolling text

font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
small_font = ImageFont.truetype(FONT_PATH, SMALL_FONT_SIZE)

# preview = FramePreview()


def format_time(s):
    m, s = divmod(s, 60)
    return f"{m:02.0f}:{s:02.0f}"

def create_progress_bar(progress, width=WIDTH, height=PROGRESS_BAR_HEIGHT, pos_seconds=0, total_seconds=0):
    bar_img = Image.new("1", (width, height), 0)
    draw = ImageDraw.Draw(bar_img)

    full_bar_width = width
    bar_filled = int((progress / 100.0) * full_bar_width)

    # filled part
    draw.rectangle((0, 0, bar_filled, height), fill=1)
    # empty part
    draw.rectangle((bar_filled, 0, full_bar_width, height), fill=0)
    # outline
    draw.rectangle((0, 0, full_bar_width, height), outline=1)

    return bar_img

def create_scrolling_text_image(text, font, height):
    """Create a scrolling text image with wrapping"""
    temp_img = Image.new("1", (1000, height), 0)
    temp_draw = ImageDraw.Draw(temp_img)
    text_width = int(temp_draw.textlength(text, font=font))
    
    if text_width <= WIDTH:
        # Text fits, no scrolling needed
        img = Image.new("1", (WIDTH, height), 0)
        draw = ImageDraw.Draw(img)
        draw.text((WIDTH/2, 0), text, font=font, fill=1, anchor='ma')
        return img, text_width
    else:
        # Text needs scrolling - create image with gap for wrapping
        scroll_width = text_width + SCROLL_GAP
        img = Image.new("1", (scroll_width, height), 0)
        draw = ImageDraw.Draw(img)
        # Draw text at the beginning
        draw.text((0, 0), text, font=font, fill=1)
        # Draw text again after the gap for seamless wrapping
        draw.text((text_width + SCROLL_GAP, 0), text, font=font, fill=1)
        return img, scroll_width

def crop_with_wrap(img, crop_x, crop_width, img_width, height):
    """Crop an image with wrapping when crop extends beyond image boundary"""
    result = Image.new("1", (crop_width, height), 0)
    
    if crop_x + crop_width <= img_width:
        # Simple crop - no wrapping needed
        cropped = img.crop((crop_x, 0, crop_x + crop_width, height))
        result.paste(cropped, (0, 0))
    else:
        # Wrapping needed - composite two parts
        # First part: from crop_x to end of image
        first_part_width = img_width - crop_x
        first_part = img.crop((crop_x, 0, img_width, height))
        result.paste(first_part, (0, 0))
        
        # Second part: from beginning of image to fill remaining width
        remaining_width = crop_width - first_part_width
        if remaining_width > 0:
            second_part = img.crop((0, 0, remaining_width, height))
            result.paste(second_part, (first_part_width, 0))
    
    return result

def contains_hebrew(text):
    return bool(re.search(r'[\u0590-\u05FF]', text))



def text_to_frames(artist, title, progress, pos_seconds, total_seconds, x, start_time):
    pos_seconds = pos_seconds + (time.time()-start_time)
    artist = artist if not contains_hebrew(artist) else artist[::-1]  # Reverse non-ASCII artist names
    title = title if not contains_hebrew(title) else title[::-1]  # Reverse non-ASCII titles

    # Create scrolling text images
    artist_img, artist_scroll_width = create_scrolling_text_image(artist, font, TEXT_HEIGHT//2)
    title_img, title_scroll_width = create_scrolling_text_image(title, font, TEXT_HEIGHT//2)
    
    # Create progress bar image
    bar_img = create_progress_bar(progress, WIDTH, PROGRESS_BAR_HEIGHT, pos_seconds, total_seconds)

    # Create final frame
    frame = Image.new("1", (WIDTH, HEIGHT), 0)
    
    if artist_scroll_width <= WIDTH and title_scroll_width <= WIDTH:
        # No scrolling needed - text fits
        frame.paste(title_img, (0, 0))
        frame.paste(artist_img, (0, TEXT_HEIGHT // 2))
    else:
        # Scrolling needed - crop with wrapping
        artist_crop_x = x % artist_scroll_width if artist_scroll_width > WIDTH else 0
        title_crop_x = x % title_scroll_width if title_scroll_width > WIDTH else 0
        
        # Crop and paste title
        if title_scroll_width > WIDTH:
            title_crop = crop_with_wrap(title_img, title_crop_x, WIDTH, title_scroll_width, TEXT_HEIGHT // 2)
            frame.paste(title_crop, (0, 0))
        else:
            frame.paste(title_img, (0, 0))
            
        # Crop and paste artist
        if artist_scroll_width > WIDTH:
            artist_crop = crop_with_wrap(artist_img, artist_crop_x, WIDTH, artist_scroll_width, TEXT_HEIGHT // 2)
            frame.paste(artist_crop, (0, TEXT_HEIGHT // 2))
        else:
            frame.paste(artist_img, (0, TEXT_HEIGHT // 2))
    
    # Paste progress bar
    frame.paste(bar_img, (0, TEXT_HEIGHT))
    
    # Add time labels with XOR overlay
    draw = ImageDraw.Draw(frame)
    label = f"{format_time(pos_seconds)} / {format_time(total_seconds)}"
    label_img = Image.new("1", (WIDTH, PROGRESS_BAR_HEIGHT), 0)
    label_draw = ImageDraw.Draw(label_img)
    label_draw.text((0, 0), label, font=small_font, fill=1)
    
    # XOR the label onto the progress bar
    for y in range(PROGRESS_BAR_HEIGHT):
        for x_pos in range(WIDTH):
            label_pixel = label_img.getpixel((x_pos, y))
            if label_pixel:
                bg_y = TEXT_HEIGHT + y
                bg_pixel = frame.getpixel((x_pos, bg_y))
                frame.putpixel((x_pos, bg_y), bg_pixel ^ 1)
    
    return frame

def frame_to_bytes(img):
    buf = bytearray()
    for y in range(0, HEIGHT, 8):
        for x in range(WIDTH):
            byte = 0
            for b in range(8):
                if y + b < HEIGHT and img.getpixel((x, y + b)):
                    byte |= (1 << b)
            buf.append(byte)
    return buf

def send_frame(bytebuf):
    report = bytearray([0x00]) + bytebuf
    try:
        d = hid.device()
        d.open(VENDOR_ID, PRODUCT_ID)
        d.write(report)
        d.close()
    except Exception as e:
        print("HID send error:", e)

x = 0  # Scrolling position


async def fetch_and_send():
    global x
    mgr = await GlobalSystemMediaTransportControlsSessionManager.request_async()
    session = mgr.get_current_session()
    if session:
        props = await session.try_get_media_properties_async()
        info = session.get_playback_info()
        timeline = session.get_timeline_properties()

        artist = props.artist
        title = props.title
        status = info.playback_status.name

        if status.capitalize() == "Playing".capitalize():
            pos = timeline.position.total_seconds()
            dur = timeline.end_time.total_seconds()
            progress = (pos / dur) * 100 if dur > 0 else 0
            frame = text_to_frames(artist, title, progress, pos, dur, x, time.time())
            x += 6  # Increment scrolling position for next frame
            # preview.update(frame)  # Update preview window
            send_frame(frame_to_bytes(frame))
        else:
            # Notify keyboard of stop/pause by clearing
            print("Media is not playing, clearing display.")
    else:
        print("No media session found.")


async def main():
    while True:
        await fetch_and_send()
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())