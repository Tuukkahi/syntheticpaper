from PIL import Image
from pathlib import Path

def stack_frames(
    frame_paths,
    out_path,
    *,
    drop_bottom_frac=0.14,   # fraction of height to remove (colorbar area)
    drop_side_frac=0.03,     # fraction of width to remove from left and right
    keep_colorbar_on_last=True,
    gap_px=0,
    bg=(255, 255, 255, 255),
):
    """
    Stack frames vertically. Crop sides for all frames.
    Crop bottom (colorbar) for all but the last frame.
    """
    frame_paths = [Path(p) for p in frame_paths]
    ims = [Image.open(p).convert("RGBA") for p in frame_paths]

    cropped = []
    for i, im in enumerate(ims):
        w, h = im.width, im.height

        # side crop
        dx = int(round(drop_side_frac * w))
        left = dx
        right = w - dx

        # bottom crop (colorbar)
        is_last = (i == len(ims) - 1)
        if keep_colorbar_on_last and is_last:
            bottom = h
        else:
            dy = int(round(drop_bottom_frac * h))
            bottom = max(1, h - dy)

        # top always stays at 0
        im2 = im.crop((left, 0, right, bottom))
        cropped.append(im2)

    # sanity: all widths must match now
    widths = {im.width for im in cropped}
    if len(widths) != 1:
        raise ValueError(f"Frames have different widths after cropping: {sorted(widths)}")

    total_h = sum(im.height for im in cropped) + gap_px * (len(cropped) - 1)
    out = Image.new("RGBA", (cropped[0].width, total_h), bg)

    y = 0
    for i, im in enumerate(cropped):
        out.paste(im, (0, y))
        y += im.height + (gap_px if i < len(cropped) - 1 else 0)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.save(out_path)
    return str(out_path)
frames_dir = Path("frames/")
paths = [frames_dir / f"frame_{i:02d}.png" for i in [1,2,3]]

stack_frames(
    paths,
    "frames/stack_123.png",
    drop_bottom_frac=0.14,  # tune this once
    drop_side_frac=0.0,
    gap_px=8
)
