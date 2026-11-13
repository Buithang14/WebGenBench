from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def generate_reference_login_image(output_path: Path):
    width, height = 1440, 900
    img = Image.new("RGB", (width, height), color="#F3F4F6")
    draw = ImageDraw.Draw(img)

    # Card dimensions
    card_w, card_h = 460, 560
    card_x = (width - card_w) // 2
    card_y = (height - card_h) // 2

    # Draw card shadow
    for offset in range(8, 0, -2):
        draw.rounded_rectangle(
            [card_x - offset, card_y - offset, card_x + card_w + offset, card_y + card_h + offset],
            radius=16,
            fill="#E5E7EB",
        )

    # Draw card background
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=16,
        fill="#FFFFFF",
        outline="#E5E7EB",
        width=1,
    )

    # Fonts
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 26)
        font_sub = ImageFont.truetype("arial.ttf", 14)
        font_label = ImageFont.truetype("arialbd.ttf", 13)
        font_input = ImageFont.truetype("arial.ttf", 14)
        font_btn = ImageFont.truetype("arialbd.ttf", 15)
    except Exception:
        font_title = font_sub = font_label = font_input = font_btn = ImageFont.load_default()

    # 1. Title & Subtitle
    draw.text((card_x + 40, card_y + 45), "Welcome Back", fill="#111827", font=font_title)
    draw.text((card_x + 40, card_y + 82), "Please enter your details to sign in.", fill="#6B7280", font=font_sub)

    # 2. Email Field
    y_email = card_y + 130
    draw.text((card_x + 40, y_email), "Email address", fill="#374151", font=font_label)
    input_w = card_w - 80
    draw.rounded_rectangle([card_x + 40, y_email + 24, card_x + 40 + input_w, y_email + 70], radius=8, fill="#F9FAFB", outline="#D1D5DB", width=1)
    draw.text((card_x + 55, y_email + 38), "name@example.com", fill="#9CA3AF", font=font_input)

    # 3. Password Field
    y_pass = card_y + 225
    draw.text((card_x + 40, y_pass), "Password", fill="#374151", font=font_label)
    draw.rounded_rectangle([card_x + 40, y_pass + 24, card_x + 40 + input_w, y_pass + 70], radius=8, fill="#F9FAFB", outline="#D1D5DB", width=1)
    draw.text((card_x + 55, y_pass + 40), "••••••••••••", fill="#4B5563", font=font_input)
    # Eye icon placeholder
    draw.text((card_x + 40 + input_w - 45, y_pass + 38), "[O]", fill="#6B7280", font=font_sub)

    # 4. Remember me & Forgot password
    y_opts = card_y + 325
    draw.rounded_rectangle([card_x + 40, y_opts, card_x + 58, y_opts + 18], radius=4, fill="#2563EB", outline="#2563EB")
    draw.text((card_x + 44, y_opts + 2), "v", fill="#FFFFFF", font=font_sub)
    draw.text((card_x + 68, y_opts + 1), "Remember for 30 days", fill="#4B5563", font=font_sub)
    draw.text((card_x + 40 + input_w - 110, y_opts + 1), "Forgot password?", fill="#2563EB", font=font_sub)

    # 5. Sign In button
    y_btn = card_y + 375
    draw.rounded_rectangle([card_x + 40, y_btn, card_x + 40 + input_w, y_btn + 50], radius=8, fill="#2563EB", outline=None)
    draw.text((card_x + 195, y_btn + 15), "Sign In", fill="#FFFFFF", font=font_btn)

    # 6. Footer text
    y_footer = card_y + 465
    draw.text((card_x + 95, y_footer), "Don't have an account?", fill="#6B7280", font=font_sub)
    draw.text((card_x + 250, y_footer), "Sign up for free", fill="#2563EB", font=font_label)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path))
    print(f"Generated {output_path} successfully with dimensions {img.size}")


if __name__ == "__main__":
    out_file = Path(__file__).resolve().parent / "T01_reference.png"
    generate_reference_login_image(out_file)

