from PIL import Image, ImageDraw, ImageFont
import io
from data_model import CVData

font_name = ImageFont.truetype("fonts/Exo2-Regular.ttf", size=36)
font_regular = ImageFont.truetype("fonts/Nunito-Regular.ttf", size=24)

def create_cv_pdf(cv_data: CVData) -> bytes:
    template = Image.open("templates/cv_template.png")
    draw = ImageDraw.Draw(template)

    name_x, name_y = 200, 50
    draw.text((name_x, name_y), cv_data.name, font=font_name, fill=(0, 0, 0))

    coords = {
        'position': (260, 160),
        'languages': (260, 250),
        'about': (260, 345),
        'education': (260, 442),
        'skills': (260, 538),
        'experience': (260, 633),
        'contacts': (260, 729)
    }

    draw.text(coords['position'], cv_data.position, font=font_regular, fill=(0, 0, 0))
    draw.text(coords['languages'], cv_data.languages, font=font_regular, fill=(0, 0, 0))
    draw.text(coords['about'], cv_data.about, font=font_regular, fill=(0, 0, 0))
    draw.text(coords['education'], cv_data.education, font=font_regular, fill=(0, 0, 0))
    draw.text(coords['skills'], cv_data.skills, font=font_regular, fill=(0, 0, 0))
    draw.text(coords['experience'], cv_data.experience, font=font_regular, fill=(0, 0, 0))
    draw.text(coords['contacts'], cv_data.contacts, font=font_regular, fill=(0, 0, 0))

    pdf_bytes = io.BytesIO()
    template.save(pdf_bytes, format='PDF', resolution=100.0)
    return pdf_bytes.getvalue()
