import React, { useState, useEffect } from 'react';
import NovelSelectDropDown from '../components/NovelSelectDropDown';

export default function RecommendPage() {
  const [selectedNovel, setSelectedNovel] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  async function handleSelect(novel) {
    setSelectedNovel(novel);
    const res = await fetch(`http://3.36.221.36:8000/api/recommendations/?novelId=${novel.value}`);
    const data = await res.json();
    setRecommendations(data);
  }

  return (
    <div>
      <h1>Find Similar Novels</h1>
      <NovelSelectDropDown onSelect={handleSelect} />

      {selectedNovel && (
        <div>
          <h2>Recommendations for "{selectedNovel.label}"</h2>
          <div>
            {recommendations.map(recommendation => (
              <div key={recommendation.novel.id}>
                <h1>{recommendation.novel.title}</h1>
                <h3>{recommendation.similarity}</h3>
                <p>{recommendation.novel.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
