import argparse
from pathlib import Path

from PIL import Image


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

        dx = int(round(drop_side_frac * w))
        left = dx
        right = w - dx

        is_last = i == len(ims) - 1
        if keep_colorbar_on_last and is_last:
            bottom = h
        else:
            dy = int(round(drop_bottom_frac * h))
            bottom = max(1, h - dy)

        im2 = im.crop((left, 0, right, bottom))
        cropped.append(im2)

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


def select_frame_paths(frames_dir, *, start_name="frame_04.png", step=5, limit=3):
    frames_dir = Path(frames_dir)
    frame_paths = sorted(frames_dir.glob("frame_*.png"))
    if not frame_paths:
        raise FileNotFoundError(f"No frame_*.png files found in {frames_dir}")

    frame_names = [path.name for path in frame_paths]
    if start_name not in frame_names:
        raise FileNotFoundError(f"{start_name} not found in {frames_dir}")

    start_index = frame_names.index(start_name)
    selected = frame_paths[start_index::step]
    return selected[:limit] if limit is not None else selected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("frames_dir", type=Path, help="Directory containing frame_*.png files")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output path for the stacked image (default: <frames_dir>/stack.png)",
    )
    args = parser.parse_args()

    frame_paths = select_frame_paths(args.frames_dir)
    out_path = args.output or args.frames_dir / "stack.png"

    stack_frames(
        frame_paths,
        out_path,
        drop_bottom_frac=0.14,
        drop_side_frac=0.0,
        gap_px=8,
    )


if __name__ == "__main__":
    main()
