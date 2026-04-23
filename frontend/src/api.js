const API_BASE = `http://${window.location.hostname}:8000/api/v1`;

/**
 * Handles all backend interaction.
 */

// 1. Upload Document
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });
  
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Failed to upload document');
  }
  return res.json();
};

// 2. Generate Flashcards
export const generateFlashcards = async (documentId, numCards = null) => {
  const payload = { document_id: documentId };
  if (numCards) payload.num_cards = numCards;

  const res = await fetch(`${API_BASE}/flashcards/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (res.status === 429) {
    throw new Error('AI Rate Limit Reached: The AI is currently under heavy load. Please wait about a minute and try again.');
  }

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Failed to generate flashcards');
  }
  return res.json();
};

// 3. List Flashcards (Adaptive Priority Sorted)
export const listFlashcards = async (limit = 100) => {
  const url = new URL(`${API_BASE}/flashcards/`, window.location.origin);
  url.searchParams.append('limit', limit);
  
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch flashcards');
  return res.json();
};

// 4. Submit Review (SM-2)
export const submitReview = async (flashcardId, quality) => {
  const res = await fetch(`${API_BASE}/reviews/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      flashcard_id: flashcardId,
      quality: quality
    }),
  });

  if (!res.ok) throw new Error('Failed to submit review');
  return res.json();
};

// 5. Delete Flashcard
export const deleteFlashcard = async (flashcardId) => {
  const res = await fetch(`${API_BASE}/flashcards/${flashcardId}`, {
    method: 'DELETE',
  });

  if (!res.ok) throw new Error('Failed to delete flashcard');
  return true;
};

// 6. List Pending Flashcards (quality control queue)
export const listPendingFlashcards = async () => {
  const url = new URL(`${API_BASE}/flashcards/`, window.location.origin);
  url.searchParams.append('card_status', 'pending');

  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch pending flashcards');
  return res.json();
};

// 7. Accept a Flashcard (move from pending to collection)
export const acceptFlashcard = async (flashcardId) => {
  const res = await fetch(`${API_BASE}/flashcards/${flashcardId}/accept`, {
    method: 'PATCH',
  });

  if (!res.ok) throw new Error('Failed to accept flashcard');
  return res.json();
};
