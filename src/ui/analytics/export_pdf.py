# Изменения в src/ui/analytics/export_pdf.py
# (предполагается, что в src/ui/export_pdf.py нет уникального функционала,
# которого нет в src/ui/analytics/export_pdf.py, кроме импорта.
# Если есть, его нужно будет перенести.)

# src/ui/analytics/export_pdf.py
import pandas as pd
import os
import io
from src.core.config import BASE_DIR, LOGS_DIR # Добавлен LOGS_DIR для сохранения логов PDF
from src.core.logging_setup import logger
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as ReportLabImage # Добавлен PageBreak и ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO # Добавлен BytesIO

# Регистрируем системные шрифты Arial
try:
    # Используем относительные пути для надежности, если приложение запускается из другого места
    # или требуются специфические шрифты, которые могут быть вложены в ресурсы приложения.
    # Для системных шрифтов Windows путь остается таким, какой он есть.
    pdfmetrics.registerFont(TTFont('Arial', r'C:\\Windows\\Fonts\\arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', r'C:\\Windows\\Fonts\\arialbd.ttf'))
    logger.info("Шрифты Arial успешно зарегистрированы.")
except Exception as e:
    logger.error(f"Ошибка регистрации шрифтов Arial: {str(e)}. Использование Times New Roman в качестве запасного варианта.")
    # В качестве запасного варианта используем Times New Roman
    pdfmetrics.registerFont(TTFont('Arial', r'C:\\Windows\\Fonts\\times.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', r'C:\\Windows\\Fonts\\timesbd.ttf'))


def create_colored_text_style(color_hex):
    """Создает стиль параграфа с заданным цветом."""
    styles = getSampleStyleSheet()
    style = ParagraphStyle('ColoredText', parent=styles['Normal'])
    style.textColor = colors.HexColor(color_hex)
    return style

def export_monte_carlo_to_pdf(market, lang, summary_df, fig_equity, fig_drawdown, fig_heatmap, optimal_results, initial_balance=0):
    """Экспорт результатов симуляции Монте-Карло в PDF с использованием reportlab."""
    try:
        pdf_file = os.path.join(LOGS_DIR, f"Monte_Carlo_Report_{market}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
        elements = []
        styles = getSampleStyleSheet()

        # Заголовок
        elements.append(Paragraph(lang.get('monte_carlo_simulation_report_title', f"Отчет по симуляции Монте-Карло ({market})"), styles['Title']))
        elements.append(Spacer(1, 0.2 * inch))

        # Стартовый капитал
        if initial_balance > 0:
            elements.append(Paragraph(f"<b>{lang.get('initial_balance', 'Стартовый капитал')}:</b> ${initial_balance:,.2f}", styles['Normal']))
            elements.append(Spacer(1, 0.1 * inch))

        # Общая сводка
        elements.append(Paragraph(lang.get('simulation_summary', 'Общая сводка симуляции'), styles['h2']))
        if not summary_df.empty:
            data = [
                [lang.get('metric', 'Метрика'), lang.get('value', 'Значение')]
            ]
            for index, row in summary_df.iterrows():
                metric_name = lang.get(row['metric_key'], row['metric_key']) # Использование ключа перевода
                value = row['value']
                data.append([metric_name, value])

            table = Table(data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10475a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Arial-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f2f9f2')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.25 * inch))
        else:
            elements.append(Paragraph(lang.get('no_summary_data', 'Нет данных для сводки симуляции.'), styles['Normal']))
        
        elements.append(PageBreak()) # Добавляем разрыв страницы

        # Оптимальные стратегии
        elements.append(Paragraph(lang.get('optimal_strategies', 'Оптимальные стратегии'), styles['h2']))
        if optimal_results:
            elements.append(Paragraph(f"<b>{lang.get('max_profit_strategy', 'Макс. прибыль')}:</b> {lang.get('trade_setup', 'Сетап')}: {optimal_results['max_profit'][0]}, {lang.get('timeframe', 'Таймфрейм')}: {optimal_results['max_profit'][1]}", styles['Normal']))
            elements.append(Paragraph(f"<b>{lang.get('min_drawdown_strategy', 'Мин. просадка')}:</b> {lang.get('trade_setup', 'Сетап')}: {optimal_results['min_drawdown'][0]}, {lang.get('timeframe', 'Таймфрейм')}: {optimal_results['min_drawdown'][1]}", styles['Normal']))
            elements.append(Paragraph(f"<b>{lang.get('balanced_strategy', 'Баланс')}:</b> {lang.get('trade_setup', 'Сетап')}: {optimal_results['balanced'][0]}, {lang.get('timeframe', 'Таймфрейм')}: {optimal_results['balanced'][1]}", styles['Normal']))
            elements.append(Spacer(1, 0.25 * inch))
        else:
            elements.append(Paragraph(lang.get('no_optimal_strategies', 'Нет оптимальных стратегий.'), styles['Normal']))

        # Визуализации
        elements.append(Paragraph(lang.get('visualizations', 'Визуализация'), styles['h2']))
        
        # Графики: сохраняем как изображение и вставляем
        image_width = 500
        image_height = 300

        if fig_equity:
            equity_img_buffer = BytesIO()
            fig_equity.write_image(equity_img_buffer, format='png', width=image_width, height=image_height, scale=2)
            equity_img_buffer.seek(0)
            img = ReportLabImage(equity_img_buffer)
            img.drawWidth = image_width * 0.7 # Уменьшаем размер для PDF
            img.drawHeight = image_height * 0.7
            elements.append(Paragraph(lang.get('monte_carlo_equity', 'Кривые эквити Монте-Карло'), styles['h3']))
            elements.append(img)
            elements.append(Spacer(1, 0.1 * inch))

        if fig_drawdown:
            drawdown_img_buffer = BytesIO()
            fig_drawdown.write_image(drawdown_img_buffer, format='png', width=image_width, height=image_height, scale=2)
            drawdown_img_buffer.seek(0)
            img = ReportLabImage(drawdown_img_buffer)
            img.drawWidth = image_width * 0.7
            img.drawHeight = image_height * 0.7
            elements.append(Paragraph(lang.get('monte_carlo_drawdown_histogram', 'Гистограмма максимальных просадок'), styles['h3']))
            elements.append(img)
            elements.append(Spacer(1, 0.1 * inch))

        if fig_heatmap:
            heatmap_img_buffer = BytesIO()
            fig_heatmap.write_image(heatmap_img_buffer, format='png', width=image_width, height=image_height, scale=2)
            heatmap_img_buffer.seek(0)
            img = ReportLabImage(heatmap_img_buffer)
            img.drawWidth = image_width * 0.7
            img.drawHeight = image_height * 0.7
            elements.append(Paragraph(lang.get('monte_carlo_heatmap', 'Тепловая карта прибыли'), styles['h3']))
            elements.append(img)
            elements.append(Spacer(1, 0.1 * inch))


        # Сохранение PDF в памяти
        logger.info("Генерация PDF в памяти")
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        # Сохранение PDF на диск
        logger.info(f"Сохранение PDF на диск: {pdf_file}")
        with open(pdf_file, 'wb') as f:
            f.write(pdf_bytes)
        
        logger.info(f"PDF отчет успешно создан: {pdf_file}")
        return pdf_file, pdf_bytes
    except Exception as e:
        logger.error(f"Ошибка при экспорте Монте-Карло в PDF для {market}: {str(e)}")
        raise

def export_analytics_to_pdf(market, lang, metrics, profit_loss_data=None, long_short_data=None, equity_drawdown_figure=None, activity_data=None, initial_balance=0):
    """Экспорт аналитики в PDF."""
    try:
        pdf_file = os.path.join(LOGS_DIR, f"Analytics_Report_{market}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph(lang.get('analytics_report_title', f"Отчет по аналитике ({market})"), styles['Title']))
        elements.append(Spacer(1, 0.2 * inch))

        # Стартовый капитал
        if initial_balance > 0:
            elements.append(Paragraph(f"<b>{lang.get('initial_balance', 'Стартовый капитал')}:</b> ${initial_balance:,.2f}", styles['Normal']))
            elements.append(Spacer(1, 0.1 * inch))

        # Общие метрики
        elements.append(Paragraph(lang.get('general_metrics', 'Общие метрики'), styles['h2']))
        if metrics:
            data = [
                [lang.get('metric', 'Метрика'), lang.get('value', 'Значение')]
            ]
            for key, value in metrics.items():
                metric_name = lang.get(key, key)
                data.append([metric_name, value])
            
            table = Table(data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10475a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Arial-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f2f9f2')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.25 * inch))
        else:
            elements.append(Paragraph(lang.get('no_metrics_data', 'Нет данных для общих метрик.'), styles['Normal']))

        elements.append(PageBreak())

        # Прибыль и убытки
        elements.append(Paragraph(lang.get('profit_loss', 'Прибыль и убытки'), styles['h2']))
        if profit_loss_data:
            elements.append(Paragraph(f"<b>{lang.get('profit', 'Прибыль')}:</b> {profit_loss_data.get('total_profit', 0):.2f}", styles['Normal']))
            elements.append(Paragraph(f"<b>{lang.get('loss', 'Убытки')}:</b> {profit_loss_data.get('total_loss', 0):.2f}", styles['Normal']))
            if profit_loss_data.get('monthly_profit_loss_fig'):
                monthly_pl_buffer = BytesIO()
                profit_loss_data['monthly_profit_loss_fig'].write_image(monthly_pl_buffer, format='png', width=500, height=300, scale=2)
                monthly_pl_buffer.seek(0)
                img = ReportLabImage(monthly_pl_buffer)
                img.drawWidth = 500 * 0.7
                img.drawHeight = 300 * 0.7
                elements.append(Paragraph(lang.get('monthly_profit_loss', 'Прибыль/убытки по месяцам'), styles['h3']))
                elements.append(img)
            if profit_loss_data.get('profit_loss_pie_fig'):
                pl_pie_buffer = BytesIO()
                profit_loss_data['profit_loss_pie_fig'].write_image(pl_pie_buffer, format='png', width=500, height=300, scale=2)
                pl_pie_buffer.seek(0)
                img = ReportLabImage(pl_pie_buffer)
                img.drawWidth = 500 * 0.7
                img.drawHeight = 300 * 0.7
                elements.append(Paragraph(lang.get('profit_loss_distribution', 'Распределение прибыли/убытков'), styles['h3']))
                elements.append(img)
            elements.append(Spacer(1, 0.25 * inch))
        else:
            elements.append(Paragraph(lang.get('no_profit_loss_data', 'Нет данных по прибыли и убыткам.'), styles['Normal']))

        elements.append(PageBreak())

        # Длинные и короткие позиции
        elements.append(Paragraph(lang.get('long_short_positions', 'Длинные и короткие позиции'), styles['h2']))
        if long_short_data:
            elements.append(Paragraph(f"<b>{lang.get('long_trades', 'Длинные сделки')}:</b> {long_short_data.get('long_count', 0)}", styles['Normal']))
            elements.append(Paragraph(f"<b>{lang.get('short_trades', 'Короткие сделки')}:</b> {long_short_data.get('short_count', 0)}", styles['Normal']))
            if long_short_data.get('long_short_pie_fig'):
                ls_pie_buffer = BytesIO()
                long_short_data['long_short_pie_fig'].write_image(ls_pie_buffer, format='png', width=500, height=300, scale=2)
                ls_pie_buffer.seek(0)
                img = ReportLabImage(ls_pie_buffer)
                img.drawWidth = 500 * 0.7
                img.drawHeight = 300 * 0.7
                elements.append(Paragraph(lang.get('long_short_distribution', 'Распределение длинных/коротких позиций'), styles['h3']))
                elements.append(img)
            elements.append(Spacer(1, 0.25 * inch))
        else:
            elements.append(Paragraph(lang.get('no_long_short_data', 'Нет данных по длинным/коротким позициям.'), styles['Normal']))

        elements.append(PageBreak())

        # Риски
        elements.append(Paragraph(lang.get('risks', 'Риски'), styles['h2']))
        if equity_drawdown_figure or activity_data:
            if equity_drawdown_figure:
                equity_drawdown_buffer = BytesIO()
                equity_drawdown_figure.write_image(equity_drawdown_buffer, format='png', width=700, height=400, scale=2) # Увеличенная ширина
                equity_drawdown_buffer.seek(0)
                img = ReportLabImage(equity_drawdown_buffer)
                img.drawWidth = 700 * 0.7
                img.drawHeight = 400 * 0.7
                elements.append(Paragraph(lang.get('balance_drawdown_chart', 'График баланса/просадки по времени'), styles['h3']))
                elements.append(img)
            if activity_data and activity_data.get('day_of_week_fig'):
                day_of_week_buffer = BytesIO()
                activity_data['day_of_week_fig'].write_image(day_of_week_buffer, format='png', width=500, height=300, scale=2)
                day_of_week_buffer.seek(0)
                img = ReportLabImage(day_of_week_buffer)
                img.drawWidth = 500 * 0.7
                img.drawHeight = 300 * 0.7
                elements.append(Paragraph(lang.get('activity_by_day_of_week', 'Активность по дням недели'), styles['h3']))
                elements.append(img)
            elements.append(Spacer(1, 0.25 * inch))
        else:
            elements.append(Paragraph(lang.get('no_risk_data', 'Нет данных по рискам.'), styles['Normal']))


        # Build PDF
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(f"PDF отчет по аналитике успешно создан: {pdf_file}")
        return pdf_file, pdf_bytes

    except Exception as e:
        logger.error(f"Ошибка при экспорте аналитики в PDF для {market}: {str(e)}")
        raise

# NOTE: The original export_monte_carlo_to_pdf function had a line:
# logger.info("Графики временно отключены для диагностики")
# This line has been removed to re-enable chart export.
# If charts are causing issues, it means there might be an issue with Plotly's rendering to static image or ReportLab integration.