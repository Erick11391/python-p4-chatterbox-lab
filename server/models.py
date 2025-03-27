from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, DateTime
from sqlalchemy.sql import func
from sqlalchemy_serializer import SerializerMixin

# Define naming convention for constraints
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Initialize SQLAlchemy with metadata
db = SQLAlchemy(metadata=metadata)

class Message(db.Model, SerializerMixin):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(255), nullable=False)  # Added max length
    username = db.Column(db.String(50), nullable=False)  # Added max length
    created_at = db.Column(DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(DateTime(timezone=True), onupdate=func.now())

    # Serialization rules (exclude timestamps from serialization)
    serialize_rules = ('-created_at', '-updated_at')

    def __repr__(self):
        return f'<Message id={self.id}, username={self.username}, body={self.body[:20]}...>'

    # Add a to_dict method for better control (optional but recommended)
    def to_dict(self):
        return {
            'id': self.id,
            'body': self.body,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }