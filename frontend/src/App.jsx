import React, { useState } from 'react';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import UploadSection from './components/UploadSection';
import ReviewSession from './components/ReviewSession';
import ReviewNewCards from './components/ReviewNewCards';
import CardBrowser from './components/CardBrowser';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [browseCards, setBrowseCards] = useState([]);
  const [browseStartIndex, setBrowseStartIndex] = useState(0);

  const handleGenerationSuccess = (count) => {
    setTimeout(() => {
      setCurrentView('dashboard');
    }, 1500);
  };

  const handleStartReview = () => {
    setCurrentView('review');
  };

  const handleReviewNew = () => {
    setCurrentView('review-new');
  };

  const handleFinishReview = () => {
    setCurrentView('dashboard');
  };

  const handleBrowseCard = (cards, index) => {
    setBrowseCards(cards);
    setBrowseStartIndex(index);
    setCurrentView('browse');
  };

  const handleCloseBrowse = () => {
    setCurrentView('dashboard');
  };

  return (
    <Layout currentView={currentView} setView={setCurrentView}>
      {currentView === 'dashboard' && (
        <Dashboard 
          onStartReview={handleStartReview} 
          onReviewNew={handleReviewNew}
          onBrowseCard={handleBrowseCard} 
        />
      )}
      {currentView === 'upload' && <UploadSection onGenerationSuccess={handleGenerationSuccess} />}
      {currentView === 'review' && <ReviewSession onFinish={handleFinishReview} />}
      {currentView === 'review-new' && <ReviewNewCards onFinish={handleFinishReview} />}
      {currentView === 'browse' && <CardBrowser cards={browseCards} startIndex={browseStartIndex} onClose={handleCloseBrowse} />}
    </Layout>
  );
}

export default App;
