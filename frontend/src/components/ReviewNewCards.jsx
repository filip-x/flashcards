import React, { useState, useEffect } from 'react';
import { listPendingFlashcards, acceptFlashcard, deleteFlashcard } from '../api';
import { CheckCircle2, XCircle, FileText, ChevronLeft } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const ReviewNewCards = ({ onFinish }) => {
  const [cards, setCards] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [acceptedCount, setAcceptedCount] = useState(0);
  const [discardedCount, setDiscardedCount] = useState(0);
  const [isActioning, setIsActioning] = useState(false);

  useEffect(() => {
    const fetchPending = async () => {
      try {
        const res = await listPendingFlashcards();
        setCards(res.flashcards || []);
      } catch (err) {
        console.error("Failed to fetch pending cards", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchPending();
  }, []);

  const handleFlip = () => setIsFlipped(f => !f);

  const handleAccept = async () => {
    if (isActioning) return;
    setIsActioning(true);
    try {
      await acceptFlashcard(cards[currentIndex].id);
      setAcceptedCount(c => c + 1);
      advance();
    } catch (err) {
      console.error("Failed to accept card", err);
    } finally {
      setIsActioning(false);
    }
  };

  const handleDiscard = async () => {
    if (isActioning) return;
    setIsActioning(true);
    try {
      await deleteFlashcard(cards[currentIndex].id);
      setDiscardedCount(c => c + 1);
      advance();
    } catch (err) {
      console.error("Failed to discard card", err);
    } finally {
      setIsActioning(false);
    }
  };

  const advance = () => {
    setIsFlipped(false);
    setTimeout(() => {
      setCurrentIndex(i => i + 1);
    }, 200);
  };

  // Keyboard shortcuts
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === ' ') { e.preventDefault(); handleFlip(); }
      if (e.key === 'ArrowRight' || e.key === 'a') handleAccept();
      if (e.key === 'ArrowLeft' || e.key === 'd') handleDiscard();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [currentIndex, isFlipped, isActioning]);

  if (isLoading) {
    return <div className="loader-container" style={{ marginTop: '100px' }}><div className="spinner"></div></div>;
  }

  // All cards reviewed
  if (currentIndex >= cards.length) {
    return (
      <div className="upload-container">
        <CheckCircle2 size={64} color="var(--accent-cyan)" style={{ marginBottom: '1rem' }} />
        <h1 className="upload-title text-gradient">Quality Control Complete</h1>
        <div style={{ display: 'flex', gap: '3rem', margin: '1.5rem 0' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: '800', fontFamily: 'Outfit', color: '#2ed573' }}>{acceptedCount}</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Accepted</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: '800', fontFamily: 'Outfit', color: '#ff4757' }}>{discardedCount}</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Discarded</div>
          </div>
        </div>
        <p className="text-secondary" style={{ maxWidth: '400px', textAlign: 'center' }}>
          {acceptedCount > 0
            ? `${acceptedCount} card${acceptedCount !== 1 ? 's' : ''} added to your collection.`
            : 'No cards were accepted this time.'}
        </p>
        <button className="btn btn-primary" onClick={onFinish} style={{ marginTop: '2rem' }}>
          Back to Dashboard
        </button>
      </div>
    );
  }

  // No pending cards at all
  if (cards.length === 0) {
    return (
      <div className="upload-container">
        <CheckCircle2 size={48} color="var(--text-secondary)" style={{ marginBottom: '1rem', opacity: 0.5 }} />
        <h2 style={{ fontFamily: 'Outfit', marginBottom: '0.5rem' }}>No Pending Cards</h2>
        <p className="text-secondary">Generate flashcards from a document first, then come back to review them.</p>
        <button className="btn btn-secondary" onClick={onFinish} style={{ marginTop: '2rem' }}>
          Back to Dashboard
        </button>
      </div>
    );
  }

  const currentCard = cards[currentIndex];
  const progressPercent = ((currentIndex) / cards.length) * 100;

  return (
    <div style={{ animation: 'fadeIn 0.3s ease' }}>
      {/* Top bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <button className="btn btn-secondary" onClick={onFinish} style={{ gap: '0.4rem', padding: '0.5rem 1rem', fontSize: '0.9rem' }}>
          <ChevronLeft size={16} /> Dashboard
        </button>
        <div style={{ textAlign: 'center' }}>
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Quality Control — Card {currentIndex + 1} of {cards.length}
          </span>
        </div>
        <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem' }}>
          <span style={{ color: '#2ed573' }}>✓ {acceptedCount}</span>
          <span style={{ color: '#ff4757' }}>✕ {discardedCount}</span>
        </div>
      </div>

      {/* Source file */}
      {currentCard.document_filename && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '1rem',
          padding: '0.4rem 0.8rem', background: 'rgba(112, 0, 255, 0.1)',
          borderRadius: 'var(--radius-sm)', width: 'fit-content', fontSize: '0.8rem', color: 'var(--accent-cyan)',
        }}>
          <FileText size={13} />
          {currentCard.document_filename}
        </div>
      )}

      {/* Progress bar */}
      <div style={{ width: '100%', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginBottom: '2.5rem' }}>
        <div style={{ width: `${progressPercent}%`, height: '100%', background: 'var(--accent-gradient)', borderRadius: '2px', transition: 'width 0.3s ease' }} />
      </div>

      {/* Card */}
      <div className="review-container" style={{ maxWidth: '800px', margin: '0 auto' }}>
        <div className="scene" onClick={handleFlip} style={{ height: isFlipped ? 'auto' : '340px', minHeight: '220px' }}>
          <div className={`flashcard ${isFlipped ? 'is-flipped' : ''}`} style={{ height: isFlipped ? 'auto' : '340px', minHeight: '220px' }}>

            {/* Front */}
            <div className="card-face card-front glass-panel" style={{ padding: '3rem', minHeight: '220px' }}>
              <div className="card-content" style={{ fontSize: '1.4rem', lineHeight: '1.5' }}>
                {currentCard.question}
              </div>
              {!isFlipped && (
                <div className="card-hint">Click to reveal answer · Space to flip</div>
              )}
            </div>

            {/* Back */}
            <div className="card-face card-back glass-panel" style={{
              transform: 'rotateX(180deg)',
              padding: '2.5rem',
              overflowY: 'auto',
              maxHeight: '70vh',
              alignItems: 'flex-start',
              textAlign: 'left',
            }}>
              <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--accent-cyan)', marginBottom: '1rem', fontWeight: '600' }}>
                Answer
              </div>
              <div className="markdown-content" style={{ color: 'var(--text-primary)', lineHeight: '1.7', fontSize: '1.05rem', fontFamily: 'inherit' }}>
                <ReactMarkdown>{currentCard.answer}</ReactMarkdown>
              </div>
            </div>

          </div>
        </div>

        {/* Accept / Discard actions */}
        <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem', justifyContent: 'center' }}>
          <button
            className="btn"
            onClick={handleDiscard}
            disabled={isActioning}
            style={{
              background: 'rgba(255, 71, 87, 0.1)',
              border: '1px solid rgba(255, 71, 87, 0.3)',
              color: '#ff4757',
              gap: '0.5rem',
              minWidth: '160px',
              fontSize: '1rem',
              padding: '0.85rem 1.5rem',
            }}
          >
            <XCircle size={18} /> Discard
          </button>
          <button
            className="btn btn-secondary"
            onClick={handleFlip}
            style={{ minWidth: '120px' }}
          >
            {isFlipped ? 'Hide Answer' : 'Show Answer'}
          </button>
          <button
            className="btn"
            onClick={handleAccept}
            disabled={isActioning}
            style={{
              background: 'rgba(46, 213, 115, 0.1)',
              border: '1px solid rgba(46, 213, 115, 0.3)',
              color: '#2ed573',
              gap: '0.5rem',
              minWidth: '160px',
              fontSize: '1rem',
              padding: '0.85rem 1.5rem',
            }}
          >
            <CheckCircle2 size={18} /> Accept
          </button>
        </div>

        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '1rem', opacity: 0.6 }}>
          Keyboard: A = accept · D = discard · Space = flip
        </p>
      </div>
    </div>
  );
};

export default ReviewNewCards;
