import argparse
from pathlib import Path

from PIL import Image


def crop_x_range(image, left, right):
    if left < 0 or right > image.width or left >= right:
        raise ValueError(
            f"Invalid crop range [{left}, {right}] for image width {image.width}"
        )
    return image.crop((left, 0, right, image.height))


def stitch_columns(image_paths, out_path):
    if len(image_paths) != 3:
        raise ValueError("Expected exactly three stacked images")

    images = [Image.open(path).convert("RGBA") for path in image_paths]
    common_height = min(image.height for image in images)
    if common_height <= 0:
        raise ValueError("Images must have positive height")

    trimmed = [image.crop((0, 0, image.width, common_height)) for image in images]
    panels = [
        crop_x_range(trimmed[0], 0, 3253),
        crop_x_range(trimmed[1], 1625, 3253),
        crop_x_range(trimmed[2], 1625, 3253),
    ]

    total_width = sum(panel.width for panel in panels)
    out = Image.new("RGBA", (total_width, common_height), (255, 255, 255, 255))

    x = 0
    for panel in panels:
        out.paste(panel, (x, 0))
        x += panel.width

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.save(out_path)
    return str(out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("first", type=Path, help="First stacked image; keep x=[0, 3253]")
    parser.add_argument(
        "second",
        type=Path,
        help="Second stacked image; keep x=[1625, 3253]",
    )
    parser.add_argument(
        "third",
        type=Path,
        help="Third stacked image; keep x=[1625, 3253]",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("stacked_columns.png"),
        help="Output path for the stitched image",
    )
    args = parser.parse_args()

    stitch_columns([args.first, args.second, args.third], args.output)


if __name__ == "__main__":
    main()
