from app import Base, engine
from sqlalchemy.sql import func
from sqlalchemy import DateTime, Column, Integer, String

class Places(Base):
    __tablename__ = 'places'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    place = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    visit_date = Column(String(50), nullable=False)
    transport = Column(String(50), nullable=False)
    reg_date = Column(DateTime(timezone=True), default=func.now())

    def toDict(self):
        return {
            'id': self.id,
            'place': self.place,
            'country': self.country,
            'visit_date': self.visit_date,
            'transport': self.transport,
        }

Base.metadata.create_all(bind=engine)