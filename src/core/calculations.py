from datetime import datetime, time
import pytz
import re
from src.core.logging_setup import logger

def validate_and_convert_time(time_str, default_time=None):
    """Валидация и конвертация строки времени в объект time."""
    try:
        if not time_str or not re.match(r'^\d{2}:\d{2}$', time_str):
            return default_time
        hours, minutes = map(int, time_str.split(':'))
        if 0 <= hours <= 23 and 0 <= minutes <= 59:
            return time(hours, minutes)
        return default_time
    except Exception as e:
        logger.error(f"Ошибка валидации времени '{time_str}': {str(e)}")
        return default_time

def determine_status(entry_datetime, release_datetime):
    """Определение статуса сделки."""
    try:
        if entry_datetime is None and release_datetime is None:
            return "Ожидание"
        elif entry_datetime is not None and release_datetime is None:
            return "Активная"
        elif entry_datetime is not None and release_datetime is not None:
            return "Закрытая"
        return "Ожидание"
    except Exception as e:
        logger.error(f"Ошибка определения статуса: {str(e)}")
        return "Ожидание"

def determine_direction(entry_point, stop_loss):
    """Определение направления сделки."""
    try:
        return "Long" if entry_point > stop_loss else "Short" if entry_point < stop_loss else "Long"
    except Exception as e:
        logger.error(f"Ошибка определения направления: {str(e)}")
        return "Long"

def calculate_fields(
    entry_point, stop_loss, take_profit_one, take_profit_two, take_profit_three,
    take_profit_one_percent, take_profit_two_percent, take_profit_three_percent,
    entry_date, release_date, timezone, risk_percent, tick_size, reward_risk
):
    """Расчёт полей сделки."""
    try:
        # Установка timezone по умолчанию
        timezone = timezone if timezone is not None else 0
        logger.debug(f"Расчёт полей: entry_date={entry_date}, timezone={timezone}")

        duration_hours = (release_date - entry_date).total_seconds() / 3600 if entry_date and release_date else 0
        entry_date_only = entry_date.date() if entry_date else None
        release_date_only = release_date.date() if release_date else None
        trade_type = "Scalping" if 0 < duration_hours < 1 else "Intraday" if entry_date_only == release_date_only else "Swing"

        local_tz = pytz.UTC
        entry_date = entry_date.replace(tzinfo=local_tz) if entry_date else datetime.now(tz=local_tz)
        local_time = entry_date.astimezone(pytz.FixedOffset(timezone * 60))
        logger.debug(f"Локальное время входа: {local_time}, час: {local_time.hour}")
        session = "Asia" if 0 <= local_time.hour < 8 else "Europe" if 8 <= local_time.hour < 16 else "America"
        logger.debug(f"Определена сессия: {session}")

        direction = determine_direction(entry_point, stop_loss)
        tick_multiplier = 10 ** tick_size
        avg_rr = 0.0
        weighted_rr = 0.0

        if stop_loss and entry_point != stop_loss:
            risk_ticks = (entry_point - stop_loss) * tick_multiplier if direction.lower() == "long" else (stop_loss - entry_point) * tick_multiplier
            for tp, percent in [(take_profit_one, take_profit_one_percent), (take_profit_two, take_profit_two_percent), (take_profit_three, take_profit_three_percent)]:
                if tp and percent > 0:
                    if tp == stop_loss:
                        rr = -1
                    else:
                        reward_ticks = (tp - entry_point) * tick_multiplier if direction.lower() == "long" else (entry_point - tp) * tick_multiplier
                        rr = reward_ticks / risk_ticks if risk_ticks != 0 else 0
                    weighted_rr += rr * (percent / 100)
            avg_rr = weighted_rr

        if risk_percent != reward_risk and reward_risk != 0:
            avg_rr *= risk_percent / reward_risk
        avg_rr = round(avg_rr, 3)

        profit_percent = avg_rr * risk_percent if stop_loss and any([take_profit_one, take_profit_two, take_profit_three]) else 0
        if any((tp == stop_loss and percent == 100) for tp, percent in [(take_profit_one, take_profit_one_percent), (take_profit_two, take_profit_two_percent), (take_profit_three, take_profit_three_percent)]):
            profit_percent = -risk_percent
        profit_percent = round(profit_percent, 3)

        result = "Loss" if profit_percent == -risk_percent else "Win" if profit_percent > 0 else "Loss" if profit_percent < 0 else "Breakeven"
        logger.debug(f"Результат расчёта: trade_type={trade_type}, session={session}, avg_rr={avg_rr}, profit_percent={profit_percent}, result={result}, direction={direction}")
        return trade_type, session, avg_rr, profit_percent, result, direction
    except Exception as e:
        logger.error(f"Ошибка расчёта полей: {str(e)}")
        return "Swing", "Europe", 0.0, 0.0, "Breakeven", "Long"