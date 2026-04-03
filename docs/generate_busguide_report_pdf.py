# -*- coding: utf-8 -*-
"""
BusGuide 캡스톤 발표 보고서 PDF 생성 스크립트
reportlab + 맑은고딕 한글 폰트 사용
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import Flowable
import os

# ── 한글 폰트 등록 ──
FONT_PATH = "C:/Windows/Fonts/malgun.ttf"
FONT_BOLD_PATH = "C:/Windows/Fonts/malgunbd.ttf"
pdfmetrics.registerFont(TTFont("Malgun", FONT_PATH))
pdfmetrics.registerFont(TTFont("MalgunBold", FONT_BOLD_PATH))

# ── 색상 정의 (BusGuide 시니어 테마 반영) ──
PRIMARY = HexColor("#FF6F00")       # 주황 (시니어 친화적 따뜻한 색)
DARK = HexColor("#1A1A1A")          # 고대비 배경색
ACCENT = HexColor("#E94560")        # 강조색
TEAL = HexColor("#00897B")          # 보조색
SENIOR_YELLOW = HexColor("#FFF176") # 시니어 UX 노란색
LIGHT_BG = HexColor("#FFF8E1")      # 연한 노란 배경
LIGHT_GRAY = HexColor("#F5F5F5")
MID_GRAY = HexColor("#E0E0E0")
TEXT_GRAY = HexColor("#555555")

# ── 스타일 정의 ──
def make_styles():
    s = {}
    s['cover_title'] = ParagraphStyle('CoverTitle', fontName='MalgunBold', fontSize=28,
        textColor=white, alignment=TA_CENTER, leading=36, spaceAfter=8)
    s['cover_sub'] = ParagraphStyle('CoverSub', fontName='Malgun', fontSize=14,
        textColor=HexColor("#FFD180"), alignment=TA_CENTER, leading=20)
    s['cover_info'] = ParagraphStyle('CoverInfo', fontName='Malgun', fontSize=11,
        textColor=HexColor("#FFB74D"), alignment=TA_CENTER, leading=16)

    s['h1'] = ParagraphStyle('H1', fontName='MalgunBold', fontSize=20,
        textColor=PRIMARY, spaceBefore=20, spaceAfter=10, leading=26,
        borderPadding=(0, 0, 4, 0))
    s['h2'] = ParagraphStyle('H2', fontName='MalgunBold', fontSize=14,
        textColor=DARK, spaceBefore=14, spaceAfter=6, leading=20)
    s['h3'] = ParagraphStyle('H3', fontName='MalgunBold', fontSize=12,
        textColor=TEAL, spaceBefore=10, spaceAfter=4, leading=16)

    s['body'] = ParagraphStyle('Body', fontName='Malgun', fontSize=10,
        textColor=black, leading=16, spaceAfter=4, alignment=TA_JUSTIFY)
    s['body_sm'] = ParagraphStyle('BodySm', fontName='Malgun', fontSize=9,
        textColor=TEXT_GRAY, leading=14, spaceAfter=2)
    s['bullet'] = ParagraphStyle('Bullet', fontName='Malgun', fontSize=10,
        textColor=black, leading=16, spaceAfter=2, leftIndent=16,
        bulletIndent=4, bulletFontSize=10)
    s['code'] = ParagraphStyle('Code', fontName='Courier', fontSize=8.5,
        textColor=HexColor("#333333"), leading=12, spaceAfter=2,
        backColor=LIGHT_GRAY, borderPadding=4, leftIndent=8)
    s['code_kr'] = ParagraphStyle('CodeKR', fontName='Malgun', fontSize=8.5,
        textColor=HexColor("#333333"), leading=12, spaceAfter=2,
        backColor=LIGHT_GRAY, borderPadding=4, leftIndent=8)

    s['th'] = ParagraphStyle('TH', fontName='MalgunBold', fontSize=9,
        textColor=white, alignment=TA_CENTER, leading=13)
    s['td'] = ParagraphStyle('TD', fontName='Malgun', fontSize=9,
        textColor=black, leading=13)
    s['td_c'] = ParagraphStyle('TDC', fontName='Malgun', fontSize=9,
        textColor=black, alignment=TA_CENTER, leading=13)
    s['caption'] = ParagraphStyle('Caption', fontName='Malgun', fontSize=8,
        textColor=TEXT_GRAY, alignment=TA_CENTER, leading=12, spaceAfter=8)
    s['page_num'] = ParagraphStyle('PageNum', fontName='Malgun', fontSize=8,
        textColor=TEXT_GRAY, alignment=TA_CENTER)

    s['formula'] = ParagraphStyle('Formula', fontName='MalgunBold', fontSize=11,
        textColor=ACCENT, alignment=TA_CENTER, leading=18, spaceAfter=4,
        backColor=HexColor("#FFF0F3"), borderPadding=8)

    s['toc_item'] = ParagraphStyle('TOCItem', fontName='Malgun', fontSize=11,
        textColor=DARK, leading=22, leftIndent=8)

    s['demo'] = ParagraphStyle('Demo', fontName='Malgun', fontSize=10,
        textColor=HexColor("#333333"), leading=16, spaceAfter=2,
        backColor=HexColor("#FFFDE7"), borderPadding=8, leftIndent=12)
    return s

S = make_styles()

# ── 헬퍼 함수들 ──
def heading1(text):
    return Paragraph(text, S['h1'])

def heading2(text):
    return Paragraph(text, S['h2'])

def heading3(text):
    return Paragraph(text, S['h3'])

def body(text):
    return Paragraph(text, S['body'])

def body_sm(text):
    return Paragraph(text, S['body_sm'])

def bullet(text):
    return Paragraph(f"<bullet>&bull;</bullet> {text}", S['bullet'])

def code_line(text):
    import re
    if re.search(r'[\uac00-\ud7af\u3131-\u3163\u3200-\u321e]', text):
        return Paragraph(text, S['code_kr'])
    return Paragraph(text, S['code'])

def code_kr(text):
    return Paragraph(text, S['code_kr'])

def formula(text):
    return Paragraph(text, S['formula'])

def demo_line(text):
    return Paragraph(text, S['demo'])

def spacer(h=6):
    return Spacer(1, h)

def hr():
    return HRFlowable(width="100%", thickness=1, color=MID_GRAY, spaceBefore=6, spaceAfter=6)

def make_table(headers, rows, col_widths=None):
    """테이블 생성 헬퍼"""
    header_cells = [Paragraph(h, S['th']) for h in headers]
    data = [header_cells]
    for row in rows:
        data.append([Paragraph(str(c), S['td']) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Malgun'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.5, MID_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return t


def draw_cover_page(canvas, doc):
    """표지를 onFirstPage 콜백으로 그림"""
    c = canvas
    w, h = A4

    # 배경 그라데이션 효과 (시니어 따뜻한 톤)
    c.setFillColor(HexColor("#1A1A1A"))
    c.rect(0, 0, w, h, fill=1, stroke=0)
    c.setFillColor(HexColor("#2D1B00"))
    c.rect(0, h * 0.3, w, h * 0.7, fill=1, stroke=0)
    c.setFillColor(HexColor("#FF6F00"))
    c.rect(0, h * 0.55, w, h * 0.45, fill=1, stroke=0)

    # 장식 라인
    c.setStrokeColor(HexColor("#FFB74D"))
    c.setLineWidth(2)
    c.line(w * 0.15, h * 0.48, w * 0.85, h * 0.48)

    # 타이틀
    c.setFont("MalgunBold", 32)
    c.setFillColor(white)
    c.drawCentredString(w / 2, h * 0.72, "BusGuide")

    c.setFont("Malgun", 15)
    c.setFillColor(HexColor("#FFD180"))
    c.drawCentredString(w / 2, h * 0.65, "\uc5b4\ub974\uc2e0 \uc74c\uc131 \uae30\ubc18 \ubc84\uc2a4 \uc548\ub0b4 \uc2dc\uc2a4\ud15c")

    c.setFont("Malgun", 11)
    c.setFillColor(HexColor("#FFB74D"))
    c.drawCentredString(w / 2, h * 0.59,
        "\uc74c\uc131 \uc9c8\uc758 \u2192 \uc0ac\ud22c\ub9ac \ubcc0\ud658 \u2192 NLP \uc758\ub3c4 \ud30c\uc545 \u2192 \uc2e4\uc2dc\uac04 \ubc84\uc2a4 \uc548\ub0b4")

    # 하단 정보
    c.setFont("MalgunBold", 13)
    c.setFillColor(white)
    c.drawCentredString(w / 2, h * 0.28, "\uce85\uc2a4\ud1a4 \ub514\uc790\uc778 \ud504\ub85c\uc81d\ud2b8 \ubc1c\ud45c \ubcf4\uace0\uc11c")

    c.setFont("Malgun", 11)
    c.setFillColor(HexColor("#FFB74D"))
    c.drawCentredString(w / 2, h * 0.22, "\uac1c\ubc1c\uc790: \ud604\uc218")
    c.drawCentredString(w / 2, h * 0.18, "2026\ub144 4\uc6d4")

    c.setFont("Malgun", 9)
    c.setFillColor(HexColor("#CC8A00"))
    c.drawCentredString(w / 2, h * 0.10,
        "Kotlin \xb7 Jetpack Compose \xb7 FastAPI \xb7 Kiwi NLP \xb7 TAGO API \xb7 Hilt \xb7 Retrofit")


# ══════════════════════════════════════════════════════════════
# PDF 본문 구성
# ══════════════════════════════════════════════════════════════

def build_pdf():
    output_path = os.path.join(os.path.dirname(__file__), "BusGuide_\ubc1c\ud45c\ubcf4\uace0\uc11c.pdf")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm
    )

    pw = A4[0] - 4.4 * cm  # 사용 가능 폭
    story = []

    # ══════════════════════════════
    # 표지 — onFirstPage 콜백으로 그림
    # ══════════════════════════════
    story.append(PageBreak())

    # ══════════════════════════════
    # 목차
    # ══════════════════════════════
    story.append(heading1("\ubaa9\ucc28"))
    story.append(hr())
    toc_items = [
        "1. \ud504\ub85c\uc81d\ud2b8 \uac1c\uc694",
        "2. \ubb38\uc81c \uc815\uc758 \u2014 \ub514\uc9c0\ud138 \uc18c\uc678 \ubb38\uc81c",
        "3. \uc194\ub8e8\uc158 \uc18c\uac1c \ubc0f \ud575\uc2ec \uae30\ub2a5",
        "4. \uc2dc\uc2a4\ud15c \uc544\ud0a4\ud14d\ucc98",
        "5. \uae30\uc220 \uc2a4\ud0dd \ubc0f \uc120\ud0dd \uadfc\uac70",
        "6. \ud575\uc2ec \uae30\uc220 \u2014 NLP \ud30c\uc774\ud504\ub77c\uc778",
        "7. \ubf08\ub300 \ucf54\ub4dc (\ud575\uc2ec \ubc1c\ucde8)",
        "8. \ucc28\ubcc4\ud654 \ubd84\uc11d \u2014 \uae30\uc874 \uc194\ub8e8\uc158\uacfc \ube44\uad50",
        "9. \uc5d0\ub7ec \ud578\ub4e4\ub9c1 & \uc5e3\uc9c0 \ucf00\uc774\uc2a4",
        "10. \ud14c\uc2a4\ud2b8 \uc804\ub7b5 \ubc0f \uacb0\uacfc",
        "11. \ud654\uba74 \ud750\ub984 & \uc2dc\ub2c8\uc5b4 UX \uc124\uacc4",
        "12. \ud558\ub4dc\uc6e8\uc5b4 \uad6c\uc131 \ubc0f \ube44\uc6a9",
        "13. \uc644\uc131\ub3c4 \ud3c9\uac00 & \ud5a5\ud6c4 \ubc1c\uc804 \ubc29\ud5a5",
    ]
    for item in toc_items:
        story.append(Paragraph(item, S['toc_item']))
    story.append(PageBreak())

    # ══════════════════════════════
    # 1. 프로젝트 개요
    # ══════════════════════════════
    story.append(heading1("1. \ud504\ub85c\uc81d\ud2b8 \uac1c\uc694"))
    story.append(hr())
    story.append(body(
        "<b>BusGuide</b>\ub294 \ub514\uc9c0\ud138 \uc18c\uc678 \uacc4\uce35(70\ub300 \uc774\uc0c1)\uc744 \uc704\ud55c "
        "<b>\uc74c\uc131 \uae30\ubc18 \ubc84\uc2a4 \uc548\ub0b4 \ud0dc\ube14\ub9bf \ud0a4\uc624\uc2a4\ud06c</b>\uc785\ub2c8\ub2e4."
    ))
    story.append(spacer(4))
    story.append(body(
        "\uc815\ub958\uc7a5\uc5d0 \uc124\uce58\ub41c \ud0dc\ube14\ub9bf\uc5d0 <b>\"\uba85\uc9c0\ubcd1\uc6d0 \uac00\ub294 \ubc84\uc2a4 \uc788\uc5b4\uc694?\"</b>\ub77c\uace0 "
        "\ub9d0\ud558\uba74 <b>\"\u0035\u0038\ubc88 \ubc84\uc2a4\uac00 5\ubd84 \ud6c4\uc5d0 \uc635\ub2c8\ub2e4\"</b>\ub77c\uace0 "
        "\uc74c\uc131+\ud654\uba74\uc73c\ub85c \uc548\ub0b4\ud574\uc8fc\ub294 \uc2dc\uc2a4\ud15c\uc785\ub2c8\ub2e4. "
        "\ubd80\uc0b0 \uc0ac\ud22c\ub9ac \uc778\uc2dd\uacfc \uc5f0\uc18d \ub300\ud654 \uae30\ub2a5\uc744 \uc9c1\uc811 \uad6c\ud604\ud55c NLP \uc5d4\uc9c4\uc744 \ud0d1\uc7ac\ud588\uc2b5\ub2c8\ub2e4."
    ))
    story.append(spacer(8))

    overview_data = [
        ["\ud504\ub85c\uc81d\ud2b8\uba85", "BusGuide (\uc5b4\ub974\uc2e0 \uc74c\uc131 \uae30\ubc18 \ubc84\uc2a4 \uc548\ub0b4 \uc2dc\uc2a4\ud15c)"],
        ["\uac1c\ubc1c \uc5b8\uc5b4", "Kotlin (Android) + Python (FastAPI \uc11c\ubc84)"],
        ["UI \ud504\ub808\uc784\uc6cc\ud06c", "Jetpack Compose (Material Design 3)"],
        ["\uc544\ud0a4\ud14d\ucc98", "Simple Client + Clean Architecture (Android) + FastAPI (Server)"],
        ["\ud575\uc2ec \uae30\uc220", "Google STT/TTS, Kiwi NLP, TAGO API, Hilt, Retrofit"],
        ["\ud0c0\uac9f \ud50c\ub7ab\ud3fc", "Android 10.4\uc778\uce58 \ud0dc\ube14\ub9bf (\uc815\ub958\uc7a5 \uc124\uce58\ud615 \ud0a4\uc624\uc2a4\ud06c)"],
        ["\ud328\ud0a4\uc9c0\uba85", "com.hyeonsu.busguide"],
    ]
    t = Table(
        [[Paragraph(r[0], S['td']), Paragraph(r[1], S['td'])] for r in overview_data],
        colWidths=[pw * 0.3, pw * 0.7]
    )
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Malgun'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (0, -1), LIGHT_BG),
        ('FONTNAME', (0, 0), (0, -1), 'MalgunBold'),
        ('GRID', (0, 0), (-1, -1), 0.5, MID_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t)
    story.append(PageBreak())

    # ══════════════════════════════
    # 2. 문제 정의
    # ══════════════════════════════
    story.append(heading1("2. \ubb38\uc81c \uc815\uc758 \u2014 \ub514\uc9c0\ud138 \uc18c\uc678 \ubb38\uc81c"))
    story.append(hr())

    story.append(heading2("2-1. \ub514\uc9c0\ud138 \uc18c\uc678 \ud604\ud669"))
    story.append(body(
        "\ubd80\uc0b0\uc2dc 70\ub300 \uc774\uc0c1 \uc778\uad6c\ub294 <b>35\ub9cc \uba85</b>\uc774\uba70, "
        "\uc774 \uc911 \uc2a4\ub9c8\ud2b8\ud3f0 \ubbf8\uc0ac\uc6a9\uc790\ub294 <b>24\ub9cc \uba85(68%)</b>\uc785\ub2c8\ub2e4. "
        "\ubc84\uc2a4 \uc571\uc744 \uc0ac\uc6a9\ud560 \uc218 \uc788\ub294 70\ub300\ub294 <b>\uaca8\uc6b0 12%</b>\uc5d0 \ubd88\uacfc\ud569\ub2c8\ub2e4."
    ))
    story.append(spacer())

    story.append(heading2("2-2. \ud604\uc7a5\uc758 \ubd88\ud3b8\ud568"))
    story.append(body(
        "\uc5b4\ub974\uc2e0\ub4e4\uc774 \ub9e4\ubc88 \uae30\uc0ac\ub2d8\uaed8 \"\uc5b4\ub514 \uac00\uc694?\"\ub77c\uace0 \ubb3c\uc5b4\ubcf4\ub294 \uac83\uc774 \ud604\uc2e4\uc785\ub2c8\ub2e4. "
        "\uc6b4\uc804 \uc911 \uae30\uc0ac \ubc29\ud574\ub294 <b>\uc548\uc804 \ubb38\uc81c</b>\ub85c \uc774\uc5b4\uc9c0\uba70, "
        "\uae30\uc874 BIS \uc804\uad11\ud310\uc740 \ub178\uc120\ubc88\ud638\ub9cc \ud45c\uc2dc\ud560 \ubfd0 <b>\ubaa9\uc801\uc9c0 \uc548\ub0b4 \uae30\ub2a5\uc774 \uc5c6\uc2b5\ub2c8\ub2e4.</b>"
    ))
    story.append(spacer())

    story.append(heading2("2-3. \uae30\uc874 \uc194\ub8e8\uc158\uc758 \ud55c\uacc4"))
    story.append(body(
        "\uce74\uce74\uc624\ub9f5, \ub124\uc774\ubc84 \uc9c0\ub3c4 \ub4f1 \ubc84\uc2a4 \uc571\uc740 "
        "<b>\uc2a4\ub9c8\ud2b8\ud3f0 \uc0ac\uc6a9\uc774 \uac00\ub2a5\ud55c \uc0ac\ub78c</b>\uc744 \uc804\uc81c\ub85c \uc124\uacc4\ub418\uc5c8\uc2b5\ub2c8\ub2e4. "
        "\uc571 \uc124\uce58, \uac80\uc0c9\uc5b4 \uc785\ub825, \uc791\uc740 \uae00\uc528 \uc77d\uae30 \ub4f1 \ubaa8\ub4e0 \uacfc\uc815\uc774 "
        "\ub514\uc9c0\ud138 \uc18c\uc678 \uacc4\uce35\uc5d0\uac8c\ub294 <b>\ub192\uc740 \uc9c4\uc785\uc7a5\ubcbd</b>\uc785\ub2c8\ub2e4."
    ))
    story.append(spacer())

    story.append(heading2("2-4. \uc6b0\ub9ac\uac00 \ud574\uacb0\ud558\ub824\ub294 \uac83"))
    story.append(body(
        "<b>\uc2a4\ub9c8\ud2b8\ud3f0\uc744 \ubabb \uc4f0\ub294 \uc5b4\ub974\uc2e0\ub3c4 \uc74c\uc131\uc73c\ub85c \ubc84\uc2a4 \uc815\ubcf4\ub97c \uc5bb\uc744 \uc218 \uc788\uac8c.</b> "
        "\uc815\ub958\uc7a5 \ud0dc\ube14\ub9bf\uc5d0 \ub9d0\ub9cc \ud558\uba74 \ub418\ub294 \uc2dc\uc2a4\ud15c\uc73c\ub85c, "
        "\uc571 \uc124\uce58, \ud68c\uc6d0\uac00\uc785, \uac80\uc0c9\uc5b4 \uc785\ub825 \uc5c6\uc774 \uc0ac\uc6a9\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4."
    ))
    story.append(PageBreak())

    # ══════════════════════════════
    # 3. 솔루션 소개 및 핵심 기능
    # ══════════════════════════════
    story.append(heading1("3. \uc194\ub8e8\uc158 \uc18c\uac1c \ubc0f \ud575\uc2ec \uae30\ub2a5"))
    story.append(hr())

    story.append(heading2("3-1. \ud575\uc2ec \uae30\ub2a5 5\uac00\uc9c0"))
    story.append(make_table(
        ["\uae30\ub2a5", "\uc124\uba85"],
        [
            ["\uc74c\uc131 \uc9c8\uc758 \u2192 \uc74c\uc131+\ud654\uba74 \ub2f5\ubcc0", "\ub9d0\ub9cc \ud558\uba74 \ub05d \u2014 STT\ub85c \uc778\uc2dd\ud558\uace0 TTS+\ud654\uba74\uc73c\ub85c \uc751\ub2f5"],
            ["\uc5f0\uc18d \ub300\ud654", "\"\uac70\uae30\uc11c \ud574\uc6b4\ub300 \uac00\ub824\uba74?\" \u2014 \uc774\uc804 \ub9e5\ub77d \uae30\uc5b5 (\ucee8\ud14d\uc2a4\ud2b8 \uc11c\ube44\uc2a4)"],
            ["\ubd80\uc0b0 \uc0ac\ud22c\ub9ac \uc778\uc2dd", "\"\uc5b4\ub370 \uce74\ub294 \ubc84\uc2a4\uc608\uc694?\" \u2014 19\uac1c \uc0ac\ud22c\ub9ac \uc790\ub3d9 \ubcc0\ud658"],
            ["\ud130\uce58 \ubc31\uc5c5", "\uc74c\uc131 \uc2e4\ud328 \uc2dc 3\ucd08 \ud6c4 \uc790\ub3d9\uc73c\ub85c \ud070 \ubc84\ud2bc \ud654\uba74 \uc804\ud658"],
            ["\uc2dc\ub2c8\uc5b4 \ud2b9\ud654 UX", "48pt \ud3f0\ud2b8, 120dp \ubc84\ud2bc, \uace0\ub300\ube44 \uc0c9\uc0c1, \uc0bc\uc911 \ud53c\ub4dc\ubc31"],
        ],
        col_widths=[pw * 0.3, pw * 0.7]
    ))
    story.append(spacer(8))

    story.append(heading2("3-2. \ub370\ubaa8 \uc2dc\ub098\ub9ac\uc624"))
    demo_lines = [
        "<b>\uc5b4\ub974\uc2e0:</b> [\ub9d0\ud558\uae30 \ubc84\ud2bc \ud130\uce58]",
        "<b>\uc2dc\uc2a4\ud15c:</b> \"\uc5b4\ub514 \uac00\uc2dc\ub824\uace0\uc694?\"",
        "",
        "<b>\uc5b4\ub974\uc2e0:</b> \"\uba85\uc9c0\ubcd1\uc6d0 \uce74\ub294 \ubc84\uc2a4 \uc788\ub098\uc608?\"",
        "<b>\uc2dc\uc2a4\ud15c:</b> (\uc0ac\ud22c\ub9ac \uc790\ub3d9 \ubcc0\ud658: \uce74\ub294\u2192\uac00\ub294, \uc788\ub098\uc608\u2192\uc788\ub098\uc694)",
        "         \"\uba85\uc9c0\ubcd1\uc6d0 \uac00\uc2dc\ub824\uba74 58\ubc88 \ubc84\uc2a4 \ud0c0\uc2dc\uba74 \ub429\ub2c8\ub2e4. 5\ubd84 \ud6c4 \ub3c4\ucc29 \uc608\uc815\uc785\ub2c8\ub2e4.\"",
        "",
        "<b>\uc5b4\ub974\uc2e0:</b> \"\uac70\uae30\uc11c \ud574\uc6b4\ub300 \uac00\ub824\uba74?\"",
        "<b>\uc2dc\uc2a4\ud15c:</b> (\ucee8\ud14d\uc2a4\ud2b8: \uba85\uc9c0\ubcd1\uc6d0 \uae30\uc5b5)",
        "         \"181\ubc88 \ubc84\uc2a4\ub85c \uac08\uc544\ud0c0\uc2dc\uba74 \ud574\uc6b4\ub300\uc5d0 \uac08 \uc218 \uc788\uc2b5\ub2c8\ub2e4.\"",
    ]
    for line in demo_lines:
        if line:
            story.append(demo_line(line))
        else:
            story.append(spacer(4))
    story.append(spacer(8))

    story.append(heading2("3-3. \ucd94\uac00 \uae30\ub2a5"))
    story.append(make_table(
        ["\uae30\ub2a5", "\uc124\uba85"],
        [
            ["\ud0a4\uc624\uc2a4\ud06c \ubaa8\ub4dc", "\uc0c1\ud0dc\ubc14/\ub124\ube44\ubc14 \uc228\uae40, \ud648\ubc84\ud2bc \ucc28\ub2e8, \ud654\uba74 \uc0c1\uc2dc \ucf1c\uc9d0"],
            ["GPS \uc815\ub958\uc7a5 \uac10\uc9c0", "\uc704\uce58 \uae30\ubc18\uc73c\ub85c \uac00\uc7a5 \uac00\uae4c\uc6b4 \uc815\ub958\uc7a5 \uc790\ub3d9 \uc124\uc815"],
            ["\uc790\uc8fc \uac00\ub294 \uacf3 \ud504\ub9ac\uc14b", "\uc9c0\uc5ed\ubcc4 \uc778\uae30 \ubaa9\uc801\uc9c0 \ud070 \ubc84\ud2bc (JSON \uc124\uc815)"],
            ["\uc624\ud504\ub77c\uc778 \ud3f4\ubc31", "\uc778\ud130\ub137 \ub04a\uae40 \uc2dc \uce90\uc2dc\ub41c \ub178\uc120\ud45c \ud45c\uc2dc"],
            ["\uc0ac\uc6a9 \ub85c\uadf8 \uc218\uc9d1", "\uc9c8\uc758 \ud14d\uc2a4\ud2b8, \uc131\uacf5/\uc2e4\ud328\uc728, \uc790\uc8fc \uac80\uc0c9 \ubaa9\uc801\uc9c0 TOP 10"],
        ],
        col_widths=[pw * 0.3, pw * 0.7]
    ))
    story.append(PageBreak())

    # ══════════════════════════════
    # 4. 시스템 아키텍처
    # ══════════════════════════════
    story.append(heading1("4. \uc2dc\uc2a4\ud15c \uc544\ud0a4\ud14d\ucc98"))
    story.append(hr())

    story.append(heading2("4-1. \uc2ec\ud50c \ud074\ub77c\uc774\uc5b8\ud2b8 \ud328\ud134"))
    story.append(spacer(4))

    arch_style_header = ParagraphStyle('ArchH', fontName='MalgunBold', fontSize=10,
        textColor=white, alignment=TA_CENTER, leading=14)
    arch_style_body = ParagraphStyle('ArchB', fontName='Malgun', fontSize=8.5,
        textColor=black, alignment=TA_CENTER, leading=12)

    arch_data = [
        [Paragraph("Android \ud0dc\ube14\ub9bf (\uc587\uc740 \ud074\ub77c\uc774\uc5b8\ud2b8)", arch_style_header)],
        [Paragraph("STT \uc74c\uc131\uc778\uc2dd | TTS \uc74c\uc131\ucd9c\ub825 | \uc2dc\ub2c8\uc5b4 UI | \ud0a4\uc624\uc2a4\ud06c \ubaa8\ub4dc\n"
                   "\uc74c\uc131 \uc785\ucd9c\ub825 + \ud654\uba74 \ud45c\uc2dc\ub9cc \ub2f4\ub2f9", arch_style_body)],
        [Paragraph("FastAPI \uc11c\ubc84 (\ub450\uaebc\uc6b4 \uc11c\ubc84)", arch_style_header)],
        [Paragraph("\u2460 \uc0ac\ud22c\ub9ac \ubcc0\ud658 | \u2461 \uc758\ub3c4 \ud30c\uc545 | \u2462 \uc720\uc0ac\uc5b4 \ub9e4\uce6d\n"
                   "\u2463 TAGO API \ud638\ucd9c | \u2464 \ucee8\ud14d\uc2a4\ud2b8 \uc800\uc7a5 | \u2465 \uc751\ub2f5 \uc0dd\uc131", arch_style_body)],
        [Paragraph("TAGO \uacf5\uacf5 \ubc84\uc2a4 \ub370\uc774\ud130 API", arch_style_header)],
        [Paragraph("\uc2e4\uc2dc\uac04 \ub3c4\ucc29\uc815\ubcf4 | \ub178\uc120\uc815\ubcf4 | \uc815\ub958\uc7a5 \uc815\ubcf4\n"
                   "\uad6d\ud1a0\uad50\ud1b5\ubd80 \uc804\uad6d \ubc84\uc2a4\uc815\ubcf4 \uc2dc\uc2a4\ud15c", arch_style_body)],
    ]

    arch_colors = [PRIMARY, white, TEAL, white, HexColor("#8E44AD"), white]
    arch_table = Table(arch_data, colWidths=[pw])
    style_cmds = [
        ('FONTNAME', (0, 0), (-1, -1), 'Malgun'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    for i, color in enumerate(arch_colors):
        style_cmds.append(('BACKGROUND', (0, i), (-1, i), color))
    arch_table.setStyle(TableStyle(style_cmds))
    story.append(arch_table)
    story.append(Paragraph("[\uadf8\ub9bc 1] Simple Client \uc544\ud0a4\ud14d\ucc98 3\uacc4\uce35 \uad6c\uc870", S['caption']))
    story.append(spacer(8))

    story.append(body(
        "<b>\uacc4\uce35 \ubd84\ub9ac\uc758 \ud575\uc2ec \uc7a5\uc810:</b> \uc571\uc740 \uc74c\uc131 \uc785\ucd9c\ub825\uacfc \ud654\uba74 \ud45c\uc2dc\ub9cc \ub2f4\ub2f9\ud558\uace0, "
        "\ubaa8\ub4e0 \ub85c\uc9c1\uc740 \uc11c\ubc84\uc5d0\uc11c \ucc98\ub9ac\ud569\ub2c8\ub2e4. "
        "\uc11c\ubc84\ub9cc \uc218\uc815\ud558\uba74 \uc571 \uc5c5\ub370\uc774\ud2b8 \uc5c6\uc774 \uac1c\uc120 \uac00\ub2a5\ud558\uba70, "
        "\ub2e4\uc591\ud55c \uc815\ub958\uc7a5 \ud0dc\ube14\ub9bf\uc5d0 \uc77c\uad00\ub41c \uc11c\ube44\uc2a4\ub97c \uc81c\uacf5\ud569\ub2c8\ub2e4."
    ))
    story.append(spacer(10))

    story.append(heading2("4-2. \ud328\ud0a4\uc9c0 \uad6c\uc870"))

    # Android 패키지
    story.append(heading3("Android \uc571 \uad6c\uc870"))
    pkg_android = [
        "com.hyeonsu.busguide/",
        "  di/              NetworkModule, RepositoryModule  (Hilt DI)",
        "  data/remote/     BusGuideApi (Retrofit)           (\uc11c\ubc84 \ud1b5\uc2e0)",
        "  data/repository/ BusGuideRepositoryImpl           (Repository \uad6c\ud604)",
        "  domain/model/    Station, BusArrival, Query*       (\ub3c4\uba54\uc778 \ubaa8\ub378)",
        "  domain/repository/ BusGuideRepository             (\ucd94\uc0c1\ud654 \uacc4\uc57d)",
        "  presentation/main/   MainScreen + MainViewModel   (\uba54\uc778 \ud654\uba74)",
        "  presentation/result/ ResultScreen                 (\uacb0\uacfc \ud654\uba74)",
        "  presentation/theme/  SeniorTheme, Color, Type     (\uc2dc\ub2c8\uc5b4 \ud14c\ub9c8)",
        "  speech/          SpeechManager, TtsManager        (STT/TTS \ub798\ud37c)",
        "  kiosk/           KioskManager                     (\ud0a4\uc624\uc2a4\ud06c \ubaa8\ub4dc)",
    ]
    for line in pkg_android:
        story.append(code_kr(line))
    story.append(spacer(4))

    # Server 패키지
    story.append(heading3("FastAPI \uc11c\ubc84 \uad6c\uc870"))
    pkg_server = [
        "server/",
        "  main.py                  FastAPI \uc5d4\ud2b8\ub9ac\ud3ec\uc778\ud2b8",
        "  models.py                Pydantic \ub370\uc774\ud130 \ubaa8\ub378",
        "  routers/query.py         POST /query (\uc74c\uc131 \uc9c8\uc758 \ucc98\ub9ac)",
        "  routers/bus.py           GET /bus/* (\ubc84\uc2a4 \uc815\ubcf4 \uc870\ud68c)",
        "  services/nlp_service.py  \uc0ac\ud22c\ub9ac \ubcc0\ud658 + \uc758\ub3c4 \ubd84\ub958 + \uc720\uc0ac\uc5b4 \ub9e4\uce6d",
        "  services/bus_service.py  TAGO API \uc5f0\ub3d9",
        "  services/context_service.py  \ub300\ud654 \ucee8\ud14d\uc2a4\ud2b8 \uad00\ub9ac",
        "  services/response_builder.py  \uc751\ub2f5 \uc0dd\uc131\uae30",
        "  data/*.json              \uc0ac\ud22c\ub9ac/\uc720\uc0ac\uc5b4/\uc758\ub3c4/\ud504\ub9ac\uc14b \ub370\uc774\ud130",
    ]
    for line in pkg_server:
        story.append(code_kr(line))
    story.append(PageBreak())

    # ══════════════════════════════
    # 5. 기술 스택
    # ══════════════════════════════
    story.append(heading1("5. \uae30\uc220 \uc2a4\ud0dd \ubc0f \uc120\ud0dd \uadfc\uac70"))
    story.append(hr())
    story.append(make_table(
        ["\uc601\uc5ed", "\uae30\uc220", "\uc120\ud0dd \uadfc\uac70"],
        [
            ["Language", "Kotlin + Python", "Android \uacf5\uc2dd \uc5b8\uc5b4 + FastAPI \ub85c \ube60\ub978 \uc11c\ubc84 \uac1c\ubc1c"],
            ["UI", "Jetpack Compose\n(Material3)", "\uc120\uc5b8\ud615 UI\ub85c \uc0c1\ud0dc \uad00\ub9ac \uac04\uacb0, \uc2dc\ub2c8\uc5b4 \ud14c\ub9c8 \ucee4\uc2a4\ud130\ub9c8\uc774\uc9d5 \uc6a9\uc774"],
            ["Architecture", "Simple Client +\nClean Architecture", "\uc11c\ubc84\uc5d0 \ub85c\uc9c1 \uc9d1\uc911 \u2192 \uc571 \uc5c5\ub370\uc774\ud2b8 \uc5c6\uc774 \uac1c\uc120 \uac00\ub2a5"],
            ["STT", "Android\nSpeechRecognizer", "\ubb34\ub8cc, \ud55c\uad6d\uc5b4 \uc9c0\uc6d0, \ub124\ud2b8\uc6cc\ud06c \ubd88\uc694 (on-device)"],
            ["TTS", "Android\nTextToSpeech", "\ubb34\ub8cc, 0.85\ubc30\uc18d \uc124\uc815\uc73c\ub85c \uc5b4\ub974\uc2e0 \uccad\ucde8 \ubc30\ub824"],
            ["NLP", "Kiwi (\ud55c\uad6d\uc5b4\n\ud615\ud0dc\uc18c \ubd84\uc11d)", "\ubb34\ub8cc \uc624\ud508\uc18c\uc2a4, \ud55c\uad6d\uc5b4 \ud2b9\ud654, \uc0ac\ud22c\ub9ac \ucc98\ub9ac \ubcf4\uc870"],
            ["Backend", "FastAPI + Uvicorn", "\ube44\ub3d9\uae30 \uc9c0\uc6d0, \uc790\ub3d9 API \ubb38\uc11c\ud654, Python \uc0dd\ud0dc\uacc4 \ud65c\uc6a9"],
            ["Bus Data", "TAGO API\n(\uad6d\ud1a0\uad50\ud1b5\ubd80)", "\uc804\uad6d \ubc84\uc2a4 \ub370\uc774\ud130 \ud1b5\ud569 API, \uc2e4\uc2dc\uac04 \ub3c4\ucc29\uc815\ubcf4 \uc81c\uacf5"],
            ["DI", "Hilt", "@Inject \ud55c \uc904\ub85c \uc758\uc874\uc131 \uc8fc\uc785, Android \uc804\uc6a9 \ucd5c\uc801\ud654"],
            ["Networking", "Retrofit +\nKotlinx Serialization", "Kotlin data class\uc640 \uc790\uc5f0\uc2a4\ub7ec\uc6b4 JSON \ub9e4\ud551"],
            ["Kiosk", "DevicePolicyManager\n(LOCK_TASK)", "\uc0c1\ud0dc\ubc14/\ud648\ubc84\ud2bc \ucc28\ub2e8, \uc815\ub958\uc7a5 \uc124\uce58\ud615\uc5d0 \ud544\uc218"],
        ],
        col_widths=[pw * 0.15, pw * 0.22, pw * 0.63]
    ))
    story.append(PageBreak())

    # ══════════════════════════════
    # 6. 핵심 기술 — NLP 파이프라인
    # ══════════════════════════════
    story.append(heading1("6. \ud575\uc2ec \uae30\uc220 \u2014 NLP \ud30c\uc774\ud504\ub77c\uc778"))
    story.append(hr())
    story.append(body(
        "BusGuide\ub294 <b>4\ub2e8\uacc4 NLP \ud30c\uc774\ud504\ub77c\uc778</b>\uc744 \uc9c1\uc811 \uad6c\ud604\ud558\uc5ec "
        "\uc5b4\ub974\uc2e0\uc758 \uc74c\uc131 \uc9c8\uc758\ub97c \uc815\ud655\ud558\uac8c \ucc98\ub9ac\ud569\ub2c8\ub2e4."
    ))
    story.append(spacer(6))

    # NLP 파이프라인 다이어그램
    nlp_data = [
        [Paragraph("1\ub2e8\uacc4: \uc0ac\ud22c\ub9ac \ubcc0\ud658 (dialect_map.json)", arch_style_header)],
        [Paragraph("\"\uce74\ub294\" \u2192 \"\uac00\ub294\", \"\uc788\ub098\uc608\" \u2192 \"\uc788\ub098\uc694\" \u2014 19\uac1c \ubd80\uc0b0 \uc0ac\ud22c\ub9ac \ub9e4\ud551\n"
                   "\uae34 \ud0a4\uc6cc\ub4dc \uc6b0\uc120 \uce58\ud658\uc73c\ub85c \ubd80\ubd84 \ub9e4\uce6d \ucda9\ub3cc \ubc29\uc9c0", arch_style_body)],
        [Paragraph("2\ub2e8\uacc4: \uc758\ub3c4 \ubd84\ub958 (intent_rules.json)", arch_style_header)],
        [Paragraph("\ub178\uc120_\uac80\uc0c9 | \ub3c4\ucc29_\uc2dc\uac04 | \ud658\uc2b9_\uc548\ub0b4 | \uc815\ub958\uc7a5_\ud655\uc778\n"
                   "\uc6b0\uc120\uc21c\uc704 \uae30\ubc18 \ud0a4\uc6cc\ub4dc \ub9e4\uce6d + Kiwi \ud615\ud0dc\uc18c \ubd84\uc11d \ubcf4\uc870", arch_style_body)],
        [Paragraph("3\ub2e8\uacc4: \uc720\uc0ac\uc5b4 \ub9e4\uce6d (synonyms.json)", arch_style_header)],
        [Paragraph("\"\ubc14\ub2e4\" \u2192 \"\ud574\uc6b4\ub300\", \"\uae30\ucc28\uc5ed\" \u2192 \"\ubd80\uc0b0\uc5ed\" \u2014 10\uac1c \uc9c0\uba85 + 40+ \uc720\uc0ac\uc5b4\n"
                   "\uc5ed\uc0c9\uc778 \uae30\ubc18 \ube60\ub978 \ub8e9\uc5c5 + \uae34 \ud0a4\uc6cc\ub4dc \uc6b0\uc120 \ub9e4\uce6d", arch_style_body)],
        [Paragraph("4\ub2e8\uacc4: \ucee8\ud14d\uc2a4\ud2b8 \ub300\ud654 (context_service.py)", arch_style_header)],
        [Paragraph("\"\uac70\uae30\" = \uc774\uc804 \ubaa9\uc801\uc9c0, \"\uadf8\uac70\" = \uc774\uc804 \ubc84\uc2a4\ubc88\ud638 \u2014 \ub300\uba85\uc0ac \ud574\uc11d\n"
                   "\uc138\uc158 ID \uae30\ubc18 \uc778\uba54\ubaa8\ub9ac \uc800\uc7a5, 5\ubd84 TTL \uc790\ub3d9 \ub9cc\ub8cc", arch_style_body)],
    ]
    nlp_colors = [PRIMARY, white, TEAL, white, HexColor("#8E44AD"), white, HexColor("#C62828"), white]
    nlp_table = Table(nlp_data, colWidths=[pw])
    nlp_cmds = [
        ('FONTNAME', (0, 0), (-1, -1), 'Malgun'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    for i, color in enumerate(nlp_colors):
        nlp_cmds.append(('BACKGROUND', (0, i), (-1, i), color))
    nlp_table.setStyle(TableStyle(nlp_cmds))
    story.append(nlp_table)
    story.append(Paragraph("[\uadf8\ub9bc 2] 4\ub2e8\uacc4 NLP \ud30c\uc774\ud504\ub77c\uc778 \ud750\ub984\ub3c4", S['caption']))
    story.append(spacer(8))

    story.append(heading2("6-1. \uc0ac\ud22c\ub9ac \ubcc0\ud658 \uc0c1\uc138"))
    story.append(body(
        "<b>dialect_map.json</b>\uc5d0\uc11c 19\uac1c \ubd80\uc0b0 \uc0ac\ud22c\ub9ac \ub9e4\ud551\uc744 \ub85c\ub4dc\ud558\uc5ec "
        "\uc815\uaddc\uc2dd \uae30\ubc18\uc73c\ub85c \uce58\ud658\ud569\ub2c8\ub2e4. "
        "\uae34 \ud0a4\uc6cc\ub4dc\ub97c \uba3c\uc800 \uce58\ud658\ud558\uc5ec \"\uc788\ub098\uc608\" > \"\ub098\uc608\" \ucda9\ub3cc\uc744 \ubc29\uc9c0\ud569\ub2c8\ub2e4."
    ))
    story.append(spacer(4))
    story.append(make_table(
        ["\uc0ac\ud22c\ub9ac (\uc785\ub825)", "\ud45c\uc900\uc5b4 (\ubcc0\ud658 \uacb0\uacfc)", "\uc608\uc2dc \ubb38\uc7a5"],
        [
            ["\uce74\ub294", "\uac00\ub294", "\"\uba85\uc9c0\ubcd1\uc6d0 \uce74\ub294 \ubc84\uc2a4\" \u2192 \"\uba85\uc9c0\ubcd1\uc6d0 \uac00\ub294 \ubc84\uc2a4\""],
            ["\uc5b4\ub370", "\uc5b4\ub514", "\"\uc5b4\ub370 \uce74\ub294 \ubc84\uc2a4\uc608\uc694\" \u2192 \"\uc5b4\ub514 \uac00\ub294 \ubc84\uc2a4\uc608\uc694\""],
            ["\uc788\ub098\uc608", "\uc788\ub098\uc694", "\"\ubc84\uc2a4 \uc788\ub098\uc608?\" \u2192 \"\ubc84\uc2a4 \uc788\ub098\uc694?\""],
            ["\ub9de\ub098", "\ub9de\ub098\uc694", "\"\uc5ec\uae30 \ub9de\ub098?\" \u2192 \"\uc5ec\uae30 \ub9de\ub098\uc694?\""],
            ["\uce74\ub77c\uce74\ub294", "\uac08\uc544\ud0c0\ub294", "\"\ubc84\uc2a4 \uce74\ub77c\uce74\ub294\" \u2192 \"\ubc84\uc2a4 \uac08\uc544\ud0c0\ub294\""],
        ],
        col_widths=[pw * 0.2, pw * 0.2, pw * 0.6]
    ))
    story.append(spacer(8))

    story.append(heading2("6-2. \uc758\ub3c4 \ubd84\ub958 \uc0c1\uc138"))
    story.append(make_table(
        ["\uc758\ub3c4", "\ud0a4\uc6cc\ub4dc \uc608\uc2dc", "\uc6b0\uc120\uc21c\uc704", "\uc751\ub2f5 \uc608\uc2dc"],
        [
            ["\ud658\uc2b9_\uc548\ub0b4", "\"\uac08\uc544\ud0c0\", \"\uac14\ub2e4\uac00\"", "1 (\ucd5c\uc6b0\uc120)", "\"181\ubc88\uc73c\ub85c \uac08\uc544\ud0c0\uc138\uc694\""],
            ["\ub3c4\ucc29_\uc2dc\uac04", "\"\uba87 \ubd84\", \"\uc5b8\uc81c\"", "2", "\"5\ubd84 \ud6c4 \ub3c4\ucc29\ud569\ub2c8\ub2e4\""],
            ["\uc815\ub958\uc7a5_\ud655\uc778", "\"\uc5ec\uae30 \uc5b4\ub514\", \"\ubb34\uc2a8 \ubc84\uc2a4\"", "3", "\"\ud604\uc7ac \uc815\ub958\uc7a5\uc740 \uba85\uc9c0\ub300\ud559\uad50\uc785\ub2c8\ub2e4\""],
            ["\ub178\uc120_\uac80\uc0c9", "\"\uac00\ub294 \ubc84\uc2a4\", \"\uac00\ub824\uba74\"", "4 (\uae30\ubcf8\uac12)", "\"58\ubc88 \ubc84\uc2a4 \ud0c0\uc2dc\uba74 \ub429\ub2c8\ub2e4\""],
        ],
        col_widths=[pw * 0.15, pw * 0.22, pw * 0.13, pw * 0.5]
    ))
    story.append(spacer(4))
    story.append(body(
        "<b>[\ubc1c\ud45c \ud3ec\uc778\ud2b8]</b> \uc6b0\uc120\uc21c\uc704\uac00 \uc911\uc694\ud55c \uc774\uc720: "
        "\"\uba85\uc9c0\ubcd1\uc6d0 \uac14\ub2e4\uac00 \ud574\uc6b4\ub300 \uac00\ub824\uba74?\" \uac19\uc740 \ubb38\uc7a5\uc5d0\ub294 "
        "\ud658\uc2b9\uacfc \ub178\uc120 \ud0a4\uc6cc\ub4dc\uac00 \ubaa8\ub450 \ud3ec\ud568\ub418\uc5b4 \uc788\uc5b4, "
        "\ud658\uc2b9 \uc758\ub3c4\ub97c \uc6b0\uc120 \ucc98\ub9ac\ud574\uc57c \uc815\ud655\ud569\ub2c8\ub2e4."
    ))
    story.append(spacer(8))

    story.append(heading2("6-3. \uc720\uc0ac\uc5b4 \ub9e4\uce6d \uc0c1\uc138"))
    story.append(make_table(
        ["\ud45c\uc900 \uc9c0\uba85", "\uc720\uc0ac\uc5b4 (\uc5b4\ub974\uc2e0 \ud45c\ud604)", "\uc5ed\uc0c9\uc778 \ubc29\uc2dd"],
        [
            ["\ud574\uc6b4\ub300", "\ubc14\ub2e4, \ud574\uc6b4\ub300 \ud574\uc218\uc695\uc7a5, \ud574\uc6b4\ub300\uc5ed", "\"\ubc14\ub2e4\" \u2192 \"\ud574\uc6b4\ub300\" \uc5ed\ubc29\ud5a5 \ub8e9\uc5c5"],
            ["\ubd80\uc0b0\uc5ed", "\uae30\ucc28\uc5ed, KTX\uc5ed, \ubd80\uc0b0\uc5ed\uc804\ucca0\uc5ed", "\"\uae30\ucc28\uc5ed\" \u2192 \"\ubd80\uc0b0\uc5ed\""],
            ["\uba85\uc9c0\ubcd1\uc6d0", "\uba85\uc9c0 \ud070\ubcd1\uc6d0, \uba85\uc9c0\ubcd1\uc6d0, \uba85\uc9c0", "\"\uba85\uc9c0 \ud070\ubcd1\uc6d0\" \u2192 \"\uba85\uc9c0\ubcd1\uc6d0\""],
            ["\ub0a8\ud3ec\ub3d9", "\uc790\uac08\uce58, \ub0a8\ud3ec\ub3d9\uc2dc\uc7a5, \ub0a8\ud3ec", "\"\uc790\uac08\uce58\" \u2192 \"\ub0a8\ud3ec\ub3d9\""],
            ["\uc11c\uba74", "\uc11c\uba74 \ub86d\ub370, \uc11c\uba74\uc5ed, \uc11c\uba74\uc2dc\uc7a5", "\"\uc11c\uba74 \ub86d\ub370\" \u2192 \"\uc11c\uba74\""],
        ],
        col_widths=[pw * 0.2, pw * 0.4, pw * 0.4]
    ))
    story.append(spacer(8))

    story.append(heading2("6-4. \ucee8\ud14d\uc2a4\ud2b8 \ub300\ud654 \uc0c1\uc138"))
    story.append(body(
        "\uc138\uc158 ID\ubcc4 \uc778\uba54\ubaa8\ub9ac \uc800\uc7a5\uc73c\ub85c \uc5f0\uc18d \ub300\ud654\ub97c \uc9c0\uc6d0\ud569\ub2c8\ub2e4. "
        "5\ubd84 TTL \uc790\ub3d9 \ub9cc\ub8cc\ub85c \uba54\ubaa8\ub9ac \ub204\uc218\ub97c \ubc29\uc9c0\ud569\ub2c8\ub2e4."
    ))
    story.append(spacer(4))

    context_lines = [
        "<b>\uc9c8\ubb38 1:</b> \"58\ubc88 \uc5b4\ub514 \uac00\uc694?\"",
        "\u2192 \ucee8\ud14d\uc2a4\ud2b8 \uc800\uc7a5: {destination: \"\uba85\uc9c0\ubcd1\uc6d0\", bus: \"58\"}",
        "",
        "<b>\uc9c8\ubb38 2:</b> \"\uba87 \ubd84 \ud6c4\uc5d0 \uc640\uc694?\"",
        "\u2192 58\ubc88 \uae30\uc5b5\ub428! \"5\ubd84 \ud6c4 \ub3c4\ucc29\ud569\ub2c8\ub2e4\"",
        "",
        "<b>\uc9c8\ubb38 3:</b> \"\uac70\uae30\uc11c \ud574\uc6b4\ub300 \uac00\ub824\uba74?\"",
        "\u2192 \"\uac70\uae30\" = \uba85\uc9c0\ubcd1\uc6d0 (\ub300\uba85\uc0ac \ud574\uc11d)",
        "\u2192 \"181\ubc88 \ubc84\uc2a4\ub85c \uac08\uc544\ud0c0\uc138\uc694\"",
    ]
    for line in context_lines:
        if line:
            story.append(demo_line(line))
        else:
            story.append(spacer(4))
    story.append(PageBreak())

    # ══════════════════════════════
    # 7. 뼈대 코드
    # ══════════════════════════════
    story.append(heading1("7. \ubf08\ub300 \ucf54\ub4dc (\ud575\uc2ec \ubc1c\ucde8)"))
    story.append(hr())

    story.append(heading2("7-1. NlpService (\uc0ac\ud22c\ub9ac \ubcc0\ud658 + \uc758\ub3c4 \ubd84\ub958)"))
    story.append(body_sm("server/services/nlp_service.py"))
    story.append(body_sm(
        "[\ubc1c\ud45c \ud3ec\uc778\ud2b8] \uc774 \ud074\ub798\uc2a4\uac00 BusGuide NLP\uc758 \ud575\uc2ec\uc785\ub2c8\ub2e4. "
        "\uc0ac\ud22c\ub9ac \ubcc0\ud658 \u2192 \uc758\ub3c4 \ubd84\ub958 \u2192 \uc720\uc0ac\uc5b4 \ub9e4\uce6d \u2192 \ubaa9\uc801\uc9c0 \ucd94\ucd9c\uc744 "
        "\ub2e8\uc77c \ud30c\uc774\ud504\ub77c\uc778\uc73c\ub85c \ucc98\ub9ac\ud569\ub2c8\ub2e4."
    ))
    code_nlp = [
        "# [\uc0ac\ud22c\ub9ac \ubcc0\ud658 \uc5d4\uc9c4] dialect_map.json\uc5d0\uc11c \ub9e4\ud551 \ub85c\ub4dc",
        "# \uae34 \ud0a4\uc6cc\ub4dc \uc6b0\uc120 \uce58\ud658\uc73c\ub85c \ubd80\ubd84 \ub9e4\uce6d \ucda9\ub3cc \ubc29\uc9c0",
        "class NlpService:",
        "    def __init__(self):",
        "        self.dialect_map = load_json('dialect_map.json')",
        "        self.intent_rules = load_json('intent_rules.json')",
        "        self.synonyms = load_json('synonyms.json')",
        "        # \uc5ed\uc0c9\uc778: {\"\ubc14\ub2e4\": \"\ud574\uc6b4\ub300\", \"\uae30\ucc28\uc5ed\": \"\ubd80\uc0b0\uc5ed\", ...}",
        "        self.reverse_synonyms = self._build_reverse_synonyms()",
        "",
        "    def convert_dialect(self, text: str) -&gt; str:",
        "        \"\"\"[1\ub2e8\uacc4] \uc0ac\ud22c\ub9ac \u2192 \ud45c\uc900\uc5b4 \ubcc0\ud658\"\"\"",
        "        # \uae34 \ud0a4\uc6cc\ub4dc \uc6b0\uc120 \uc815\ub82c (\"\uc788\ub098\uc608\" &gt; \"\ub098\uc608\" \ucda9\ub3cc \ubc29\uc9c0)",
        "        sorted_map = sorted(self.dialect_map.items(),",
        "                            key=lambda x: len(x[0]), reverse=True)",
        "        for dialect, standard in sorted_map:",
        "            text = text.replace(dialect, standard)",
        "        return text",
        "",
        "    def classify_intent(self, text: str) -&gt; str:",
        "        \"\"\"[2\ub2e8\uacc4] \ud0a4\uc6cc\ub4dc \uae30\ubc18 \uc758\ub3c4 \ubd84\ub958\"\"\"",
        "        # \uc6b0\uc120\uc21c\uc704 \uc815\ub82c: \ud658\uc2b9(1) &gt; \ub3c4\ucc29(2) &gt; \uc815\ub958\uc7a5(3) &gt; \ub178\uc120(4)",
        "        sorted_rules = sorted(self.intent_rules,",
        "                              key=lambda r: r['priority'])",
        "        for rule in sorted_rules:",
        "            if any(kw in text for kw in rule['keywords']):",
        "                return rule['intent']",
        "        return '\ub178\uc120_\uac80\uc0c9'  # \uae30\ubcf8\uac12",
        "",
        "    def match_synonym(self, text: str) -&gt; str:",
        "        \"\"\"[3\ub2e8\uacc4] \uc720\uc0ac\uc5b4 \u2192 \ud45c\uc900 \uc9c0\uba85 \ub9e4\uce6d\"\"\"",
        "        sorted_syns = sorted(self.reverse_synonyms.items(),",
        "                             key=lambda x: len(x[0]), reverse=True)",
        "        for variation, standard in sorted_syns:",
        "            if variation in text:",
        "                text = text.replace(variation, standard)",
        "        return text",
    ]
    for line in code_nlp:
        story.append(code_line(line) if line.strip() else spacer(2))
    story.append(spacer(8))

    story.append(heading2("7-2. ContextService (\uc5f0\uc18d \ub300\ud654 + \ub300\uba85\uc0ac \ud574\uc11d)"))
    story.append(body_sm("server/services/context_service.py"))
    story.append(body_sm(
        "[\ubc1c\ud45c \ud3ec\uc778\ud2b8] \uc138\uc158 ID \uae30\ubc18 \uc778\uba54\ubaa8\ub9ac \uc800\uc7a5\uc73c\ub85c \uc5f0\uc18d \ub300\ud654\ub97c \uc9c0\uc6d0\ud569\ub2c8\ub2e4. "
        "\"\uac70\uae30\", \"\uadf8\uac70\" \uac19\uc740 \ub300\uba85\uc0ac\ub97c \uc774\uc804 \ubaa9\uc801\uc9c0/\ubc84\uc2a4\ub85c \ud574\uc11d\ud569\ub2c8\ub2e4."
    ))
    code_context = [
        "class ContextService:",
        "    def __init__(self):",
        "        self._store: dict[str, dict] = {}  # session_id \u2192 context",
        "        self.TTL = 300  # 5\ubd84 \uc790\ub3d9 \ub9cc\ub8cc",
        "",
        "    def save(self, session_id: str, data: dict):",
        "        \"\"\"\ub300\ud654 \ucee8\ud14d\uc2a4\ud2b8 \uc800\uc7a5 (\ubaa9\uc801\uc9c0, \ubc84\uc2a4\ubc88\ud638, \uc815\ub958\uc7a5)\"\"\"",
        "        self._store[session_id] = {",
        "            **data,",
        "            'timestamp': time.time()",
        "        }",
        "",
        "    def resolve_pronoun(self, session_id: str, text: str) -&gt; str:",
        "        \"\"\"\ub300\uba85\uc0ac \ud574\uc11d: \"\uac70\uae30\" \u2192 \uc774\uc804 \ubaa9\uc801\uc9c0\"\"\"",
        "        ctx = self.get(session_id)",
        "        if not ctx:",
        "            return text",
        "        pronouns = ['\uac70\uae30', '\uac70\uae30\uc11c', '\uadf8\uacf3']",
        "        for p in pronouns:",
        "            if p in text and 'destination' in ctx:",
        "                text = text.replace(p, ctx['destination'])",
        "        return text",
    ]
    for line in code_context:
        story.append(code_line(line) if line.strip() else spacer(2))
    story.append(spacer(8))

    story.append(heading2("7-3. /query \uc5d4\ub4dc\ud3ec\uc778\ud2b8 (\uc804\uccb4 \ud30c\uc774\ud504\ub77c\uc778)"))
    story.append(body_sm("server/routers/query.py"))
    story.append(body_sm(
        "[\ubc1c\ud45c \ud3ec\uc778\ud2b8] 6\ub2e8\uacc4 \ud30c\uc774\ud504\ub77c\uc778\uc774 \ud55c \ubc88\uc758 API \ud638\ucd9c\ub85c \uc2e4\ud589\ub429\ub2c8\ub2e4. "
        "\uc5b4\ub974\uc2e0\uc774 \ub9d0\ud558\uba74 \uc774 \uc5d4\ub4dc\ud3ec\uc778\ud2b8\uac00 \ubaa8\ub4e0 \ucc98\ub9ac\ub97c \uc218\ud589\ud569\ub2c8\ub2e4."
    ))
    code_query = [
        "@router.post('/query')",
        "async def process_query(req: QueryRequest):",
        "    # \u2460 \ub300\uba85\uc0ac \ud574\uc11d: \"\uac70\uae30\" \u2192 \uc774\uc804 \ubaa9\uc801\uc9c0",
        "    text = context_service.resolve_pronoun(",
        "        req.session_id, req.text)",
        "",
        "    # \u2461 \uc0ac\ud22c\ub9ac \ubcc0\ud658: \"\uce74\ub294\" \u2192 \"\uac00\ub294\"",
        "    text = nlp.convert_dialect(text)",
        "",
        "    # \u2462 \uc720\uc0ac\uc5b4 \ub9e4\uce6d: \"\ubc14\ub2e4\" \u2192 \"\ud574\uc6b4\ub300\"",
        "    text = nlp.match_synonym(text)",
        "",
        "    # \u2463 \uc758\ub3c4 \ubd84\ub958: \ub178\uc120_\uac80\uc0c9 / \ub3c4\ucc29_\uc2dc\uac04 / \ud658\uc2b9 / \uc815\ub958\uc7a5",
        "    intent = nlp.classify_intent(text)",
        "",
        "    # \u2464 TAGO API \ud638\ucd9c + \uc751\ub2f5 \uc0dd\uc131",
        "    destination = nlp.extract_destination(text)",
        "    buses = await bus_service.get_arrivals(req.station_id)",
        "    response = build_response(intent, destination, buses)",
        "",
        "    # \u2465 \ucee8\ud14d\uc2a4\ud2b8 \uc800\uc7a5 (\ub2e4\uc74c \uc9c8\ubb38\uc5d0\uc11c \uae30\uc5b5)",
        "    context_service.save(req.session_id, {",
        "        'destination': destination,",
        "        'bus': response.buses[0].bus_number if response.buses",
        "              else None",
        "    })",
        "    return response",
    ]
    for line in code_query:
        story.append(code_line(line) if line.strip() else spacer(2))
    story.append(PageBreak())

    story.append(heading2("7-4. MainScreen (\uc2dc\ub2c8\uc5b4 \ud2b9\ud654 UI)"))
    story.append(body_sm("presentation/main/MainScreen.kt"))
    story.append(body_sm(
        "[\ubc1c\ud45c \ud3ec\uc778\ud2b8] 240dp \uc6d0\ud615 \ub9d0\ud558\uae30 \ubc84\ud2bc + 3\uc5f4 \ud504\ub9ac\uc14b \uadf8\ub9ac\ub4dc\ub85c "
        "\uc5b4\ub974\uc2e0\uc774 \uc9c1\uad00\uc801\uc73c\ub85c \uc0ac\uc6a9\ud560 \uc218 \uc788\ub294 UI\uc785\ub2c8\ub2e4."
    ))
    code_main = [
        "// [\uc2dc\ub2c8\uc5b4 UX] 240dp \uc6d0\ud615 \ub9d0\ud558\uae30 \ubc84\ud2bc (5cm \uc774\uc0c1)",
        "// \uc190\ub5a8\ub9bc\uc774 \uc788\uc5b4\ub3c4 \uc27d\uac8c \ub204\ub97c \uc218 \uc788\ub294 \ud06c\uae30",
        "Button(",
        "    onClick = { viewModel.startListening() },",
        "    modifier = Modifier",
        "        .size(240.dp)          // \uc5b4\ub974\uc2e0 \uc190\uac00\ub77d \ud06c\uae30 \uace0\ub824",
        "        .clip(CircleShape),",
        "    colors = ButtonDefaults.buttonColors(",
        "        containerColor = SeniorPrimary  // \ub530\ub73b\ud55c \uc8fc\ud669\uc0c9",
        "    )",
        ") {",
        "    Icon(",
        "        imageVector = Icons.Default.Mic,",
        "        modifier = Modifier.size(80.dp),  // \ud070 \ub9c8\uc774\ud06c \uc544\uc774\ucf58",
        "        tint = Color.White",
        "    )",
        "}",
        "",
        "// [\uc2dc\ub2c8\uc5b4 UX] 48sp \ud3f0\ud2b8 \uc548\ub0b4 \ubb38\uad6c (3.4\ubc30 \ud06c\uae30)",
        "Text(",
        "    text = \"\uc5b4\ub514 \uac00\uc2dc\ub824\uace0\uc694?\",",
        "    style = SeniorTypography.displayLarge,  // 48sp",
        "    color = SeniorOnBackground              // \ub178\ub780\uc0c9 (#FFF176)",
        ")",
        "",
        "// [\uc2dc\ub2c8\uc5b4 UX] \uc790\uc8fc \uac00\ub294 \uacf3 \ud504\ub9ac\uc14b (3\uc5f4 \uadf8\ub9ac\ub4dc)",
        "LazyVerticalGrid(",
        "    columns = GridCells.Fixed(3),",
        "    modifier = Modifier.padding(16.dp)",
        ") {",
        "    items(presets) { preset -&gt;",
        "        PresetButton(  // 120dp \ubc84\ud2bc, 24sp \ud3f0\ud2b8",
        "            text = preset.label,",
        "            onClick = { viewModel.sendQuery(preset.query) }",
        "        )",
        "    }",
        "}",
    ]
    for line in code_main:
        story.append(code_line(line) if line.strip() else spacer(2))
    story.append(PageBreak())

    # ══════════════════════════════
    # 8. 차별화 분석
    # ══════════════════════════════
    story.append(heading1("8. \ucc28\ubcc4\ud654 \ubd84\uc11d \u2014 \uae30\uc874 \uc194\ub8e8\uc158\uacfc \ube44\uad50"))
    story.append(hr())
    story.append(make_table(
        ["\uae30\ub2a5", "\uce74\uce74\uc624\ub9f5", "BIS \uc804\uad11\ud310", "BusGuide"],
        [
            ["\ud0c0\uac9f", "\uc80a\uc740 \uce35", "\ubaa8\ub4e0 \uc0ac\ub78c", "\ub514\uc9c0\ud138 \uc57d\uc790"],
            ["\ud544\uc694 \uae30\uae30", "\uc2a4\ub9c8\ud2b8\ud3f0", "\uc5c6\uc74c", "\uc5c6\uc74c (\uc815\ub958\uc7a5 \uc124\uce58)"],
            ["\uc778\ud130\ud398\uc774\uc2a4", "\ud130\uce58+\uac80\uc0c9", "\uc2dc\uac01\ub9cc", "\uc74c\uc131+\uc2dc\uac01"],
            ["\ub300\ud654\ud615", "X", "X", "O (\uc5f0\uc18d \ub300\ud654)"],
            ["\uc811\uadfc\uc131", "\uc571 \uc124\uce58 \ud544\uc694", "\uc77d\uae30 \ud544\uc694", "\ub9d0\ub9cc \ud558\uba74 \ub428"],
            ["\uc124\uce58 \ube44\uc6a9", "\u2014", "300~500\ub9cc\uc6d0", "14\ub9cc\uc6d0"],
            ["\uc0ac\ud22c\ub9ac \uc9c0\uc6d0", "X", "X", "O (19\uac1c \ud328\ud134)"],
            ["\ubaa9\uc801\uc9c0 \uc548\ub0b4", "O (\uac80\uc0c9 \ud544\uc694)", "X", "O (\uc74c\uc131 \uc9c8\uc758)"],
        ],
        col_widths=[pw * 0.2, pw * 0.2, pw * 0.2, pw * 0.4]
    ))
    story.append(spacer(8))
    story.append(body(
        "<b>\ud575\uc2ec \ucc28\ubcc4\uc810 \uc694\uc57d:</b> \uce74\uce74\uc624\ub9f5\uc740 \uc2a4\ub9c8\ud2b8\ud3f0 \uc0ac\uc6a9\uc774 \uac00\ub2a5\ud55c \uc0ac\ub78c\uc744 \uc704\ud55c \uac83\uc785\ub2c8\ub2e4. "
        "BusGuide\ub294 <b>\ub514\uc9c0\ud138 \uc18c\uc678 \uacc4\uce35 24\ub9cc \uba85</b>\uc744 \uc704\ud55c \uc194\ub8e8\uc158\uc73c\ub85c, "
        "\uc571 \uc124\uce58 \uc5c6\uc774, \uac80\uc0c9\uc5b4 \uc785\ub825 \uc5c6\uc774, <b>\ub9d0\ub9cc \ud558\uba74 \ub418\ub294</b> \uc720\uc77c\ud55c \uc2dc\uc2a4\ud15c\uc785\ub2c8\ub2e4."
    ))
    story.append(PageBreak())

    # ══════════════════════════════
    # 9. 에러 핸들링
    # ══════════════════════════════
    story.append(heading1("9. \uc5d0\ub7ec \ud578\ub4e4\ub9c1 & \uc5e3\uc9c0 \ucf00\uc774\uc2a4"))
    story.append(hr())
    story.append(body(
        "\uc2e4\uc81c \uc11c\ube44\uc2a4 \ud488\uc9c8\uc744 \uacb0\uc815\ud558\ub294 \uac83\uc740 \ud575\uc2ec \uae30\ub2a5\uc774 \uc544\ub2c8\ub77c <b>\uc5e3\uc9c0 \ucf00\uc774\uc2a4 \ucc98\ub9ac</b>\uc785\ub2c8\ub2e4."
    ))
    story.append(spacer(6))
    story.append(make_table(
        ["\uc0c1\ud669", "\ucc98\ub9ac \ubc29\uc2dd"],
        [
            ["\uc74c\uc131 \uc778\uc2dd \uc2e4\ud328", "3\ucd08 \ud0c0\uc784\uc544\uc6c3 \u2192 TTS \"\ud654\uba74\uc744 \ub20c\ub7ec\uc8fc\uc138\uc694\" \u2192 \ud130\uce58 \ud654\uba74 \uc790\ub3d9 \uc804\ud658"],
            ["\uc778\ud130\ub137 \ub04a\uae40", "\uc548\ub0b4 \uba54\uc2dc\uc9c0 + \uce90\uc2dc\ub41c \ub178\uc120\ud45c \ud45c\uc2dc (DataStore \uce90\uc2dc)"],
            ["\ubaa9\uc801\uc9c0 \uc778\uc2dd \uc2e4\ud328", "\"\uc5b4\ub514\ub85c \uac00\uc2dc\ub824\uace0\uc694?\" \ub2e4\uc2dc \uc9c8\ubb38 + \ud504\ub9ac\uc14b \ubc84\ud2bc \uc81c\uc2dc"],
            ["TAGO API \uc624\ub958", "\"\uc7a0\uc2dc \ud6c4 \ub2e4\uc2dc \ub9d0\uc500\ud574\uc8fc\uc138\uc694\" \uc548\ub0b4 + \uc790\ub3d9 \uc7ac\uc2dc\ub3c4 (3\ud68c)"],
            ["\ucee8\ud14d\uc2a4\ud2b8 \ub9cc\ub8cc (5\ubd84)", "\uc790\ub3d9 \uc138\uc158 \ucd08\uae30\ud654 \u2192 \uba54\uc778 \ud654\uba74\uc73c\ub85c \ubcf5\uadc0"],
            ["\uc18c\uc74c \ud658\uacbd", "\uc74c\uc131 + \ud130\uce58 \ubcd1\ud589 (\uba40\ud2f0\ubaa8\ub2ec) \u2192 \uc790\ub3d9 \ud130\uce58 \uc804\ud658"],
            ["\ubc84\uc2a4 \ub3c4\ucc29 \uc815\ubcf4 \uc5c6\uc74c", "\"\ud604\uc7ac \ub3c4\ucc29 \uc608\uc815\uc778 \ubc84\uc2a4\uac00 \uc5c6\uc2b5\ub2c8\ub2e4\" \uc548\ub0b4"],
        ],
        col_widths=[pw * 0.25, pw * 0.75]
    ))
    story.append(PageBreak())

    # ══════════════════════════════
    # 10. 테스트 전략 및 결과
    # ══════════════════════════════
    story.append(heading1("10. \ud14c\uc2a4\ud2b8 \uc804\ub7b5 \ubc0f \uacb0\uacfc"))
    story.append(hr())

    story.append(heading2("10-1. \uc11c\ubc84 \ud14c\uc2a4\ud2b8 \uacb0\uacfc"))
    story.append(body(
        "\uc11c\ubc84 \ucf54\ub4dc\ub294 <b>29\uac1c \ud14c\uc2a4\ud2b8 \uc804\uc218 \ud1b5\uacfc</b>\ub85c "
        "\ubaa8\ub4e0 \ud575\uc2ec \uae30\ub2a5\uc758 \uc815\ud655\uc131\uc744 \uac80\uc99d\ud588\uc2b5\ub2c8\ub2e4."
    ))
    story.append(spacer(4))
    story.append(make_table(
        ["\ud14c\uc2a4\ud2b8 \ud30c\uc77c", "\ud14c\uc2a4\ud2b8 \uc218", "\uac80\uc99d \ub0b4\uc6a9"],
        [
            ["test_models.py", "4\uac1c", "Pydantic \ubaa8\ub378 \uc0dd\uc131, \uae30\ubcf8\uac12, \uc9c1\ub82c\ud654"],
            ["test_nlp_dialect.py", "4\uac1c", "\uc0ac\ud22c\ub9ac \ubcc0\ud658 19\uac1c \ud328\ud134 \uc815\ud655\uc131"],
            ["test_nlp_intent.py", "5\uac1c", "4\uac00\uc9c0 \uc758\ub3c4 \uc62c\ubc14\ub978 \ubd84\ub958, \uc6b0\uc120\uc21c\uc704 \uac80\uc99d"],
            ["test_nlp_synonym.py", "5\uac1c", "10\uac1c \uc9c0\uba85 + 40+ \uc720\uc0ac\uc5b4 \ub9e4\uce6d \uc815\ud655\uc131"],
            ["test_context.py", "5\uac1c", "\ucee8\ud14d\uc2a4\ud2b8 \uc800\uc7a5/\uc870\ud68c, \ub300\uba85\uc0ac \ud574\uc11d, TTL \ub9cc\ub8cc"],
            ["test_bus_service.py", "3\uac1c", "TAGO API \uc5f0\ub3d9, \uc751\ub2f5 \ud30c\uc2f1, \uc5d0\ub7ec \ucc98\ub9ac"],
            ["test_query_router.py", "3\uac1c", "\uc804\uccb4 \ud30c\uc774\ud504\ub77c\uc778 \ud1b5\ud569 \ud14c\uc2a4\ud2b8"],
            ["<b>\ud569\uacc4</b>", "<b>29\uac1c</b>", "<b>\uc804\uc218 \ud1b5\uacfc (PASSED)</b>"],
        ],
        col_widths=[pw * 0.3, pw * 0.15, pw * 0.55]
    ))
    story.append(spacer(8))

    story.append(heading2("10-2. \ud14c\uc2a4\ud2b8 \uc804\ub7b5"))
    story.append(make_table(
        ["\ud14c\uc2a4\ud2b8 \uc720\ud615", "\ub300\uc0c1", "\ub3c4\uad6c"],
        [
            ["Unit Test", "NlpService, ContextService, BusService", "pytest + pytest-asyncio"],
            ["Integration Test", "/query \uc804\uccb4 \ud30c\uc774\ud504\ub77c\uc778", "FastAPI TestClient"],
            ["UI Test", "\ub9d0\ud558\uae30 \ubc84\ud2bc, \ud504\ub9ac\uc14b, \uacb0\uacfc \ud654\uba74", "Compose UI Test"],
            ["E2E Test", "\uc74c\uc131 \u2192 NLP \u2192 \uc751\ub2f5 \uc804\uccb4 \ud750\ub984", "\uc2e4\uc81c \ud0dc\ube14\ub9bf + \uc11c\ubc84"],
        ],
        col_widths=[pw * 0.2, pw * 0.45, pw * 0.35]
    ))
    story.append(spacer(8))

    story.append(heading2("10-3. \ud14c\uc2a4\ud2b8 \ucee4\ubc84\ub9ac\uc9c0 \ubaa9\ud45c"))
    story.append(make_table(
        ["\ub808\uc774\uc5b4", "\ubaa9\ud45c", "\uadfc\uac70"],
        [
            ["NLP \uc11c\ube44\uc2a4", "90% \uc774\uc0c1", "\uc0ac\ud22c\ub9ac/\uc758\ub3c4/\uc720\uc0ac\uc5b4 \u2014 \uc624\ubd84\ub958\ub294 \uc5b4\ub974\uc2e0 \ud63c\ub780 \uc9c1\uacb0"],
            ["\ucee8\ud14d\uc2a4\ud2b8 \uc11c\ube44\uc2a4", "80% \uc774\uc0c1", "\uc5f0\uc18d \ub300\ud654 \uc815\ud655\uc131 \u2014 \ub300\uba85\uc0ac \ud574\uc11d \uc624\ub958 \ubc29\uc9c0"],
            ["API \ub77c\uc6b0\ud130", "70% \uc774\uc0c1", "\uc785\ucd9c\ub825 \uac80\uc99d, \uc5d0\ub7ec \ucf00\uc774\uc2a4 \ud655\uc778"],
            ["Android UI", "\uc8fc\uc694 \uc2dc\ub098\ub9ac\uc624", "\ub9d0\ud558\uae30 \u2192 \uacb0\uacfc \u2192 \ub2e4\uc2dc \uc9c8\ubb38 \ud750\ub984 \uac80\uc99d"],
        ],
        col_widths=[pw * 0.25, pw * 0.2, pw * 0.55]
    ))
    story.append(PageBreak())

    # ══════════════════════════════
    # 11. 화면 흐름 & 시니어 UX 설계
    # ══════════════════════════════
    story.append(heading1("11. \ud654\uba74 \ud750\ub984 & \uc2dc\ub2c8\uc5b4 UX \uc124\uacc4"))
    story.append(hr())

    flow_data = [
        [Paragraph("<b>[1] \uba54\uc778 \ud654\uba74</b>", S['td']),
         Paragraph("240dp \uc6d0\ud615 \ub9d0\ud558\uae30 \ubc84\ud2bc (5cm \uc774\uc0c1)\n"
                   "\"\uc5b4\ub514 \uac00\uc2dc\ub824\uace0\uc694?\" 48sp \uc548\ub0b4 \ubb38\uad6c\n"
                   "\uc790\uc8fc \uac00\ub294 \uacf3 3\uc5f4 \ud504\ub9ac\uc14b \ubc84\ud2bc", S['td'])],
        [Paragraph("<b>[2] \uc74c\uc131 \uc778\uc2dd \uc911</b>", S['td']),
         Paragraph("\ub9c8\uc774\ud06c \uc560\ub2c8\uba54\uc774\uc158 + \ud30c\ud615 \ud45c\uc2dc\n"
                   "\"\ub9d0\uc500\ud558\uc138\uc694...\" \uc548\ub0b4 \ud14d\uc2a4\ud2b8\n"
                   "3\ucd08 \uce68\ubb35 \uc2dc \uc790\ub3d9 \uc885\ub8cc", S['td'])],
        [Paragraph("<b>[3] \uacb0\uacfc \ud654\uba74</b>", S['td']),
         Paragraph("\ub3c4\ucc29 \ubc84\uc2a4 \ubaa9\ub85d (\ubc88\ud638, \ub3c4\ucc29 \uc2dc\uac04, \ub0a8\uc740 \uc815\uac70\uc7a5)\n"
                   "TTS \uc790\ub3d9 \uc548\ub0b4 (\uc74c\uc131 \uc77d\uc5b4\uc90c)\n"
                   "\"\ub2e4\uc2dc \ubb3c\uc5b4\ubcf4\uae30\" / \"\ucc98\uc74c\uc73c\ub85c\" \ud070 \ubc84\ud2bc", S['td'])],
        [Paragraph("<b>[4] \ud130\uce58 \ubc31\uc5c5</b>", S['td']),
         Paragraph("\uc74c\uc131 \uc2e4\ud328 \uc2dc \uc790\ub3d9 \uc804\ud658\n"
                   "\uc790\uc8fc \uac00\ub294 \uacf3 \ubc84\ud2bc \ud654\uba74 (120dp \uc774\uc0c1)\n"
                   "\ub204\ub974\uba74 \ud574\ub2f9 \ubaa9\uc801\uc9c0 \uc9c1\uc811 \uac80\uc0c9", S['td'])],
    ]
    flow_table = Table(flow_data, colWidths=[pw * 0.25, pw * 0.75])
    flow_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Malgun'),
        ('GRID', (0, 0), (-1, -1), 0.5, MID_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (0, -1), LIGHT_BG),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [white, LIGHT_GRAY]),
    ]))
    story.append(flow_table)
    story.append(Paragraph("[\ud45c] 4\uac1c \ud654\uba74\uc758 \uad6c\uc131 \ubc0f \ud575\uc2ec \uae30\ub2a5", S['caption']))
    story.append(spacer(8))

    story.append(heading2("\uc2dc\ub2c8\uc5b4 \ud2b9\ud654 UX \uc0c1\uc138"))
    story.append(make_table(
        ["\ud56d\ubaa9", "\uc77c\ubc18 \uc571", "BusGuide", "\uc774\uc720"],
        [
            ["\ud3f0\ud2b8 \ud06c\uae30", "14sp", "48sp (3.4\ubc30)", "\ub178\uc548 \uace0\ub824"],
            ["\ubc84\ud2bc \ucd5c\uc18c \ud06c\uae30", "48dp", "120dp (2.5\ubc30)", "\uc190\ub5a8\ub9bc \ub300\uc751"],
            ["\uc0c9\uc0c1", "\ub2e4\uc591", "\uace0\ub300\ube44 (\uac80\uc815+\ub178\ub791)", "\uc2dc\ub825 \uc57d\ud574\ub3c4 \uac00\ub3c5"],
            ["\ud53c\ub4dc\ubc31", "\uc2dc\uac01\ub9cc", "\uc74c\uc131+\uc2dc\uac01+\uc9c4\ub3d9", "\uc0bc\uc911 \ud655\uc778"],
            ["\ud130\uce58 \uc601\uc5ed", "\uc791\uc740 \ud328\ub529", "\ub113\uc740 \ud328\ub529", "\uc624\ud130\uce58 \ubc29\uc9c0"],
        ],
        col_widths=[pw * 0.17, pw * 0.17, pw * 0.3, pw * 0.36]
    ))
    story.append(PageBreak())

    # ══════════════════════════════
    # 12. 하드웨어 구성 및 비용
    # ══════════════════════════════
    story.append(heading1("12. \ud558\ub4dc\uc6e8\uc5b4 \uad6c\uc131 \ubc0f \ube44\uc6a9"))
    story.append(hr())

    story.append(heading2("12-1. \uc815\ub958\uc7a5 1\uacf3 \uc124\uce58 \ube44\uc6a9"))
    story.append(make_table(
        ["\ud488\ubaa9", "\uac00\uaca9", "\ube44\uace0"],
        [
            ["\uc911\uace0 \uac24\ub7ed\uc2dc \ud0ed A7 (10.4\uc778\uce58 LTE)", "7\ub9cc\uc6d0", "\ub178\uc548\uc5d0\ub3c4 \ubcfc \uc218 \uc788\ub294 \ud654\uba74 \ud06c\uae30"],
            ["\ubc29\uc218 \ucf00\uc774\uc2a4 (IP65)", "2\ub9cc\uc6d0", "\uc57c\uc678 \uc815\ub958\uc7a5 \uc124\uce58 \ub300\ube44"],
            ["\ubcf4\uc870 \ubc30\ud130\ub9ac + \ucda9\uc804\uae30", "3\ub9cc\uc6d0", "24\uc2dc\uac04 \uc5f0\uc18d \uc6b4\uc601"],
            ["\uc575\ucee4 \ubcfc\ud2b8 + \ucf00\uc774\ube14", "5\ucc9c\uc6d0", "\uc815\ub958\uc7a5 \ubd80\uc0b0\ub300 \uace0\uc815"],
            ["<b>\ud569\uacc4</b>", "<b>12.5\ub9cc\uc6d0</b>", "<b>BIS \uc804\uad11\ud310(300~500\ub9cc) \ub300\ube44 1/30</b>"],
        ],
        col_widths=[pw * 0.4, pw * 0.2, pw * 0.4]
    ))
    story.append(spacer(8))

    story.append(heading2("12-2. BIS \uc804\uad11\ud310 vs BusGuide \ube44\uad50"))
    story.append(make_table(
        ["\ud56d\ubaa9", "BIS \uc804\uad11\ud310", "BusGuide"],
        [
            ["\uc124\uce58 \ube44\uc6a9", "300~500\ub9cc\uc6d0", "12.5\ub9cc\uc6d0 (1/30)"],
            ["\uc815\ubcf4 \uc81c\uacf5", "\ub178\uc120\ubc88\ud638 + \ub3c4\ucc29\uc2dc\uac04", "\ubaa9\uc801\uc9c0 \uc548\ub0b4 + \ud658\uc2b9 + \ub300\ud654"],
            ["\uc778\ud130\ud398\uc774\uc2a4", "\uc2dc\uac01 (\uc804\uad11\ud310 \uc77d\uae30)", "\uc74c\uc131 + \uc2dc\uac01 + \ud130\uce58"],
            ["\uc0ac\ud22c\ub9ac \uc9c0\uc6d0", "X", "O (19\uac1c \ud328\ud134)"],
            ["\uc720\uc9c0\ubcf4\uc218", "\uc804\ubb38 \uc5c5\uccb4 \ud544\uc694", "\uc11c\ubc84 \uc5c5\ub370\uc774\ud2b8\ub85c \uc790\ub3d9 \uac1c\uc120"],
        ],
        col_widths=[pw * 0.25, pw * 0.35, pw * 0.4]
    ))
    story.append(PageBreak())

    # ══════════════════════════════
    # 13. 완성도 평가 & 향후 발전 방향
    # ══════════════════════════════
    story.append(heading1("13. \uc644\uc131\ub3c4 \ud3c9\uac00 & \ud5a5\ud6c4 \ubc1c\uc804 \ubc29\ud5a5"))
    story.append(hr())

    story.append(heading2("13-1. \ud604\uc7ac \uc644\uc131\ub3c4"))
    story.append(make_table(
        ["\ud3c9\uac00 \ud56d\ubaa9", "\uc0c1\ud0dc", "\uc124\uba85"],
        [
            ["\uc544\ud0a4\ud14d\ucc98 \uc124\uacc4", "\uc644\ub8cc", "Simple Client + Clean Architecture, Hilt DI"],
            ["\uc11c\ubc84 \ubf08\ub300 \ucf54\ub4dc", "\uc644\ub8cc", "NLP \ud30c\uc774\ud504\ub77c\uc778, TAGO \uc5f0\ub3d9, \ucee8\ud14d\uc2a4\ud2b8 \uc11c\ube44\uc2a4"],
            ["Android \ubf08\ub300 \ucf54\ub4dc", "\uc644\ub8cc", "Compose UI, STT/TTS, \ud0a4\uc624\uc2a4\ud06c \ubaa8\ub4dc"],
            ["\uc9c1\uc811 \uad6c\ud604\ud55c NLP", "\uc644\ub8cc", "\uc0ac\ud22c\ub9ac \ubcc0\ud658 + \uc758\ub3c4 \ubd84\ub958 + \uc720\uc0ac\uc5b4 \ub9e4\uce6d"],
            ["\ucee8\ud14d\uc2a4\ud2b8 \ub300\ud654", "\uc644\ub8cc", "\uc138\uc158 \uae30\ubc18 \uc5f0\uc18d \ub300\ud654 + \ub300\uba85\uc0ac \ud574\uc11d"],
            ["\uc11c\ubc84 \ud14c\uc2a4\ud2b8", "\uc644\ub8cc", "29\uac1c \ud14c\uc2a4\ud2b8 \uc804\uc218 \ud1b5\uacfc"],
            ["\uc2dc\ub2c8\uc5b4 UX", "\uc644\ub8cc", "48sp \ud3f0\ud2b8, \uace0\ub300\ube44, \uc0bc\uc911 \ud53c\ub4dc\ubc31"],
            ["\ud558\ub4dc\ucf54\ub529 0%", "\uc644\ub8cc", "\ubaa8\ub4e0 \ub370\uc774\ud130 JSON \ud30c\uc77c \ubd84\ub9ac"],
            ["TAGO \uc2e4\uc81c \uc5f0\ub3d9", "\uc9c4\ud589 \uc911", "\uc2e4\uc81c \ubc84\uc2a4 \ub370\uc774\ud130\ub85c \ud1b5\ud569 \ud14c\uc2a4\ud2b8 \uc608\uc815"],
        ],
        col_widths=[pw * 0.25, pw * 0.15, pw * 0.6]
    ))
    story.append(spacer(10))

    story.append(heading2("13-2. \ud5a5\ud6c4 \ubc1c\uc804 \ubc29\ud5a5"))

    story.append(heading3("\ub2e8\uae30 (\uc774\ubc88 \ud559\uae30)"))
    story.append(bullet(
        "<b>\uc2e4\uc81c \ud0dc\ube14\ub9bf \ud1b5\ud569 \ud14c\uc2a4\ud2b8</b> \u2014 "
        "Android \uc571 + FastAPI \uc11c\ubc84 \uc2e4\uc81c \uc5f0\ub3d9 \ud655\uc778"
    ))
    story.append(bullet(
        "<b>TAGO API \uc2e4\uc81c \ub370\uc774\ud130 \uc5f0\ub3d9</b> \u2014 "
        "\ubd80\uc0b0 \uc815\ub958\uc7a5 \uc2e4\uc2dc\uac04 \ubc84\uc2a4 \ub3c4\ucc29\uc815\ubcf4 \uac80\uc99d"
    ))
    story.append(bullet(
        "<b>\uc5b4\ub974\uc2e0 \uc0ac\uc6a9\uc790 \ud14c\uc2a4\ud2b8</b> \u2014 "
        "\ubcf5\uc9c0\uad00 \ud611\ub825\uc73c\ub85c \uc2e4\uc81c \uc0ac\uc6a9\uc131 \ud3c9\uac00"
    ))

    story.append(heading3("\uc911\uae30 (2\ud559\uae30)"))
    story.append(bullet(
        "<b>\uce94\ud37c\uc2a4 \uc154\ud2c0 \uc815\ub958\uc7a5 \uc124\uce58</b> \u2014 "
        "\ud30c\uc77c\ub7ff \uc6b4\uc601\uc73c\ub85c \uc2e4\uc81c \uc0ac\uc6a9 \ub370\uc774\ud130 \uc218\uc9d1"
    ))
    story.append(bullet(
        "<b>\uc0ac\ud22c\ub9ac/\uc720\uc0ac\uc5b4 \uc0ac\uc804 \ud655\uc7a5</b> \u2014 "
        "\uc0ac\uc6a9 \ub85c\uadf8 \uae30\ubc18 \uc0c8\ub85c\uc6b4 \uc0ac\ud22c\ub9ac/\uc720\uc0ac\uc5b4 \ucd94\uac00"
    ))

    story.append(heading3("\uc7a5\uae30"))
    story.append(bullet(
        "<b>\ub2e4\uad6d\uc5b4 \uc9c0\uc6d0</b> \u2014 "
        "\uc678\uad6d\uc778 \uad00\uad11\uac1d\uc744 \uc704\ud55c \uc601\uc5b4/\uc911\uad6d\uc5b4/\uc77c\ubcf8\uc5b4 \uc9c0\uc6d0"
    ))
    story.append(bullet(
        "<b>\uc9c0\uc790\uccb4 \ud611\ub825</b> \u2014 "
        "\uc2e4\uc81c \uc815\ub958\uc7a5 \ud655\ub300 \uc124\uce58"
    ))
    story.append(bullet(
        "<b>\ub0a0\uc528/\ubcf5\uc9c0\uad00 \uc815\ubcf4 \ud1b5\ud569</b> \u2014 "
        "\ubc84\uc2a4 \uc548\ub0b4 + \uc0dd\ud65c \uc815\ubcf4 \ud1b5\ud569 \ud50c\ub7ab\ud3fc"
    ))

    story.append(spacer(20))

    # 하단 마무리
    story.append(hr())
    story.append(spacer(8))
    story.append(Paragraph(
        "\ubcf8 \ubcf4\uace0\uc11c\ub294 BusGuide \uce85\uc2a4\ud1a4 \ub514\uc790\uc778 \ud504\ub85c\uc81d\ud2b8\uc758 \uc124\uacc4 \ubc0f \uad6c\ud604 \ud604\ud669\uc744 \uc815\ub9ac\ud55c \ubb38\uc11c\uc785\ub2c8\ub2e4.",
        ParagraphStyle('Footer', fontName='Malgun', fontSize=9, textColor=TEXT_GRAY, alignment=TA_CENTER)
    ))
    story.append(Paragraph(
        "2026\ub144 4\uc6d4 | \uac1c\ubc1c\uc790: \ud604\uc218",
        ParagraphStyle('Footer2', fontName='Malgun', fontSize=9, textColor=TEXT_GRAY, alignment=TA_CENTER)
    ))

    # ── 페이지 번호 추가 함수 ──
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        if page_num > 1:  # 표지 제외
            canvas.saveState()
            canvas.setFont('Malgun', 8)
            canvas.setFillColor(TEXT_GRAY)
            canvas.drawCentredString(A4[0] / 2, 1.2 * cm, f"- {page_num - 1} -")
            # 헤더
            canvas.setFont('Malgun', 7)
            canvas.drawString(2.2 * cm, A4[1] - 1.2 * cm, "BusGuide | \uce85\uc2a4\ud1a4 \ubc1c\ud45c \ubcf4\uace0\uc11c")
            canvas.setStrokeColor(MID_GRAY)
            canvas.setLineWidth(0.5)
            canvas.line(2.2 * cm, A4[1] - 1.4 * cm, A4[0] - 2.2 * cm, A4[1] - 1.4 * cm)
            canvas.restoreState()

    # ── PDF 빌드 ──
    doc.build(story, onFirstPage=draw_cover_page, onLaterPages=add_page_number)
    print(f"PDF \uc0dd\uc131 \uc644\ub8cc: {output_path}")
    return output_path


if __name__ == "__main__":
    build_pdf()
