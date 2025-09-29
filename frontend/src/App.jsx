import React, { useState } from 'react';
import axios from 'axios';

export default function App() {
  const [url, setUrl] = useState('');
  const [results, setResults] = useState(null);

  const runTests = async () => {
    const res = await axios.post('http://localhost:5000/run-tests', { url });
    setResults(res.data);
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>AI QA Website Testing Tool</h1>
      <input value={url} onChange={e => setUrl(e.target.value)} placeholder="Enter website URL" style={{ width: '300px' }} />
      <button onClick={runTests} style={{ marginLeft: '1rem' }}>Run Tests</button>

      {results && <pre style={{ marginTop: '2rem', background: '#f0f0f0', padding: '1rem' }}>{JSON.stringify(results, null, 2)}</pre>}
    </div>
  );
}
