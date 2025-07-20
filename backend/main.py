from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    create_engine,
    Enum,
    DateTime,
    func,
    case,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from passlib.context import CryptContext
from datetime import datetime
import enum
import json
import os
import redis.asyncio as redis


class MemoryCache:
    """Simple in-memory cache as a fallback when Redis is unavailable."""

    def __init__(self):
        self.store = {}

    async def get(self, key):
        return self.store.get(key)

    async def set(self, key, value, ex=None):
        self.store[key] = value

    async def delete(self, key):
        self.store.pop(key, None)

    async def ping(self):
        return True
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ORIGINS", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")
# For AWS deployment, use PostgreSQL
if DATABASE_URL.startswith("postgresql"):
    connect_args = {}
else:
    connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

class MasteryLevel(enum.IntEnum):
    unknown = 0
    learning = 1
    mastered = 2

class Word(Base):
    __tablename__ = 'words'
    id = Column(Integer, primary_key=True)
    text = Column(String, unique=True, nullable=False)

class UserWord(Base):
    __tablename__ = 'user_words'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True, nullable=False)
    word_id = Column(Integer, ForeignKey('words.id'), index=True, nullable=False)
    seen_count = Column(Integer, default=0, nullable=False)
    last_seen_at = Column(DateTime)
    mastery_level = Column(Enum(MasteryLevel), default=MasteryLevel.unknown, nullable=False)

class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=False)
    score = Column(Integer, default=0, nullable=False)

class VideoWord(Base):
    __tablename__ = 'video_words'
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, index=True, nullable=False)
    word_id = Column(Integer, ForeignKey('words.id'), index=True, nullable=False)

class VideoTranscript(Base):
    __tablename__ = 'video_transcripts'
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, index=True, nullable=False)
    text = Column(String, nullable=False)
    start_sec = Column(Integer, nullable=False)
    end_sec = Column(Integer, nullable=False)

class TranscriptToken(Base):
    __tablename__ = 'transcript_tokens'
    id = Column(Integer, primary_key=True)
    video_id = Column(Integer, index=True, nullable=False)
    word_id = Column(Integer, ForeignKey('words.id'), index=True, nullable=False)
    start_sec = Column(Integer, nullable=False)
    end_sec = Column(Integer, nullable=False)

Base.metadata.create_all(bind=engine)

# Insert a minimal set of sample data if the database is empty
def seed_data():
    with SessionLocal() as db:
        if not db.query(Video).first():
            sample = Video(
                id=1,
                title="Sample Video",
                thumbnail_url="https://example.com/thumb.jpg",
                score=1,
            )
            db.add(sample)
            transcripts = [
                VideoTranscript(video_id=1, text="Hello world", start_sec=0, end_sec=2),
                VideoTranscript(video_id=1, text="Learning is fun", start_sec=2, end_sec=5),
            ]
            db.add_all(transcripts)
            words = {}
            tokens = []
            for t in transcripts:
                parts = t.text.split()
                span = (t.end_sec - t.start_sec) / max(len(parts), 1)
                for i, tok in enumerate(parts):
                    token = tok.lower()
                    if token not in words:
                        w = Word(text=token)
                        db.add(w)
                        db.flush()
                        words[token] = w.id
                    tokens.append(
                        TranscriptToken(
                            video_id=1,
                            word_id=words[token],
                            start_sec=int(t.start_sec + i * span),
                            end_sec=int(t.start_sec + (i + 1) * span),
                        )
                    )
            db.add_all(
                [VideoWord(video_id=1, word_id=w_id) for w_id in words.values()]
            )
            db.add_all(tokens)
            db.commit()

if os.getenv("SEED_DATA") == "true":
    seed_data()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_redis():
    if not hasattr(app.state, "redis"):
        redis_url = os.getenv("REDIS_URL", "redis://localhost")
        try:
            app.state.redis = redis.from_url(redis_url)
            await app.state.redis.ping()
        except Exception:
            app.state.redis = MemoryCache()
    return app.state.redis

def record_word_interaction(db, user_id: int, word_id: int, correct: bool = False):
    word = db.query(UserWord).filter_by(user_id=user_id, word_id=word_id).first()
    if not word:
        word = UserWord(user_id=user_id, word_id=word_id, seen_count=0,
                        mastery_level=MasteryLevel.unknown)
        db.add(word)
    word.seen_count += 1
    word.last_seen_at = datetime.utcnow()
    if correct:
        new_level = min(word.mastery_level.value + 1, MasteryLevel.mastered.value)
    else:
        new_level = max(word.mastery_level.value - 1, MasteryLevel.unknown.value)
    word.mastery_level = MasteryLevel(new_level)
    db.commit()
    return word

def get_mastered_words(db, user_id: int):
    return (
        db.query(UserWord, Word.text)
        .join(Word, UserWord.word_id == Word.id)
        .filter(
            UserWord.user_id == user_id,
            UserWord.mastery_level >= MasteryLevel.learning,
        )
        .all()
    )

class Credentials(BaseModel):
    username: str
    password: str

class QuizAnswer(BaseModel):
    word_id: int
    correct: bool

class SignupRequest(Credentials):
    quiz_answers: Optional[List[QuizAnswer]] = None

class QuizSubmission(BaseModel):
    user_id: int
    answers: List[QuizAnswer]

class UserWordUpdate(BaseModel):
    user_id: int
    mastery_level: MasteryLevel

@app.get('/health')
def health_check():
    return {"status": "ok"}

@app.post('/signup')
def signup(creds: SignupRequest):
    with SessionLocal() as db:
        if db.query(User).filter(User.username == creds.username).first():
            raise HTTPException(status_code=400, detail="User already exists")
        hashed = pwd_context.hash(creds.password)
        user = User(username=creds.username, password_hash=hashed)
        db.add(user)
        db.commit()
        db.refresh(user)
        if creds.quiz_answers:
            for ans in creds.quiz_answers:
                record_word_interaction(db, user.id, ans.word_id, ans.correct)
    return {"status": "created"}

@app.post('/login')
def login(creds: Credentials):
    with SessionLocal() as db:
        user = db.query(User).filter(User.username == creds.username).first()
        if not user or not pwd_context.verify(creds.password, user.password_hash):
            raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"status": "ok", "user_id": user.id}

@app.get('/api/user/words')
async def user_words(user_id: int):
    r = await get_redis()
    cache_key = f"user_words:{user_id}"
    cached = await r.get(cache_key)
    if cached:
        return json.loads(cached)
    with SessionLocal() as db:
        rows = get_mastered_words(db, user_id)
        result = [
            {
                "word_id": uw.word_id,
                "text": text,
                "mastery_level": uw.mastery_level.name,
                "seen_count": uw.seen_count,
                "last_seen_at": uw.last_seen_at.isoformat() if uw.last_seen_at else None,
            }
            for uw, text in rows
        ]
    await r.set(cache_key, json.dumps(result), ex=3600)
    return result


@app.patch('/api/user/words/{word_id}')
async def update_user_word(word_id: int, upd: UserWordUpdate):
    with SessionLocal() as db:
        entry = (
            db.query(UserWord)
            .filter_by(user_id=upd.user_id, word_id=word_id)
            .first()
        )
        if not entry:
            entry = UserWord(
                user_id=upd.user_id,
                word_id=word_id,
                seen_count=0,
                mastery_level=upd.mastery_level,
            )
            db.add(entry)
        else:
            entry.mastery_level = upd.mastery_level
        db.commit()
        text = db.query(Word.text).filter(Word.id == word_id).scalar()
        result = {
            "word_id": entry.word_id,
            "text": text,
            "mastery_level": entry.mastery_level.name,
            "seen_count": entry.seen_count,
            "last_seen_at": entry.last_seen_at.isoformat()
            if entry.last_seen_at
            else None,
        }

    r = await get_redis()
    await r.delete(f"user_words:{upd.user_id}")
    return result


@app.post('/api/user/quiz')
def submit_quiz(sub: QuizSubmission):
    with SessionLocal() as db:
        user = db.get(User, sub.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        for ans in sub.answers:
            record_word_interaction(db, sub.user_id, ans.word_id, ans.correct)
    return {"status": "recorded"}


@app.get('/api/videos/recommendations')
def video_recommendations(user_id: int, limit: int = 20):
    with SessionLocal() as db:
        subq = (
            db.query(
                VideoWord.video_id.label("vid"),
                func.sum(
                    case(
                        (
                            (UserWord.id.is_(None))
                            | (UserWord.mastery_level == MasteryLevel.unknown),
                            1,
                        ),
                        else_=0,
                    )
                ).label("unknown_count"),
            )
            .join(Word, VideoWord.word_id == Word.id)
            .outerjoin(
                UserWord,
                (VideoWord.word_id == UserWord.word_id)
                & (UserWord.user_id == user_id),
            )
            .group_by(VideoWord.video_id)
            .subquery()
        )

        videos = (
            db.query(
                Video.id,
                Video.title,
                Video.thumbnail_url,
                Video.score,
                subq.c.unknown_count,
            )
            .join(subq, Video.id == subq.c.vid)
            .filter(subq.c.unknown_count <= 1)
            .order_by(Video.score.desc())
            .limit(limit)
            .all()
        )

    return [
        {
            "id": v.id,
            "title": v.title,
            "thumbnail_url": v.thumbnail_url,
            "new_word_count": int(v.unknown_count or 0),
        }
        for v in videos
    ]


@app.get('/api/videos/{video_id}/transcript')
def video_transcript(video_id: int):
    with SessionLocal() as db:
        rows = (db.query(VideoTranscript)
                .filter(VideoTranscript.video_id == video_id)
                .order_by(VideoTranscript.start_sec)
                .all())
        if not rows:
            raise HTTPException(status_code=404, detail="Transcript not found")
        return [
            {
                "text": r.text,
                "start_sec": r.start_sec,
                "end_sec": r.end_sec,
            }
            for r in rows
        ]


@app.get('/api/videos/{video_id}/tokens')
def video_tokens(video_id: int):
    with SessionLocal() as db:
        rows = (
            db.query(TranscriptToken, Word.text)
            .join(Word, TranscriptToken.word_id == Word.id)
            .filter(TranscriptToken.video_id == video_id)
            .order_by(TranscriptToken.start_sec)
            .all()
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Tokens not found")
        return [
            {
                "word_id": t.word_id,
                "text": text,
                "start_sec": t.start_sec,
                "end_sec": t.end_sec,
            }
            for t, text in rows
        ]
