import React, { useState, useEffect } from 'react';

/**
 * Timer component - Hooks-based version (refactored)
 *
 * State:
 * - elapsed: number of seconds elapsed (useState)
 *
 * Lifecycle:
 * - useEffect (mount + unmount): starts interval on mount, clears on unmount
 */
function Timer() {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const intervalId = setInterval(() => {
      setElapsed((prevElapsed) => prevElapsed + 1);
    }, 1000);

    // Cleanup function runs on unmount (equivalent to componentWillUnmount)
    return () => {
      clearInterval(intervalId);
    };
  }, []); // Empty dependency array = run once on mount

  const reset = () => {
    setElapsed(0);
  };

  const minutes = Math.floor(elapsed / 60);
  const seconds = elapsed % 60;

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h2>Timer</h2>
      <div style={{ fontSize: '48px', marginBottom: '20px' }}>
        {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
      </div>
      <button onClick={reset} style={{ padding: '10px 20px', fontSize: '16px' }}>
        Reset
      </button>
    </div>
  );
}

export default Timer;
