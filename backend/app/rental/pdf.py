import io
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

class PdfService:

    _registered = False

    font_paths = [
        (
            r"C:\Windows\Fonts\times.ttf",
            r"C:\Windows\Fonts\timesbd.ttf",
        ),
        (
            "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman_Bold.ttf",
        ),
        (
            "/usr/share/fonts/truetype/msttcorefonts/times.ttf",
            "/usr/share/fonts/truetype/msttcorefonts/timesbd.ttf",
        ),
    ]

    @classmethod
    def register_fonts(cls):
        if cls._registered:
            return

        for regular, bold in cls.font_paths:
            if os.path.exists(regular) and os.path.exists(bold):
                pdfmetrics.registerFont(
                    TTFont("TimesNewRoman", regular)
                )
                pdfmetrics.registerFont(
                    TTFont("TimesNewRoman-Bold", bold)
                )

                cls._registered = True
                return

        raise RuntimeError(
            "Не найден Times New Roman. "
            "Проверьте наличие times.ttf и timesbd.ttf."
        )

    @classmethod
    def generate(cls, request) -> bytes:
        cls.register_fonts()

        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "Title",
            parent=styles["Normal"],
            fontName="TimesNewRoman-Bold",
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=10 * mm,
        )

        normal_style = ParagraphStyle(
            "NormalCustom",
            parent=styles["Normal"],
            fontName="TimesNewRoman",
            fontSize=11,
            leading=14,
            alignment=TA_LEFT,
        )

        bold_style = ParagraphStyle(
            "BoldCustom",
            parent=normal_style,
            fontName="TimesNewRoman-Bold",
        )

        small_style = ParagraphStyle(
            "Small",
            parent=normal_style,
            fontSize=9,
            leading=11,
        )

        story = []

        # --------------------------------------------------
        # Заголовок
        # --------------------------------------------------

        story.append(
            Paragraph(
                "ЗАЯВКА НА ВЫДАЧУ ОБОРУДОВАНИЯ",
                title_style,
            )
        )

        # --------------------------------------------------
        # Основная информация
        # --------------------------------------------------

        request_date = request.created_at.strftime("%d.%m.%Y")

        issue_date = (
            request.issue_date.strftime("%d.%m.%Y")
            if request.issue_date
            else "________________"
        )

        # Если у модели есть поле employee / issued_by
        # используем его. Если нет — оставляем пустым.
        issued_by = getattr(request, "issued_by", None)

        if issued_by:
            if hasattr(issued_by, "get_full_name"):
                issued_by_name = issued_by.get_full_name()

                if not issued_by_name:
                    issued_by_name = getattr(
                        issued_by,
                        "username",
                        str(issued_by),
                    )
            else:
                issued_by_name = str(issued_by)
        else:
            issued_by_name = "____________________________"

        info_data = [
            [
                Paragraph("<b>Дата заявки:</b>", normal_style),
                Paragraph(request_date, normal_style),
                Paragraph("<b>ФИО:</b>", normal_style),
                Paragraph(str(request.full_name), normal_style),
            ],
            [
                Paragraph("<b>Группа:</b>", normal_style),
                Paragraph(str(request.group), normal_style),
                Paragraph("<b>Дисциплина:</b>", normal_style),
                Paragraph(str(request.discipline), normal_style),
            ],
            [
                Paragraph("<b>Дата выдачи:</b>", normal_style),
                Paragraph(issue_date, normal_style),
                Paragraph("<b>Кто выдал:</b>", normal_style),
                Paragraph(issued_by_name, normal_style),
            ],
            [
                Paragraph("<b>Статус:</b>", normal_style),
                Paragraph(request.get_status_display(), normal_style),
                "",
                "",
            ],
        ]

        info_table = Table(
            info_data,
            colWidths=[
                32 * mm,
                65 * mm,
                32 * mm,
                41 * mm,
                ],
        )

        info_table.setStyle(
            TableStyle([
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ])
        )

        story.append(info_table)
        story.append(Spacer(1, 8 * mm))

        # --------------------------------------------------
        # Состав заявки
        # --------------------------------------------------

        story.append(
            Paragraph(
                "СОСТАВ ЗАЯВКИ",
                bold_style,
            )
        )

        story.append(Spacer(1, 3 * mm))

        table_data = [
            [
                Paragraph("<b>№</b>", normal_style),
                Paragraph("<b>Оборудование</b>", normal_style),
                Paragraph("<b>Количество</b>", normal_style),
                Paragraph("<b>Дата возврата</b>", normal_style),
            ]
        ]

        items = request.items.select_related("device")

        for index, item in enumerate(items, start=1):

            return_date = (
                item.return_date.strftime("%d.%m.%Y")
                if item.return_date
                else "—"
            )

            table_data.append([
                Paragraph(str(index), normal_style),
                Paragraph(
                    str(item.device.name),
                    normal_style,
                ),
                Paragraph(
                    str(item.quantity),
                    normal_style,
                ),
                Paragraph(
                    return_date,
                    normal_style,
                ),
            ])

        equipment_table = Table(
            table_data,
            colWidths=[
                12 * mm,
                95 * mm,
                30 * mm,
                33 * mm,
                ],
            repeatRows=1,
        )

        equipment_table.setStyle(
            TableStyle([
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    colors.black,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#eeeeee"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (0, -1),
                    "CENTER",
                ),
                (
                    "ALIGN",
                    (2, 0),
                    (3, -1),
                    "CENTER",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ])
        )

        story.append(equipment_table)

        story.append(Spacer(1, 15 * mm))

        # --------------------------------------------------
        # Примечание
        # --------------------------------------------------

        story.append(
            Paragraph(
                "Оборудование предоставляется студенту для использования "
                "в рамках учебной деятельности. Студент обязуется вернуть "
                "оборудование в установленный срок и в надлежащем состоянии.",
                normal_style,
            )
        )

        story.append(Spacer(1, 20 * mm))

        # --------------------------------------------------
        # Подписи
        # --------------------------------------------------

        signature_data = [
            [
                Paragraph(
                    "<b>Студент</b>",
                    normal_style,
                ),
                Paragraph(
                    "<b>Сотрудник лаборатории</b>",
                    normal_style,
                ),
            ],
            [
                Paragraph(
                    "____________________________",
                    normal_style,
                ),
                Paragraph(
                    "____________________________",
                    normal_style,
                ),
            ],
            [
                Paragraph(
                    f"({request.full_name})",
                    small_style,
                ),
                Paragraph(
                    f"({issued_by_name})",
                    small_style,
                ),
            ],
            [
                Paragraph(
                    "Дата: __________________",
                    small_style,
                ),
                Paragraph(
                    "Дата: __________________",
                    small_style,
                ),
            ],
        ]

        signature_table = Table(
            signature_data,
            colWidths=[
                85 * mm,
                85 * mm,
                ],
        )

        signature_table.setStyle(
            TableStyle([
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "LEFT",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ])
        )

        story.append(signature_table)

        doc.build(story)

        return buffer.getvalue()