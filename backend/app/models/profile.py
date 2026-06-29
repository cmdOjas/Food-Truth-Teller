"""User health profile model."""
from datetime import datetime, timezone
from sqlalchemy import JSON
from app import db


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    weight_kg = db.Column(db.Float)
    height_cm = db.Column(db.Float)
    bmi = db.Column(db.Float)
    health_conditions = db.Column(JSON, default=list)
    allergies = db.Column(JSON, default=list)
    diet_preference = db.Column(db.String(50))
    goals = db.Column(JSON, default=list)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", back_populates="profile")

    def compute_bmi(self) -> float | None:
        if self.weight_kg and self.height_cm and self.height_cm > 0:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m ** 2), 2)
        return None

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "age": self.age,
            "gender": self.gender,
            "weight_kg": self.weight_kg,
            "height_cm": self.height_cm,
            "bmi": self.bmi,
            "health_conditions": self.health_conditions or [],
            "allergies": self.allergies or [],
            "diet_preference": self.diet_preference,
            "goals": self.goals or [],
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<UserProfile user_id={self.user_id}>"
