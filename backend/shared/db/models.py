import uuid
from datetime import datetime

from sqlalchemy import BIGINT, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    google_id = Column(String(255), unique=True, nullable=True)
    credits_balance = Column(Integer, nullable=False, default=240)
    plan = Column(String(50), nullable=False, default="starter")
    timezone = Column(String(100), default="UTC")
    created_at = Column(DateTime, default=datetime.utcnow)
    credits = Column(Integer, default=100, nullable=False)
    
    conversations = relationship("Conversation", backref="user", cascade="all, delete")
    documents = relationship("Document", backref="user", cascade="all, delete")
    credit_transactions = relationship("CreditTransaction", backref="user", cascade="all, delete")
    generated_files = relationship("GeneratedFile", backref="user", cascade="all, delete")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    agent_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("Message", backref="conversation", cascade="all, delete")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    agent_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    artifact = relationship("Artifact", backref="message", uselist=False, cascade="all, delete")
    generated_file = relationship("GeneratedFile", backref="message", uselist=False)

class Artifact(Base):
    __tablename__ = "artifacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False)
    type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    language = Column(String(50), nullable=True)

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    status = Column(String(50), nullable=False, default="processing")
    page_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    chunks = relationship("DocumentChunk", backref="document", cascade="all, delete")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    qdrant_vector_id = Column(String(100), nullable=False, unique=True)

class GeneratedFile(Base):
    __tablename__ = "generated_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=True)
    type = Column(String(20), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_size_bytes = Column(BIGINT, nullable=False)
    credits_used = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    agent_type = Column(String(50), nullable=True)
    balance_after = Column(Integer, nullable=False)
    description = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
