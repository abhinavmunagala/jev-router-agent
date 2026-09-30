import React from 'react';

/**
 * Timer component - Class-based version
 *
 * State:
 * - elapsed: number of seconds elapsed
 *
 * Lifecycle:
 * - componentDidMount: starts the interval
 * - componentWillUnmount: clears the interval
 */
class Timer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      elapsed: 0,
    };
  }

  componentDidMount() {
    this.intervalId = setInterval(() => {
      this.setState((prevState) => ({
        elapsed: prevState.elapsed + 1,
      }));
    }, 1000);
  }

  componentWillUnmount() {
    clearInterval(this.intervalId);
  }

  reset = () => {
    this.setState({ elapsed: 0 });
  };

  render() {
    const { elapsed } = this.state;
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;

    return (
      <div style={{ padding: '20px', fontFamily: 'monospace' }}>
        <h2>Timer</h2>
        <div style={{ fontSize: '48px', marginBottom: '20px' }}>
          {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
        </div>
        <button onClick={this.reset} style={{ padding: '10px 20px', fontSize: '16px' }}>
          Reset
        </button>
      </div>
    );
  }
}

export default Timer;
