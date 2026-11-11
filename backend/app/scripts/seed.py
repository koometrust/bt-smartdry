import asyncio
import logging
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.hub import Hub
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")


async def seed_data():
    async with engine.begin() as conn:
        # Create tables if not exist
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Seed Hubs
        hubs_data = [
            {"name": "Meru", "location": "Meru County, Eastern Kenya", "dryer_capacity_kg": 200.0},
            {"name": "Tharaka Nithi", "location": "Tharaka Nithi County, Eastern Kenya", "dryer_capacity_kg": 200.0},
            {"name": "Eldoret", "location": "Uasin Gishu County, Rift Valley", "dryer_capacity_kg": 200.0},
        ]

        hubs_by_name = {}
        for h in hubs_data:
            res = await session.execute(select(Hub).where(Hub.name == h["name"]))
            existing = res.scalar_one_or_none()
            if not existing:
                hub = Hub(
                    name=h["name"],
                    location=h["location"],
                    dryer_capacity_kg=h["dryer_capacity_kg"]
                )
                session.add(hub)
                await session.flush()
                hubs_by_name[h["name"]] = hub
                logger.info(f"Created Hub: {h['name']} ({hub.id})")
            else:
                hubs_by_name[h["name"]] = existing
                logger.info(f"Hub exists: {h['name']} ({existing.id})")

        # 2. Seed Users
        users_data = [
            {
                "username": "admin",
                "password": "AdminPass123!",
                "role": "admin",
                "hub_id": None,
                "preferred_language": "en",
                "phone_number": "+254700000001"
            },
            {
                "username": "op_meru",
                "password": "MeruPass123!",
                "role": "operator",
                "hub_id": hubs_by_name["Meru"].id,
                "preferred_language": "en",
                "phone_number": "+254711000001"
            },
            {
                "username": "op_tharaka",
                "password": "TharakaPass123!",
                "role": "operator",
                "hub_id": hubs_by_name["Tharaka Nithi"].id,
                "preferred_language": "sw",
                "phone_number": "+254711000002"
            },
            {
                "username": "op_eldoret",
                "password": "EldoretPass123!",
                "role": "operator",
                "hub_id": hubs_by_name["Eldoret"].id,
                "preferred_language": "en",
                "phone_number": "+254711000003"
            },
        ]

        for u in users_data:
            res = await session.execute(select(User).where(User.username == u["username"]))
            existing = res.scalar_one_or_none()
            if not existing:
                user = User(
                    username=u["username"],
                    hashed_password=get_password_hash(u["password"]),
                    role=u["role"],
                    hub_id=u["hub_id"],
                    preferred_language=u["preferred_language"],
                    phone_number=u["phone_number"]
                )
                session.add(user)
                logger.info(f"Created User: {u['username']} (Role: {u['role']})")
            else:
                logger.info(f"User exists: {u['username']}")

        await session.commit()
        logger.info("Database seeding successfully completed!")


if __name__ == "__main__":
    asyncio.run(seed_data())

