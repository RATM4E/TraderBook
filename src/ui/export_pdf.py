import pandas as pd
import os
import io
from src.core.config import BASE_DIR
from src.core.logging_setup import logger
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Регистрируем системные шрифты Arial
try:
    pdfmetrics.registerFont(TTFont('Arial', r'C:\Windows\Fonts\arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', r'C:\Windows\Fonts\arialbd.ttf'))
except Exception as e:
    logger.error(f"Ошибка регистрации шрифтов Arial: {str(e)}")
    # В качестве запасного варианта используем Times New Roman
    pdfmetrics.registerFont(TTFont('Arial', r'C:\Windows\Fonts\times.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', r'C:\Windows\Fonts\timesbd.ttf'))

def export_monte_carlo_to_pdf(market, lang, summary_df, fig_equity, fig_drawdown, fig_heatmap, optimal_results):
    """Экспорт результатов симуляции Монте-Карло в PDF с использованием reportlab."""
    try:
        # Логируем текущую рабочую директорию
        logger.info(f"Текущая рабочая директория: {os.getcwd()}")

        # Формируем путь к папке reports относительно BASE_DIR
        reports_dir = os.path.join(BASE_DIR, "data", "reports")
        logger.info(f"Попытка создать директорию: {reports_dir}")
        os.makedirs(reports_dir, exist_ok=True)
        if os.path.exists(reports_dir):
            logger.info(f"Директория {reports_dir} существует или создана")
        else:
            logger.error(f"Не удалось создать или найти директорию {reports_dir}")
            raise FileNotFoundError(f"Директория {reports_dir} не существует")

        # Проверяем права доступа
        test_file = os.path.join(reports_dir, "test.txt")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            logger.info(f"Права на запись в {reports_dir} подтверждены")
        except Exception as e:
            logger.error(f"Нет прав на запись в {reports_dir}: {str(e)}")
            raise PermissionError(f"Нет прав на запись в {reports_dir}: {str(e)}")

        # Формируем имя PDF-файла
        pdf_filename = f"monte_carlo_{market}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_file = os.path.join(reports_dir, pdf_filename)
        logger.info(f"Создание PDF в: {pdf_file}")

        # Логируем структуру summary_df
        if not summary_df.empty:
            logger.info(f"Столбцы summary_df: {list(summary_df.columns)}")
            logger.info(f"Первые строки summary_df:\n{summary_df.head().to_string()}")
        else:
            logger.warning("summary_df пустой")
        logger.info(f"Оптимальные результаты: {optimal_results}")

        # Настройка стилей для PDF с использованием Arial
        logger.info("Настройка стилей PDF")
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            name='Title',
            fontName='Arial-Bold',
            fontSize=20,
            leading=24,
            alignment=1,  # Center
            spaceAfter=12
        )
        subtitle_style = ParagraphStyle(
            name='Subtitle',
            fontName='Arial',
            fontSize=12,
            leading=14,
            alignment=1,
            spaceAfter=12
        )
        section_style = ParagraphStyle(
            name='Section',
            fontName='Arial-Bold',
            fontSize=14,
            leading=16,
            spaceBefore=12,
            spaceAfter=6
        )
        normal_style = ParagraphStyle(
            name='Normal',
            fontName='Arial',
            fontSize=10,
            leading=12
        )

        # Создание PDF в памяти для скачивания
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
        elements = []

        # Заголовок
        logger.info("Добавление заголовка в PDF")
        title = lang.get('monte_carlo_report', 'Отчёт по симуляции Монте-Карло') + f" для {market}"
        # Очищаем текст от невидимых символов
        title = ''.join(c for c in title if ord(c) < 128 or 1024 <= ord(c) <= 1279).strip()
        elements.append(Paragraph(title, title_style))
        elements.append(Paragraph(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), subtitle_style))
        elements.append(Spacer(1, 0.25 * inch))

        # Оптимальные стратегии
        logger.info("Добавление оптимальных стратегий в PDF")
        elements.append(Paragraph(lang.get('optimal_strategies', 'Оптимальные стратегии'), section_style))
        strategies = []
        for key in ['max_profit', 'min_drawdown', 'balanced']:
            value = optimal_results.get(key, ['N/A', 'N/A'])
            strategy_text = f"<b>{lang.get(f'{key}_strategy', key.replace('_', ' ').title())}:</b> {value[0]} ({value[1]})"
            # Фильтр для кириллицы и латинских символов
            strategy_text = ''.join(c for c in strategy_text if ord(c) < 128 or 1024 <= ord(c) <= 1279).strip()
            strategies.append(strategy_text)
        for strategy in strategies:
            elements.append(Paragraph(strategy, normal_style))
        elements.append(Spacer(1, 0.25 * inch))

        # Таблица результатов
        logger.info("Добавление таблицы результатов в PDF")
        elements.append(Paragraph(lang.get('results_table', 'Таблица результатов'), section_style))
        table_headers = [
            lang.get('trade_setup', 'Сетап').replace('\t', ' ').strip(),
            lang.get('timeframe', 'Таймфрейм').replace('\t', ' ').strip(),
            lang.get('avg_profit', 'Средняя прибыль, %').replace('\t', ' ').strip(),
            lang.get('avg_drawdown', 'Средняя просадка, %').replace('\t', ' ').strip(),
            lang.get('avg_recovery_factor', 'Коэффициент восстановления').replace('\t', ' ').strip()
        ]
        # Очищаем заголовки
        table_headers = [''.join(c for c in h if ord(c) < 128 or 1024 <= ord(c) <= 1279).strip() for h in table_headers]
        table_data = [table_headers]
        if not summary_df.empty:
            summary_df = summary_df.replace([float('inf'), -float('inf')], 0)
            summary_df.columns = [col.replace('\t', ' ').strip() for col in summary_df.columns]
            for _, row in summary_df.iterrows():
                table_row = [
                    str(row.get('Сетап', '')).replace('\t', ' ').strip(),
                    str(row.get('Таймфрейм', '')).replace('\t', ' ').strip(),
                    f"{row.get('Средняя прибыль, %', 0):.2f}",
                    f"{row.get('Средняя просадка, %', 0):.2f}",
                    f"{row.get('Коэффициент восстановления', 0):.2f}"
                ]
                # Очищаем данные
                table_row = [''.join(c for c in r if ord(c) < 128 or 1024 <= ord(c) <= 1279).strip() for r in table_row]
                table_data.append(table_row)
        else:
            table_data.append(['Нет данных', '', '0.00', '0.00', '0.00'])
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Arial-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.25 * inch))

        # Временно отключили графики для диагностики
        logger.info("Графики временно отключены для устранения зависания")

        # Сохранение PDF в памяти
        logger.info("Генерация PDF в памяти")
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        # Сохранение PDF на диск
        logger.info(f"Сохранение PDF на диск: {pdf_file}")
        with open(pdf_file, 'wb') as f:
            f.write(pdf_bytes)
        if os.path.exists(pdf_file):
            logger.info(f"PDF успешно сохранён на диск: {pdf_file}")
        else:
            logger.error(f"PDF не найден на диске после сохранения: {pdf_file}")
            raise FileNotFoundError(f"PDF не найден на диске: {pdf_file}")

        return pdf_file, pdf_bytes

    except Exception as e:
        logger.error(f"Ошибка при экспорте PDF для {market}: {str(e)}")
        raise