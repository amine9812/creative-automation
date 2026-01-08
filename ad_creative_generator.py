import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
)
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import TextClip, concatenate_videoclips


class AdCreativeGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ad Creative Generator")
        self.setFixedSize(400, 300)  # set a reasonable window size

        # Create widgets
        self.name_label = QLabel("Product Name:")
        self.name_edit = QLineEdit()
        self.desc_label = QLabel("Product Description:")
        self.desc_edit = QTextEdit()
        self.btn_image = QPushButton("Generate Image Ad")
        self.btn_video = QPushButton("Generate Video Ad")

        # Connect button signals to handler methods
        self.btn_image.clicked.connect(self.generate_image_ad)
        self.btn_video.clicked.connect(self.generate_video_ad)

        # Layout setup
        main_layout = QVBoxLayout()
        # Row for product name
        name_layout = QHBoxLayout()
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_edit)
        main_layout.addLayout(name_layout)
        # Row for description label
        main_layout.addWidget(self.desc_label)
        # Row for description text edit
        main_layout.addWidget(self.desc_edit)
        # Row for buttons
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_image)
        btn_layout.addWidget(self.btn_video)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def _generate_tagline(self, description: str) -> str:
        """Derive a short tagline from the product description."""
        if not description:
            return ""
        desc = description.strip()
        # Find the end of the first sentence or phrase
        end_idx = -1
        for punct in ".!?":
            pos = desc.find(punct)
            if pos != -1:
                end_idx = pos
                break
        tagline = desc if end_idx == -1 else desc[:end_idx]
        tagline = tagline.strip()
        # Truncate to at most 12 words for brevity
        words = tagline.split()
        if len(words) > 12:
            tagline = " ".join(words[:12]) + "..."
        return tagline

    def generate_image_ad(self):
        # Get inputs
        product_name = self.name_edit.text().strip()
        product_desc = self.desc_edit.toPlainText().strip()
        if not product_name or not product_desc:
            QMessageBox.warning(
                self,
                "Input Required",
                "Please enter both Product Name and Description.",
            )
            return

        tagline = self._generate_tagline(product_desc)
        try:
            # Create a blank white image
            img = Image.new("RGB", (1080, 1080), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            # Load fonts (try a common font, fallback to default)
            try:
                # Try Arial or a similar font
                font_head = ImageFont.truetype("arial.ttf", 80)
            except Exception:
                font_head = ImageFont.load_default()
            try:
                font_tag = ImageFont.truetype("arial.ttf", 50)
            except Exception:
                font_tag = ImageFont.load_default()
            # Determine text positions for centering
            # Headline (product name) at top center
            text = product_name
            w_head, h_head = draw.textsize(text, font=font_head)
            x_head = (1080 - w_head) / 2
            y_head = 50  # 50px from top edge as a margin
            draw.text((x_head, y_head), text, font=font_head, fill=(0, 0, 0))
            # Tagline beneath headline, if available
            if tagline:
                w_tag, h_tag = draw.textsize(tagline, font=font_tag)
                x_tag = (1080 - w_tag) / 2
                y_tag = y_head + h_head + 20  # 20px below headline
                draw.text((x_tag, y_tag), tagline, font=font_tag, fill=(0, 0, 0))
            # Save image to file
            img.save("ad_creative_image.png")
            QMessageBox.information(
                self, "Image Ad Created", "Image ad saved as 'ad_creative_image.png'."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create image ad:\n{e}")

    def generate_video_ad(self):
        # Get inputs
        product_name = self.name_edit.text().strip()
        product_desc = self.desc_edit.toPlainText().strip()
        if not product_name or not product_desc:
            QMessageBox.warning(
                self,
                "Input Required",
                "Please enter both Product Name and Description.",
            )
            return

        tagline = self._generate_tagline(product_desc)
        try:
            # Define font settings for moviepy TextClip
            # Try to find a common font that moviepy can use
            font_choice = "Arial"  # font name (needs to be installed on system)
            fontsize_head = 70
            fontsize_tag = 60
            fontsize_cta = 70

            # Create three text clips (white text on black background)
            clip1 = TextClip(
                product_name,
                fontsize=fontsize_head,
                color="white",
                size=(1080, 1080),
                bg_color="black",
                method="caption",
                align="center",
            )
            clip1 = clip1.set_duration(4)
            clip2_text = tagline if tagline else ""  # if no tagline, use empty text
            clip2 = TextClip(
                clip2_text,
                fontsize=fontsize_tag,
                color="white",
                size=(1080, 1080),
                bg_color="black",
                method="caption",
                align="center",
            )
            clip2 = clip2.set_duration(4)
            clip3 = TextClip(
                "Buy Now",
                fontsize=fontsize_cta,
                color="white",
                size=(1080, 1080),
                bg_color="black",
                method="caption",
                align="center",
            )
            clip3 = clip3.set_duration(4)

            # Concatenate clips into one video
            final_clip = concatenate_videoclips([clip1, clip2, clip3])
            # Write the video file (12 seconds, 1080x1080)
            final_clip.write_videofile(
                "ad_creative_video.mp4", codec="libx264", fps=24, audio=False
            )
            final_clip.close()  # close the clip to release resources
            # Notify user
            QMessageBox.information(
                self, "Video Ad Created", "Video ad saved as 'ad_creative_video.mp4'."
            )
        except Exception as e:
            # If text generation fails (e.g., missing ImageMagick), show error
            QMessageBox.critical(self, "Error", f"Failed to create video ad:\n{e}")


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdCreativeGenerator()
    window.show()
    sys.exit(app.exec_())
