import React, { useState, useEffect } from 'react';
import './App.css';


// The main component of our application
function App() {
  // `useState` is a React Hook that lets you add a state variable to your component.
  // `messages` will hold the array of messages fetched from the backend.
  // `setMessages` is the function we use to update the `messages` state.
  const [messages, setMessages] = useState([]);

  // `newMessage` will hold the value of the text input field.
  // `setNewMessage` is the function we use to update the `newMessage` state.
  const [newMessage, setNewMessage] = useState('');

  // `useEffect` is a React Hook that lets you synchronize a component with an external system.
  // In this case, we use it to fetch data from our Django backend when the component first loads.
  // The empty array `[]` as the second argument means this effect will only run once, after the initial render.
  useEffect(() => {
    fetch('http://localhost:8000/api/messages/')
      .then(response => response.json())
      .then(data => setMessages(data));
  }, []);

  // This function is called when the form is submitted.
  const handleSubmit = (e) => {
    // `e.preventDefault()` stops the browser from reloading the page, which is the default behavior for form submissions.
    e.preventDefault();

    // We send a POST request to our backend to create a new message.
    fetch('http://localhost:8000/api/messages/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      // We send the new message in the request body, formatted as JSON.
      body: JSON.stringify({ body: newMessage })
    })
    .then(response => response.json())
    .then(data => {
      // After the new message is created, the backend sends it back to us.
      // We add the new message to our `messages` state array.
      // The `...messages` syntax is called the spread operator. It creates a new array with all the existing messages, plus the new one.
      setMessages([...messages, data]);
      // We clear the input field by resetting the `newMessage` state.
      setNewMessage('');
    });
  };

  // This is the JSX that defines the structure of our component. It looks like HTML, but it's actually JavaScript.
  return (
    <div className="App">
      <header className="App-header">
        <h1>Decoupled Django React App</h1>
      </header>
      <div className="App-content">
        <h2>Messages</h2>
        <ul>
          {/* We use the `map` function to loop over the `messages` array and create a list item for each message. */}
          {/* The `key` attribute is important for React to keep track of each item in the list. */}
          {messages.map(message => (
            <li key={message.id}>{message.body}</li>
          ))}
        </ul>
        {/* When this form is submitted, it will call the `handleSubmit` function. */}
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            // The `value` of the input is tied to the `newMessage` state.
            value={newMessage}
            // `onChange` is called every time the user types in the input field.
            // We update the `newMessage` state with the new value.
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Enter a new message"
          />
          <button type="submit">Send</button>
        </form>
      </div>
    </div>
  );
}

// We export the `App` component so it can be used in other parts of our application (specifically, `src/index.js`).
export default App;
