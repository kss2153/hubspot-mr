from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Template(Base):
    __tablename__ = 'template'
    id = Column(Integer, primary_key=True)
    hub_id = Column(String(50))
    template_id = Column(String(50))
    template_name = Column(String(50))
    associated_object = Column(String(10))

    def __repr__(self):
        return "<Template(hubId='%d', fileId='%d', name='%d')>" % (self.hub_id, self.template_id, self.template_name)
