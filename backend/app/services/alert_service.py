import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.alert import Alert
from app.models.batch import Batch
from app.models.user import User
from app.schemas.alert import AlertType, AlertStatus

logger = logging.getLogger(__name__)


async def trigger_alert_if_needed(
    db: AsyncSession,
    batch: Batch,
    alert_type: AlertType,
    message: str
) -> Optional[Alert]:
    # 1. Enforce max 1 alert per alert_type per batch
    existing_query = select(Alert).where(
        Alert.batch_id == batch.id,
        Alert.alert_type == alert_type.value
    )
    res = await db.execute(existing_query)
    if res.scalar_one_or_none():
        return None  # Duplicate suppressed

    # 2. Determine recipient operator phone number
    recipient_phone = "+254700000000"
    if batch.created_by_user_id:
        user = await db.get(User, batch.created_by_user_id)
        if user and user.phone_number:
            recipient_phone = user.phone_number

    # 3. Send SMS based on SMS_PROVIDER_MODE (mock, sandbox, live)
    mode = getattr(settings, "SMS_PROVIDER_MODE", "mock").lower()
    sms_status = AlertStatus.SENT
    try:
        if mode == "mock":
            logger.info(f"[SMS MOCK DISPATCH] To: {recipient_phone} | Msg: {message}")
        elif mode == "sandbox":
            import africastalking
            username = settings.AFRICASTALKING_USERNAME or "sandbox"
            africastalking.initialize(username, settings.AFRICASTALKING_API_KEY)
            sms = africastalking.SMS
            sms.send(message, [recipient_phone], settings.AFRICASTALKING_SENDER_ID)
            logger.info(f"[SMS SANDBOX DISPATCH] To: {recipient_phone} | Msg: {message}")
        elif mode == "live":
            import africastalking
            africastalking.initialize(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
            sms = africastalking.SMS
            sms.send(message, [recipient_phone], settings.AFRICASTALKING_SENDER_ID)
            logger.info(f"[SMS LIVE DISPATCH] To: {recipient_phone} | Msg: {message}")
        else:
            logger.warning(f"Unknown SMS_PROVIDER_MODE '{mode}', falling back to mock")
            logger.info(f"[SMS MOCK DISPATCH] To: {recipient_phone} | Msg: {message}")
    except Exception as e:
        logger.warning(f"Failed to dispatch SMS via Africa's Talking ({mode}): {e}")
        sms_status = AlertStatus.FAILED

    # 4. Save alert record
    alert = Alert(
        batch_id=batch.id,
        alert_type=alert_type.value,
        channel="sms",
        message=message,
        phone_number=recipient_phone,
        status=sms_status.value,
        is_read=False,
        sent_at=datetime.now(timezone.utc)
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    return alert

