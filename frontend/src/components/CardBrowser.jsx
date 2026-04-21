import React, { useState } from 'react';
import { ArrowLeft, ArrowRight, ChevronLeft, Trash2, FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { deleteFlashcard } from '../api';

const CardBrowser = ({ cards: initialCards, startIndex = 0, onClose, onCardDeleted }) => {
  const [cards, setCards] = useState(initialCards);
  const [currentIndex, setCurrentIndex] = useState(startIndex);
  const [isFlipped, setIsFlipped] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // If all cards have been deleted, go back
  if (cards.length === 0) {
    onClose();
    return null;
  }

  // Clamp the index if we deleted the last card
  const safeIndex = Math.min(currentIndex, cards.length - 1);
  if (safeIndex !== currentIndex) {
    setCurrentIndex(safeIndex);
  }

  const currentCard = cards[safeIndex];
  const progressPercent = ((safeIndex + 1) / cards.length) * 100;

  const goNext = () => {
    if (safeIndex < cards.length - 1) {
      setIsFlipped(false);
      setShowDeleteConfirm(false);
      setTimeout(() => setCurrentIndex(i => i + 1), 200);
    }
  };

  const goPrev = () => {
    if (safeIndex > 0) {
      setIsFlipped(false);
      setShowDeleteConfirm(false);
      setTimeout(() => setCurrentIndex(i => i - 1), 200);
    }
  };

  const handleFlip = () => {
    if (!showDeleteConfirm) {
      setIsFlipped(f => !f);
    }
  };

  const handleDelete = async () => {
    if (!showDeleteConfirm) {
      setShowDeleteConfirm(true);
      return;
    }

    setIsDeleting(true);
    try {
      await deleteFlashcard(currentCard.id);
      const newCards = cards.filter(c => c.id !== currentCard.id);
      setCards(newCards);
      setIsFlipped(false);
      setShowDeleteConfirm(false);
      if (onCardDeleted) onCardDeleted(currentCard.id);
      // Index will be clamped on next render
    } catch (err) {
      console.error('Failed to delete flashcard', err);
    } finally {
      setIsDeleting(false);
    }
  };

  // Keyboard navigation
  React.useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'ArrowRight') goNext();
      if (e.key === 'ArrowLeft') goPrev();
      if (e.key === ' ') { e.preventDefault(); handleFlip(); }
      if (e.key === 'Escape') {
        if (showDeleteConfirm) {
          setShowDeleteConfirm(false);
        } else {
          onClose();
        }
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [currentIndex, isFlipped, showDeleteConfirm]);

  return (
    <div style={{ animation: 'fadeIn 0.3s ease' }}>
      {/* Top bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
        <button
          className="btn btn-secondary"
          onClick={onClose}
          style={{ gap: '0.4rem', padding: '0.5rem 1rem', fontSize: '0.9rem' }}
        >
          <ChevronLeft size={16} /> Library
        </button>
        <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Card {safeIndex + 1} of {cards.length}
        </span>
        {/* Delete button */}
        <button
          className="btn btn-secondary"
          onClick={handleDelete}
          disabled={isDeleting}
          style={{
            gap: '0.4rem',
            padding: '0.5rem 1rem',
            fontSize: '0.9rem',
            color: showDeleteConfirm ? '#ff4757' : 'var(--text-secondary)',
            borderColor: showDeleteConfirm ? 'rgba(255, 71, 87, 0.4)' : undefined,
          }}
        >
          <Trash2 size={14} />
          {isDeleting ? 'Deleting...' : showDeleteConfirm ? 'Confirm Delete' : 'Delete'}
        </button>
      </div>

      {/* Source file badge */}
      {currentCard.document_filename && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem',
          marginBottom: '1rem',
          padding: '0.4rem 0.8rem',
          background: 'rgba(112, 0, 255, 0.1)',
          borderRadius: 'var(--radius-sm)',
          width: 'fit-content',
          fontSize: '0.8rem',
          color: 'var(--accent-cyan)',
        }}>
          <FileText size={13} />
          {currentCard.document_filename}
        </div>
      )}

      {/* Delete confirmation banner */}
      {showDeleteConfirm && (
        <div style={{
          padding: '0.75rem 1rem',
          background: 'rgba(255, 71, 87, 0.1)',
          border: '1px solid rgba(255, 71, 87, 0.3)',
          borderRadius: 'var(--radius-sm)',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.9rem',
        }}>
          <span style={{ color: '#ff4757' }}>Are you sure you want to delete this card?</span>
          <button
            className="btn btn-secondary"
            onClick={() => setShowDeleteConfirm(false)}
            style={{ padding: '0.3rem 0.8rem', fontSize: '0.8rem' }}
          >
            Cancel
          </button>
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
                <div className="card-hint">Click to reveal answer · Space · ←→ to navigate</div>
              )}
            </div>

            {/* Back — scrollable for longer answers */}
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
              <div className="card-hint" style={{ position: 'static', marginTop: '1.5rem', opacity: 0.5 }}>
                Click to flip back
              </div>
            </div>

          </div>
        </div>

        {/* Navigation */}
        <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem', justifyContent: 'center' }}>
          <button
            className="btn btn-secondary"
            onClick={goPrev}
            disabled={safeIndex === 0}
            style={{ gap: '0.5rem' }}
          >
            <ArrowLeft size={16} /> Previous
          </button>
          <button
            className="btn btn-secondary"
            onClick={handleFlip}
            style={{ minWidth: '120px' }}
          >
            {isFlipped ? 'Hide Answer' : 'Show Answer'}
          </button>
          <button
            className="btn btn-secondary"
            onClick={goNext}
            disabled={safeIndex === cards.length - 1}
            style={{ gap: '0.5rem' }}
          >
            Next <ArrowRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default CardBrowser;
